# Copyright (c) 2026 Salvatore Mazzaglia
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Sanitized JSON execution metadata callback for ansible-infrastructure-automation-lab.

Compatible with ansible-core 2.20+ / 2.21+ callback APIs (CallbackTaskResult
host/task/result properties) and older TaskResult (_host/_task/_result).
"""

from __future__ import annotations

DOCUMENTATION = r"""
name: automation_report
type: aggregate
short_description: Write sanitized JSON automation execution reports
version_added: "1.0.0"
description:
  - Emits sanitized JSON execution metadata under a configurable reports directory.
  - Captures play, host alias, task, role, status, changed, failed, skipped,
    duration, and aggregate recap.
  - Never records raw secrets, vault values, passwords, SSH keys, become
    passwords, or no_log task result payloads.
  - When a task uses no_log, only REDACTED is recorded; Ansible no_log is never overridden.
options:
  report_dir:
    description:
      - Directory where JSON reports are written.
      - Relative paths are resolved from the current working directory.
    type: path
    default: reports
    env:
      - name: AIAL_REPORT_DIR
    ini:
      - section: callback_automation_report
        key: report_dir
  report_prefix:
    description: Filename prefix for generated report JSON files.
    type: str
    default: automation-report
    env:
      - name: AIAL_REPORT_PREFIX
    ini:
      - section: callback_automation_report
        key: report_prefix
requirements:
  - enable the callback in ansible.cfg (callbacks_enabled)
