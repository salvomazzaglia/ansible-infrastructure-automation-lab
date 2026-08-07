#!/usr/bin/env python3
"""Local static CI orchestrator for ansible-infrastructure-automation-lab.

Runs yamllint, ansible-lint, repository guards, pytest, and playbook syntax
checks without connecting to real infrastructure.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PLAYBOOKS = [
    "playbooks/baseline.yml",
    "playbooks/check.yml",
    "playbooks/drift.yml",
    "playbooks/health.yml",
    "playbooks/security.yml",
    "playbooks/site.yml",
    "playbooks/web.yml",
]


def _run(cmd: list[str], *, env: dict[str, str] | None = None) -> int:
    print(f"\n==> {' '.join(cmd)}")
    completed = subprocess.run(cmd, cwd=ROOT, env=env)
    return int(completed.returncode)


def _which(name: str) -> str | None:
    return shutil.which(name)


def step_yamllint() -> int:
    exe = _which("yamllint")
    if not exe:
        print("SKIP yamllint (not installed)")
        return 0
    targets = [
        "playbooks",
        "roles",
        "inventories",
        "meta",
        "galaxy.yml",
        "requirements.yml",
    ]
    return _run([exe, "-c", ".yamllint", *targets])


def step_ansible_lint() -> int:
    exe = _which("ansible-lint")
    if not exe:
        print("SKIP ansible-lint (not installed)")
        return 0
    return _run([exe, "-c", ".ansible-lint", "playbooks", "roles"])


def step_validate_repository() -> int:
    script = ROOT / "scripts" / "validate-repository.py"
    return _run([sys.executable, str(script)])


def step_pytest() -> int:
    exe = _which("pytest")
    cmd = [exe] if exe else [sys.executable, "-m", "pytest"]
    return _run([*cmd, "tests"])


def step_syntax_check() -> int:
    exe = _which("ansible-playbook")
    if not exe:
        print("SKIP ansible-playbook syntax-check (not installed)")
        return 0
    inventory = str(ROOT / "inventories" / "synthetic" / "hosts.yml")
    env = os.environ.copy()
    # Never disable host key checking; do not target real hosts.
    env.setdefault("ANSIBLE_HOST_KEY_CHECKING", "True")
    env.setdefault("ANSIBLE_RETRY_FILES_ENABLED", "False")
    rc = 0
    for pb in PLAYBOOKS:
        code = _run(
            [
                exe,
                "--syntax-check",
                "-i",
                inventory,
                str(ROOT / pb),
            ],
            env=env,
        )
        rc = rc or code
    return rc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-lint",
        action="store_true",
        help="Skip yamllint and ansible-lint",
    )
    parser.add_argument(
        "--skip-syntax",
        action="store_true",
        help="Skip ansible-playbook --syntax-check",
    )
    parser.add_argument(
        "--only",
        choices=("yamllint", "ansible-lint", "validate", "pytest", "syntax"),
        help="Run a single step",
    )
    args = parser.parse_args()

    steps: list[tuple[str, Callable[[], int]]] = []
    if args.only:
        mapping = {
            "yamllint": step_yamllint,
            "ansible-lint": step_ansible_lint,
            "validate": step_validate_repository,
            "pytest": step_pytest,
            "syntax": step_syntax_check,
        }
        steps = [(args.only, mapping[args.only])]
    else:
        if not args.skip_lint:
            steps.append(("yamllint", step_yamllint))
            steps.append(("ansible-lint", step_ansible_lint))
        steps.append(("validate", step_validate_repository))
        steps.append(("pytest", step_pytest))
        if not args.skip_syntax:
            steps.append(("syntax", step_syntax_check))

    print(f"AIAL local CI — root={ROOT}")
    failed: list[str] = []
    for name, fn in steps:
        code = fn()
        if code != 0:
            failed.append(name)
            print(f"FAIL {name} (exit {code})")
        else:
            print(f"PASS {name}")

    if failed:
        print(f"\nLocal CI FAILED: {', '.join(failed)}")
        return 1
    print("\nLocal CI PASSED (static checks only — no real infrastructure touched)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
