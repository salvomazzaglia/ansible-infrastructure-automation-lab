"""Security pattern and idempotence guard tests."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.security


def test_no_curl_pipe_bash(validate_mod, repo_root: Path) -> None:
    hits = []
    for path in validate_mod.iter_text_files(repo_root):
        if path.name == "validate-repository.py":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if validate_mod.CURL_BASH.search(text):
            hits.append(validate_mod.rel(path, repo_root))
    assert hits == []


def test_no_wget_pipe_bash(validate_mod, repo_root: Path) -> None:
    hits = []
    for path in validate_mod.iter_text_files(repo_root):
        if path.name == "validate-repository.py":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if validate_mod.WGET_BASH.search(text):
            hits.append(validate_mod.rel(path, repo_root))
    assert hits == []


def test_no_chmod_777_in_automation_content(validate_mod, repo_root: Path) -> None:
    errors = [
        e
        for e in validate_mod.check_dangerous_shell_patterns(repo_root)
        if "chmod 777" in e
    ]
    assert errors == []


def test_no_state_latest_in_tasks(validate_mod, repo_root: Path) -> None:
    assert validate_mod.scan_state_latest(repo_root) == []


def test_package_management_uses_present_not_latest(repo_root: Path) -> None:
    text = (repo_root / "roles" / "package_management" / "tasks" / "main.yml").read_text(
        encoding="utf-8"
    )
    assert "state: present" in text
    assert "state: latest" not in text


def test_no_permit_root_login_yes_in_role_defaults(repo_root: Path) -> None:
    defaults = repo_root / "roles" / "ssh_hardening" / "defaults" / "main.yml"
    data_text = defaults.read_text(encoding="utf-8")
    assert "aial_ssh_permit_root_login: yes" not in data_text
    assert "prohibit-password" in data_text


def test_no_password_authentication_yes_as_default(repo_root: Path) -> None:
    defaults = (repo_root / "roles" / "ssh_hardening" / "defaults" / "main.yml").read_text(
        encoding="utf-8"
    )
    assert "aial_ssh_password_authentication: true" not in defaults
    assert "aial_ssh_password_authentication: false" in defaults


def test_host_key_checking_not_disabled(repo_root: Path, validate_mod) -> None:
    cfg = (repo_root / "ansible.cfg").read_text(encoding="utf-8")
    assert not validate_mod.HOST_KEY_FALSE.search(cfg)
    assert "host_key_checking = True" in cfg or "host_key_checking=True" in cfg.replace(" ", "")


def test_no_pull_request_target_when_ci_present(validate_mod, repo_root: Path) -> None:
    errors = [e for e in validate_mod.check_ci_workflow(repo_root) if "pull_request_target" in e]
    assert errors == []


def test_no_self_hosted_runners_when_ci_present(validate_mod, repo_root: Path) -> None:
    errors = [e for e in validate_mod.check_ci_workflow(repo_root) if "self-hosted" in e]
    assert errors == []


def test_actions_sha_pinning_soft_when_ci_absent(repo_root: Path, validate_mod) -> None:
    workflows = list((repo_root / ".github" / "workflows").glob("*.yml")) if (
        repo_root / ".github" / "workflows"
    ).is_dir() else []
    if not workflows:
        pytest.skip("CI workflows not present yet")
    errors = validate_mod.check_ci_workflow(repo_root)
    pin_errors = [e for e in errors if "SHA" in e or "unpinned" in e]
    assert pin_errors == []


def test_ssh_secure_defaults_helper(validate_mod, repo_root: Path) -> None:
    assert validate_mod.check_ssh_secure_defaults(repo_root) == []


def test_ansible_cfg_helper(validate_mod, repo_root: Path) -> None:
    assert validate_mod.check_ansible_cfg(repo_root) == []


def test_no_random_filters_in_templates(validate_mod, repo_root: Path) -> None:
    assert validate_mod.scan_random_filters(repo_root) == []


def test_changed_when_false_without_justification(validate_mod, repo_root: Path) -> None:
    assert validate_mod.scan_changed_when_false_abuse(repo_root) == []


@pytest.mark.parametrize(
    "relative",
    [
        "roles/package_management/tasks/main.yml",
        "roles/web_service/tasks/main.yml",
        "roles/common/tasks/main.yml",
        "roles/accounts/tasks/main.yml",
        "roles/ssh_hardening/tasks/main.yml",
        "roles/firewall_policy/tasks/main.yml",
        "roles/logging/tasks/main.yml",
        "roles/time_sync/tasks/main.yml",
        "roles/automatic_updates/tasks/main.yml",
        "roles/service_health/tasks/main.yml",
    ],
)
def test_role_tasks_have_no_state_latest(repo_root: Path, relative: str) -> None:
    text = (repo_root / relative).read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        assert "state: latest" not in line.lower()


@pytest.mark.parametrize(
    "template",
    [
        "roles/web_service/templates/nginx-site.conf.j2",
        "roles/web_service/templates/index.html.j2",
        "roles/ssh_hardening/templates/50-aial-hardening.conf.j2",
        "roles/firewall_policy/templates/policy.nft.j2",
        "roles/logging/templates/journald.conf.j2",
        "roles/logging/templates/rsyslog-remote.conf.j2",
        "roles/time_sync/templates/chrony.conf.j2",
        "roles/time_sync/templates/timesyncd.conf.j2",
        "roles/automatic_updates/templates/20auto-upgrades.j2",
        "roles/automatic_updates/templates/50unattended-upgrades-aial.j2",
    ],
)
def test_template_has_no_random_filter(repo_root: Path, template: str, validate_mod) -> None:
    path = repo_root / template
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert not validate_mod.RANDOM_FILTER.search(text)


def test_dangerous_shell_helper_clean(validate_mod, repo_root: Path) -> None:
    # Exclude the validator source documenting regexes by filtering curl/wget only in yml/j2/sh
    errors = validate_mod.check_dangerous_shell_patterns(repo_root)
    actionable = [e for e in errors if not e.endswith("validate-repository.py")]
    assert actionable == []


def test_emergency_ssh_defaults_still_not_yes(repo_root: Path) -> None:
    text = (repo_root / "roles" / "ssh_hardening" / "defaults" / "main.yml").read_text(
        encoding="utf-8"
    )
    assert "aial_ssh_emergency_permit_root_login: yes" not in text
    assert "aial_ssh_emergency_password_authentication: true" not in text
