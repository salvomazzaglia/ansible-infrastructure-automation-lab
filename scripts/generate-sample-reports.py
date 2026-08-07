#!/usr/bin/env python3
"""Generate deterministic synthetic sample automation reports.

Writes JSON/HTML under examples/. Hosts use .example.invalid only.
No real infrastructure data.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
BANNER = "SYNTHETIC DEMONSTRATION DATA"
GENERATED_AT = "2026-08-01T12:00:00Z"

HOSTS = [
    "web01.lab.example.invalid",
    "web02.lab.example.invalid",
    "app01.lab.example.invalid",
    "db01.lab.example.invalid",
    "mon01.lab.example.invalid",
    "bastion01.lab.example.invalid",
]
GROUPS = ["web", "app", "database", "monitoring", "bastion"]
ROLES = [
    "common",
    "package_management",
    "accounts",
    "ssh_hardening",
    "time_sync",
    "logging",
    "automatic_updates",
    "firewall_policy",
    "web_service",
    "service_health",
]


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def _task(
    host: str,
    role: str,
    task: str,
    *,
    status: str,
    changed: bool = False,
    failed: bool = False,
    skipped: bool = False,
    duration: float = 0.12,
    no_log: bool = False,
    check_mode: bool = False,
    play: str = "Synthetic infrastructure baseline",
) -> dict:
    return {
        "play": play,
        "host": host,
        "task": task,
        "role": role,
        "status": status,
        "changed": changed,
        "failed": failed,
        "skipped": skipped,
        "unreachable": False,
        "duration_seconds": duration,
        "no_log": no_log,
        "check_mode": check_mode,
        "result": "REDACTED" if no_log else None,
    }


def _recap_for(hosts: list[str], *, changed: int, ok: int, skipped: int = 0) -> dict:
    per = {}
    for host in hosts:
        per[host] = {
            "ok": ok,
            "changed": changed,
            "failures": 0,
            "unreachable": 0,
            "skipped": skipped,
            "rescued": 0,
            "ignored": 0,
        }
    return per


def sample_check_report() -> dict:
    tasks = [
        _task(
            HOSTS[0],
            "ssh_hardening",
            "Ensure SSH PermitRootLogin is prohibit-password",
            status="changed",
            changed=True,
            check_mode=True,
            duration=0.21,
        ),
        _task(
            HOSTS[1],
            "firewall_policy",
            "Ensure nftables baseline policy is present",
            status="ok",
            check_mode=True,
            duration=0.18,
        ),
        _task(
            HOSTS[2],
            "accounts",
            "Ensure service account password hash is managed",
            status="ok",
            no_log=True,
            check_mode=True,
            duration=0.09,
        ),
        _task(
            HOSTS[3],
            "time_sync",
            "Ensure chrony is configured",
            status="changed",
            changed=True,
            check_mode=True,
            duration=0.15,
        ),
        _task(
            HOSTS[4],
            "logging",
            "Ensure journald persistent storage",
            status="ok",
            check_mode=True,
            duration=0.11,
        ),
        _task(
            HOSTS[5],
            "package_management",
            "Ensure baseline packages are present",
            status="skipped",
            skipped=True,
            check_mode=True,
            duration=0.02,
        ),
    ]
    return {
        "schema": "automation-report",
        "schema_version": "1.0.0",
        "banner": BANNER,
        "generated_at": GENERATED_AT,
        "started_at": "2026-08-01T11:59:40Z",
        "finished_at": GENERATED_AT,
        "duration_seconds": 20.0,
        "playbook": "playbooks/site.yml",
        "mode": "check",
        "check_mode": True,
        "sanitized": True,
        "security": {
            "no_log_honored": True,
            "secrets_redacted": True,
            "result_payloads_omitted": True,
        },
        "inventory": {
            "groups": GROUPS,
            "host_count": len(HOSTS),
            "hosts": HOSTS,
        },
        "roles": ROLES,
        "summary": {
            "ok": 3,
            "changed": 2,
            "failures": 0,
            "unreachable": 0,
            "skipped": 1,
            "unchanged": 3,
            "tasks_recorded": len(tasks),
        },
        "recap": _recap_for(HOSTS, changed=0, ok=1, skipped=0),
        "tasks": tasks,
        "limitations": [
            "Synthetic demonstration data only.",
            "Hosts use .example.invalid aliases; no ansible_host addresses.",
            "Check mode reports proposed changes; nothing was applied.",
        ],
    }


def sample_apply_report() -> dict:
    tasks = [
        _task(
            HOSTS[0],
            "web_service",
            "Deploy nginx site configuration",
            status="changed",
            changed=True,
            duration=0.44,
        ),
        _task(
            HOSTS[1],
            "web_service",
            "Deploy nginx site configuration",
            status="changed",
            changed=True,
            duration=0.41,
        ),
        _task(
            HOSTS[2],
            "firewall_policy",
            "Apply application firewall policy",
            status="changed",
            changed=True,
            duration=0.33,
        ),
        _task(
            HOSTS[3],
            "logging",
            "Configure remote syslog forwarding",
            status="ok",
            duration=0.19,
        ),
        _task(
            HOSTS[0],
            "accounts",
            "Set service account password",
            status="ok",
            no_log=True,
            duration=0.08,
        ),
    ]
    return {
        "schema": "automation-report",
        "schema_version": "1.0.0",
        "banner": BANNER,
        "generated_at": GENERATED_AT,
        "started_at": "2026-08-01T12:05:00Z",
        "finished_at": "2026-08-01T12:05:45Z",
        "duration_seconds": 45.0,
        "playbook": "playbooks/site.yml",
        "mode": "apply",
        "check_mode": False,
        "sanitized": True,
        "security": {
            "no_log_honored": True,
            "secrets_redacted": True,
            "result_payloads_omitted": True,
        },
        "inventory": {
            "groups": GROUPS,
            "host_count": len(HOSTS),
            "hosts": HOSTS,
        },
        "roles": ROLES,
        "summary": {
            "ok": 2,
            "changed": 3,
            "failures": 0,
            "unreachable": 0,
            "skipped": 0,
            "unchanged": 2,
            "tasks_recorded": len(tasks),
        },
        "recap": _recap_for(HOSTS[:4], changed=1, ok=2),
        "tasks": tasks,
        "limitations": [
            "Synthetic demonstration data only.",
            "Apply sample illustrates changed vs ok outcomes without real hosts.",
        ],
    }


def sample_idempotence_report() -> dict:
    tasks = [
        _task(
            HOSTS[0],
            "web_service",
            "Deploy nginx site configuration",
            status="ok",
            duration=0.22,
            play="Synthetic idempotence second run",
        ),
        _task(
            HOSTS[1],
            "ssh_hardening",
            "Ensure SSH hardening template is applied",
            status="ok",
            duration=0.17,
            play="Synthetic idempotence second run",
        ),
        _task(
            HOSTS[2],
            "firewall_policy",
            "Ensure nftables baseline policy is present",
            status="ok",
            duration=0.14,
            play="Synthetic idempotence second run",
        ),
    ]
    return {
        "schema": "automation-report",
        "schema_version": "1.0.0",
        "banner": BANNER,
        "generated_at": GENERATED_AT,
        "started_at": "2026-08-01T12:10:00Z",
        "finished_at": "2026-08-01T12:10:18Z",
        "duration_seconds": 18.0,
        "playbook": "playbooks/site.yml",
        "mode": "idempotence",
        "check_mode": False,
        "sanitized": True,
        "security": {
            "no_log_honored": True,
            "secrets_redacted": True,
            "result_payloads_omitted": True,
        },
        "inventory": {
            "groups": GROUPS,
            "host_count": len(HOSTS),
            "hosts": HOSTS,
        },
        "roles": ROLES,
        "summary": {
            "ok": 3,
            "changed": 0,
            "failures": 0,
            "unreachable": 0,
            "skipped": 0,
            "unchanged": 3,
            "tasks_recorded": len(tasks),
        },
        "recap": _recap_for(HOSTS[:3], changed=0, ok=3),
        "tasks": tasks,
        "idempotence": {
            "second_run_changed": 0,
            "passed": True,
            "notes": "Second apply reported zero changes on synthetic hosts.",
        },
        "limitations": [
            "Synthetic demonstration data only.",
            "Idempotence sample is illustrative; Molecule verifies roles separately.",
        ],
    }


def sample_drift_report() -> dict:
    findings = [
        {
            "host": HOSTS[0],
            "role": "ssh_hardening",
            "task": "Ensure SSH PermitRootLogin is prohibit-password",
            "expected_change": True,
            "changed": True,
            "status": "change_required",
            "severity": "high",
            "importance": "high",
            "reason": "Observed PermitRootLogin differs from desired prohibit-password.",
            "check_mode": True,
            "timestamp": "2026-08-01T11:59:50Z",
        },
        {
            "host": HOSTS[1],
            "role": "firewall_policy",
            "task": "Ensure nftables baseline policy is present",
            "expected_change": False,
            "changed": False,
            "status": "compliant",
            "severity": "low",
            "importance": "low",
            "reason": "Firewall policy matches desired state.",
            "check_mode": True,
            "timestamp": "2026-08-01T11:59:52Z",
        },
        {
            "host": HOSTS[2],
            "role": "time_sync",
            "task": "Ensure chrony is configured",
            "expected_change": True,
            "changed": True,
            "status": "change_required",
            "severity": "medium",
            "importance": "medium",
            "reason": "NTP servers list diverges from group_vars.",
            "check_mode": True,
            "timestamp": "2026-08-01T11:59:54Z",
        },
        {
            "host": HOSTS[3],
            "role": "service_health",
            "task": "Probe synthetic health endpoint",
            "expected_change": False,
            "changed": False,
            "status": "unavailable",
            "severity": "medium",
            "importance": "medium",
            "reason": "Host unreachable in synthetic check inventory subset.",
            "check_mode": True,
            "timestamp": "2026-08-01T11:59:56Z",
        },
        {
            "host": HOSTS[4],
            "role": "logging",
            "task": "Ensure journald persistent storage",
            "expected_change": False,
            "changed": False,
            "status": "skipped",
            "severity": "low",
            "importance": "low",
            "reason": "Role tagged out for monitoring group in this sample run.",
            "check_mode": True,
            "timestamp": "2026-08-01T11:59:58Z",
        },
        {
            "host": HOSTS[5],
            "role": "accounts",
            "task": "Ensure service account password hash is managed",
            "expected_change": False,
            "changed": False,
            "status": "failed",
            "severity": "critical",
            "importance": "critical",
            "reason": "Synthetic failure: required variable placeholder not provided.",
            "check_mode": True,
            "timestamp": GENERATED_AT,
        },
    ]
    summary = {
        "compliant": 1,
        "change_required": 2,
        "unavailable": 1,
        "failed": 1,
        "skipped": 1,
        "total": len(findings),
    }
    return {
        "schema": "drift-report",
        "schema_version": "1.0.0",
        "banner": BANNER,
        "generated_at": GENERATED_AT,
        "playbook": "playbooks/site.yml",
        "check_mode": True,
        "inventory_groups": GROUPS,
        "summary": summary,
        "findings": findings,
        "limitations": [
            "Synthetic demonstration data only.",
            "Drift statuses are illustrative for schema and UI samples.",
        ],
    }


def render_html(
    check: dict,
    apply: dict,
    idem: dict,
    drift: dict,
) -> str:
    inv = check["inventory"]
    summary = apply["summary"]
    roles = ", ".join(html.escape(r) for r in check["roles"])
    groups = ", ".join(html.escape(g) for g in inv["groups"])
    hosts = "".join(f"<li>{html.escape(h)}</li>" for h in inv["hosts"])
    drift_rows = "".join(
        "<tr>"
        f"<td>{html.escape(f['host'])}</td>"
        f"<td>{html.escape(f['role'])}</td>"
        f"<td>{html.escape(f['status'])}</td>"
        f"<td>{html.escape(f['severity'])}</td>"
        f"<td>{html.escape(f['reason'])}</td>"
        "</tr>"
        for f in drift["findings"]
    )
    changed_tasks = [
        t for t in apply["tasks"] if t["changed"] and not t["failed"]
    ]
    unchanged_tasks = [t for t in apply["tasks"] if not t["changed"] and not t["skipped"]]
    failed_tasks = [t for t in apply["tasks"] if t["failed"]]
    skipped_tasks = [t for t in check["tasks"] if t["skipped"]]

    def task_list(items: list[dict]) -> str:
        if not items:
            return "<li>None in this synthetic sample.</li>"
        return "".join(
            f"<li>{html.escape(t['host'])} — {html.escape(t['task'])} "
            f"({html.escape(t['role'] or 'n/a')})</li>"
            for t in items
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sample Automation Report — Ansible Infrastructure Automation Lab</title>
  <style>
    :root {{
      --bg: #f3f6f8;
      --panel: #ffffff;
      --ink: #15202b;
      --muted: #5b6b7c;
      --accent: #0f6a5c;
      --accent-soft: #d8efe9;
      --warn: #9a5b00;
      --line: #d5dde5;
      --banner: #7a1f1f;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "Helvetica Neue", Helvetica, Arial, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(1200px 500px at 10% -10%, #e7f3ef 0%, transparent 55%),
        linear-gradient(180deg, #eef3f7 0%, var(--bg) 40%, #e8eef3 100%);
      line-height: 1.45;
    }}
    header {{
      padding: 28px 40px 18px;
      border-bottom: 1px solid var(--line);
      background: rgba(255,255,255,0.72);
      backdrop-filter: blur(6px);
    }}
    .banner {{
      display: inline-block;
      background: var(--banner);
      color: #fff;
      font-weight: 700;
      letter-spacing: 0.04em;
      font-size: 12px;
      padding: 6px 10px;
      margin-bottom: 12px;
    }}
    h1 {{
      margin: 0 0 6px;
      font-size: 28px;
      font-weight: 700;
    }}
    .subtitle {{
      margin: 0;
      color: var(--muted);
      max-width: 70ch;
    }}
    main {{
      padding: 24px 40px 48px;
      display: grid;
      gap: 18px;
    }}
    section {{
      background: var(--panel);
      border: 1px solid var(--line);
      padding: 18px 20px;
    }}
    h2 {{
      margin: 0 0 10px;
      font-size: 16px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--accent);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }}
    .stat {{
      background: var(--accent-soft);
      padding: 12px 14px;
      border-left: 4px solid var(--accent);
    }}
    .stat .label {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .stat .value {{
      font-size: 26px;
      font-weight: 700;
    }}
    ul {{ margin: 0; padding-left: 18px; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th, td {{
      text-align: left;
      padding: 8px 10px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-weight: 600;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .two-col {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
    }}
    .note {{
      color: var(--warn);
      font-size: 13px;
    }}
    footer {{
      padding: 0 40px 36px;
      color: var(--muted);
      font-size: 12px;
    }}
    @media (max-width: 960px) {{
      .grid, .two-col {{ grid-template-columns: 1fr 1fr; }}
      header, main, footer {{ padding-left: 18px; padding-right: 18px; }}
    }}
    @media (max-width: 640px) {{
      .grid, .two-col {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="banner">{html.escape(BANNER)}</div>
    <h1>Ansible Infrastructure Automation Lab</h1>
    <p class="subtitle">
      Standalone synthetic execution summary for portfolio demonstration.
      Generated at {html.escape(GENERATED_AT)}. No real infrastructure data.
    </p>
  </header>
  <main>
    <section>
      <h2>Execution summary</h2>
      <div class="grid">
        <div class="stat"><span class="label">Hosts</span><span class="value">{inv["host_count"]}</span></div>
        <div class="stat"><span class="label">Changed</span><span class="value">{summary["changed"]}</span></div>
        <div class="stat"><span class="label">Unchanged</span><span class="value">{summary.get("unchanged", summary["ok"])}</span></div>
        <div class="stat"><span class="label">Failed</span><span class="value">{summary["failures"]}</span></div>
      </div>
      <p style="margin:14px 0 0;color:var(--muted);font-size:14px;">
        Playbook <strong>playbooks/site.yml</strong> · Apply duration
        <strong>{apply["duration_seconds"]}s</strong> · Sanitized metadata only
      </p>
    </section>

    <div class="two-col">
      <section>
        <h2>Inventory groups</h2>
        <p>{groups}</p>
        <p class="note">Aliases only — no ansible_host / RFC1918 addresses.</p>
      </section>
      <section>
        <h2>Host count</h2>
        <p><strong>{inv["host_count"]}</strong> synthetic hosts</p>
        <ul>{hosts}</ul>
      </section>
    </div>

    <section>
      <h2>Roles</h2>
      <p>{roles}</p>
    </section>

    <div class="two-col">
      <section>
        <h2>Changed tasks</h2>
        <ul>{task_list(changed_tasks)}</ul>
      </section>
      <section>
        <h2>Unchanged tasks</h2>
        <ul>{task_list(unchanged_tasks)}</ul>
      </section>
    </div>

    <div class="two-col">
      <section>
        <h2>Failed tasks</h2>
        <ul>{task_list(failed_tasks)}</ul>
      </section>
      <section>
        <h2>Skipped tasks</h2>
        <ul>{task_list(skipped_tasks)}</ul>
      </section>
    </div>

    <div class="two-col">
      <section>
        <h2>Check-mode</h2>
        <p>
          Check sample reported
          <strong>{check["summary"]["changed"]}</strong> proposed changes and
          <strong>{check["summary"]["ok"]}</strong> compliant outcomes without applying state.
        </p>
      </section>
      <section>
        <h2>Idempotence</h2>
        <p>
          Second-run sample:
          <strong>{idem["idempotence"]["second_run_changed"]}</strong> changes —
          passed={str(idem["idempotence"]["passed"]).lower()}.
        </p>
      </section>
    </div>

    <section>
      <h2>Drift</h2>
      <table>
        <thead>
          <tr>
            <th>Host</th><th>Role</th><th>Status</th><th>Severity</th><th>Reason</th>
          </tr>
        </thead>
        <tbody>
          {drift_rows}
        </tbody>
      </table>
    </section>

    <section>
      <h2>Security controls</h2>
      <ul>
        <li>no_log honored — sensitive task results recorded as REDACTED only</li>
        <li>No vault values, passwords, SSH keys, or become passwords in reports</li>
        <li>Runtime reports default to gitignored <code>reports/</code> (AIAL_REPORT_DIR)</li>
        <li>Sample vault placeholders live in <code>examples/vault.example.yml</code></li>
      </ul>
    </section>

    <section>
      <h2>Limitations</h2>
      <ul>
        <li>This HTML is synthetic demonstration data for documentation and CI screenshots.</li>
        <li>Hosts end in <code>.example.invalid</code> and must not resolve on public DNS.</li>
        <li>Not an Ansible Automation Platform certification artifact.</li>
      </ul>
    </section>
  </main>
  <footer>
    salvomazzaglia/ansible-infrastructure-automation-lab · {html.escape(BANNER)}
  </footer>
</body>
</html>
"""


def main() -> int:
    EXAMPLES.mkdir(parents=True, exist_ok=True)
    check = sample_check_report()
    apply = sample_apply_report()
    idem = sample_idempotence_report()
    drift = sample_drift_report()

    _write_json(EXAMPLES / "sample-check-report.json", check)
    _write_json(EXAMPLES / "sample-apply-report.json", apply)
    _write_json(EXAMPLES / "sample-idempotence-report.json", idem)
    _write_json(EXAMPLES / "sample-drift-report.json", drift)

    html_path = EXAMPLES / "sample-automation-report.html"
    html_path.write_text(render_html(check, apply, idem, drift), encoding="utf-8", newline="\n")

    written = [
        "examples/sample-check-report.json",
        "examples/sample-apply-report.json",
        "examples/sample-idempotence-report.json",
        "examples/sample-drift-report.json",
        "examples/sample-automation-report.html",
    ]
    for rel in written:
        print(f"wrote {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