"""

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ansible.plugins.callback import CallbackBase

REDACTED = "REDACTED"

# Keys / substrings that must never appear as raw values in reports.
_SENSITIVE_KEY_RE = re.compile(
    r"(password|passwd|passphrase|secret|token|api[_-]?key|private[_-]?key|"
    r"ssh[_-]?key|become_pass|ansible_ssh_pass|vault|credential|auth)",
    re.IGNORECASE,
)

_SENSITIVE_VALUE_HINTS = (
    "BEGIN OPENSSH PRIVATE KEY",
    "BEGIN RSA PRIVATE KEY",
    "BEGIN PRIVATE KEY",
    "ANSIBLE_VAULT",
)


class CallbackModule(CallbackBase):
    """Aggregate callback that writes sanitized automation reports."""

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "aggregate"
    CALLBACK_NAME = "automation_report"
    CALLBACK_NEEDS_ENABLED = True

    def __init__(self) -> None:
        super().__init__()
        self._play_name: str | None = None
        self._playbook: str | None = None
        self._started_at: str = _utc_now()
        self._run_start: float = time.monotonic()
        self._task_starts: dict[tuple[str, str], float] = {}
        self._records: list[dict[str, Any]] = []
        self._check_mode: bool = False

    # ------------------------------------------------------------------ options
    def _report_dir(self) -> Path:
        raw: str | None = None
        try:
            raw = self.get_option("report_dir")
        except (KeyError, AttributeError, TypeError, ValueError):
            raw = None
        if not raw:
            raw = os.environ.get("AIAL_REPORT_DIR") or "reports"
        path = Path(str(raw)).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        return path

    def _report_prefix(self) -> str:
        try:
            prefix = self.get_option("report_prefix")
        except (KeyError, AttributeError, TypeError, ValueError):
            prefix = None
        return str(prefix or os.environ.get("AIAL_REPORT_PREFIX") or "automation-report")

    # --------------------------------------------------------------- result API
    @staticmethod
    def _host_obj(result: Any) -> Any:
        return getattr(result, "host", None) or getattr(result, "_host", None)

    @staticmethod
    def _task_obj(result: Any) -> Any:
        return getattr(result, "task", None) or getattr(result, "_task", None)

    @staticmethod
    def _result_mapping(result: Any) -> dict[str, Any]:
        mapping = getattr(result, "result", None)
        if mapping is None or not hasattr(mapping, "get"):
            mapping = getattr(result, "_result", None)
        if isinstance(mapping, dict):
            return mapping
        if mapping is not None and hasattr(mapping, "items"):
            try:
                return dict(mapping)
            except (TypeError, ValueError):
                return {}
        return {}

    @staticmethod
    def _host_alias(result: Any) -> str:
        host = CallbackModule._host_obj(result)
        if host is None:
            return "unknown"
        name = getattr(host, "get_name", None)
        if callable(name):
            return str(name())
        return str(getattr(host, "name", host))

    @staticmethod
    def _task_name(task: Any) -> str:
        if task is None:
            return "unknown"
        getter = getattr(task, "get_name", None)
        if callable(getter):
            return str(getter())
        return str(getattr(task, "name", None) or getattr(task, "action", "unknown"))

    @staticmethod
    def _role_name(task: Any) -> str | None:
        if task is None:
            return None
        role = getattr(task, "_role", None)
        if role is None:
            return None
        getter = getattr(role, "get_name", None)
        if callable(getter):
            return str(getter())
        return str(getattr(role, "_role_name", None) or role)

    @staticmethod
    def _task_uuid(task: Any) -> str:
        if task is None:
            return ""
        return str(getattr(task, "_uuid", "") or "")

    @staticmethod
    def _is_no_log(task: Any, result_dict: dict[str, Any]) -> bool:
        task_flag = bool(getattr(task, "no_log", False)) if task is not None else False
        result_flag = bool(result_dict.get("_ansible_no_log", False))
        return task_flag or result_flag

    @staticmethod
    def _status_flags(result: Any, result_dict: dict[str, Any]) -> dict[str, bool]:
        def _call(method: str, key: str) -> bool:
            fn = getattr(result, method, None)
            if callable(fn):
                try:
                    return bool(fn())
                except Exception:  # noqa: BLE001 - defensive against API drift
                    pass
            return bool(result_dict.get(key, False))

        return {
            "changed": _call("is_changed", "changed"),
            "failed": _call("is_failed", "failed"),
            "skipped": _call("is_skipped", "skipped"),
            "unreachable": _call("is_unreachable", "unreachable"),
        }

    @classmethod
    def _sanitize_value(cls, key: str, value: Any) -> Any:
        if _SENSITIVE_KEY_RE.search(str(key)):
            return REDACTED
        if isinstance(value, str):
            upper = value.upper()
            for hint in _SENSITIVE_VALUE_HINTS:
                if hint in upper:
                    return REDACTED
            return value
        if isinstance(value, dict):
            return {str(k): cls._sanitize_value(str(k), v) for k, v in value.items()}
        if isinstance(value, list):
            return [cls._sanitize_value(key, item) for item in value]
        return value

    def _record(
        self,
        result: Any,
        *,
        status: str,
    ) -> None:
        task = self._task_obj(result)
        result_dict = self._result_mapping(result)
        flags = self._status_flags(result, result_dict)
        host_alias = self._host_alias(result)
        uuid = self._task_uuid(task)
        start = self._task_starts.pop((uuid, host_alias), None)
        duration = round(time.monotonic() - start, 4) if start is not None else None

        no_log = self._is_no_log(task, result_dict)
        entry: dict[str, Any] = {
            "play": self._play_name,
            "host": host_alias,
            "task": self._task_name(task),
            "role": self._role_name(task),
            "status": status,
            "changed": flags["changed"],
            "failed": flags["failed"] or status == "failed",
            "skipped": flags["skipped"] or status == "skipped",
            "unreachable": flags["unreachable"] or status == "unreachable",
            "duration_seconds": duration,
            "no_log": no_log,
            "check_mode": bool(
                getattr(task, "check_mode", False) if task is not None else self._check_mode
            ),
            "result": REDACTED if no_log else None,
        }
        # Never attach raw module result payloads — metadata only.
        # Sensitive keys are still scrubbed if future fields are added.
        self._records.append(self._sanitize_value("record", entry))

    # ----------------------------------------------------------------- lifecycle
    def v2_playbook_on_start(self, playbook: Any) -> None:
        self._playbook = str(getattr(playbook, "_file_name", None) or playbook)
        self._started_at = _utc_now()
        self._run_start = time.monotonic()
        self._records = []

    def v2_playbook_on_play_start(self, play: Any) -> None:
        self._play_name = str(getattr(play, "get_name", lambda: play)())
        try:
            self._check_mode = bool(getattr(play, "check_mode", False))
        except Exception:  # noqa: BLE001
            self._check_mode = False

    def v2_playbook_on_task_start(self, task: Any, is_handler: bool) -> None:
        # Duration is measured per host via v2_runner_on_start when available.
        _ = is_handler
        uuid = self._task_uuid(task)
        if uuid:
            # Placeholder start for hosts that never emit runner_on_start.
            self._task_starts.setdefault((uuid, "*"), time.monotonic())

    def v2_runner_on_start(self, host: Any, task: Any) -> None:
        host_name = host.get_name() if hasattr(host, "get_name") else str(host)
        self._task_starts[(self._task_uuid(task), host_name)] = time.monotonic()

    def v2_runner_on_ok(self, result: Any) -> None:
        flags = self._status_flags(result, self._result_mapping(result))
        status = "changed" if flags["changed"] else "ok"
        self._record(result, status=status)

    def v2_runner_on_failed(self, result: Any, ignore_errors: bool = False) -> None:
        _ = ignore_errors
        self._record(result, status="failed")

    def v2_runner_on_skipped(self, result: Any) -> None:
        self._record(result, status="skipped")

    def v2_runner_on_unreachable(self, result: Any) -> None:
        self._record(result, status="unreachable")

    def v2_playbook_on_stats(self, stats: Any) -> None:
        hosts = sorted(getattr(stats, "processed", {}) or {})
        recap: dict[str, dict[str, int]] = {}
        for host in hosts:
            summary = stats.summarize(host)
            recap[host] = {
                "ok": int(summary.get("ok", 0)),
                "changed": int(summary.get("changed", 0)),
                "failures": int(summary.get("failures", 0)),
                "unreachable": int(summary.get("unreachable", 0)),
                "skipped": int(summary.get("skipped", 0)),
                "rescued": int(summary.get("rescued", 0)),
                "ignored": int(summary.get("ignored", 0)),
            }

        totals = {
            "ok": sum(v["ok"] for v in recap.values()),
            "changed": sum(v["changed"] for v in recap.values()),
            "failures": sum(v["failures"] for v in recap.values()),
            "unreachable": sum(v["unreachable"] for v in recap.values()),
            "skipped": sum(v["skipped"] for v in recap.values()),
            "tasks_recorded": len(self._records),
        }

        report = {
            "schema": "automation-report",
            "schema_version": "1.0.0",
            "generated_at": _utc_now(),
            "started_at": self._started_at,
            "finished_at": _utc_now(),
            "duration_seconds": round(time.monotonic() - self._run_start, 4),
            "playbook": self._playbook,
            "check_mode": self._check_mode,
            "sanitized": True,
            "security": {
                "no_log_honored": True,
                "secrets_redacted": True,
                "result_payloads_omitted": True,
            },
            "summary": totals,
            "recap": recap,
            "tasks": self._records,
        }

        out_dir = self._report_dir()
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            out_path = out_dir / f"{self._report_prefix()}-{stamp}.json"
            out_path.write_text(
                json.dumps(report, indent=2, sort_keys=False) + "\n",
                encoding="utf-8",
            )
            self._display.display(f"[automation_report] wrote {out_path}")
        except OSError as exc:
            self._display.warning(f"[automation_report] failed to write report: {exc}")


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
