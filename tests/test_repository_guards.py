"""Repository-wide guards and callback redaction unit tests."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.guards


def test_run_all_checks_passes(validate_mod, repo_root: Path) -> None:
    errors = validate_mod.run_all_checks(repo_root)
    assert errors == [], errors


def test_gitignore_helper(validate_mod, repo_root: Path) -> None:
    assert validate_mod.check_gitignore(repo_root) == []


def test_no_retry_files_tracked(validate_mod, repo_root: Path) -> None:
    assert validate_mod.check_retry_files(repo_root) == []


def test_gitignore_ignores_retry(repo_root: Path) -> None:
    gi = (repo_root / ".gitignore").read_text(encoding="utf-8")
    assert "*.retry" in gi


def test_no_gmail_anywhere_in_tracked_text(validate_mod, repo_root: Path) -> None:
    hits = []
    for path in validate_mod.iter_text_files(repo_root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if validate_mod.GMAIL.search(text):
            hits.append(validate_mod.rel(path, repo_root))
    assert hits == []


def test_gmail_detector_still_matches_obfuscation_free_address(validate_mod) -> None:
    # Build the needle without storing a contiguous address in this file's source
    # in a way that confuses humans; the detector must still fire on real text.
    sample = "contact@" + "gmail.com"
    assert validate_mod.GMAIL.search(sample)


def test_callback_contract(validate_mod, repo_root: Path) -> None:
    assert validate_mod.check_callback_contract(repo_root) == []


def test_no_rfc1918_in_inventories_examples_roles_playbooks(validate_mod, repo_root: Path) -> None:
    hits = []
    for path in validate_mod.iter_text_files(repo_root):
        if not any(p in path.parts for p in ("inventories", "examples", "playbooks", "roles")):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in validate_mod.RFC1918:
            if pattern.search(text):
                hits.append(validate_mod.rel(path, repo_root))
                break
    assert hits == []


@pytest.mark.parametrize(
    "ip",
    ["10.0.0.1", "192.168.1.10", "172.16.0.5", "172.31.255.255"],
)
def test_is_rfc1918_detection(validate_mod, ip: str) -> None:
    assert validate_mod.is_rfc1918_ip(ip) is True


@pytest.mark.parametrize(
    "ip",
    ["192.0.2.10", "198.51.100.1", "203.0.113.50", "8.8.8.8", "127.0.0.1"],
)
def test_non_rfc1918_examples(validate_mod, ip: str) -> None:
    assert validate_mod.is_rfc1918_ip(ip) is False


@pytest.mark.parametrize(
    "ip",
    ["192.0.2.1", "198.51.100.2", "203.0.113.3"],
)
def test_test_net_detection(validate_mod, ip: str) -> None:
    assert validate_mod.is_test_net_ip(ip) is True


def test_real_ip_patterns_absent_from_inventory(repo_root: Path, validate_mod) -> None:
    blob = validate_mod.inventory_text_blob(repo_root)
    for ip in validate_mod.extract_ipv4s(blob):
        # 127.0.0.1 may appear in comments about localhost prohibition — still flag non-comment
        if ip.startswith("127."):
            continue
        assert not validate_mod.is_rfc1918_ip(ip), ip


def test_callback_redacted_constant(callback_module) -> None:
    assert callback_module.REDACTED == "REDACTED"


@pytest.mark.parametrize(
    "key,value",
    [
        ("password", "s3cret-value"),
        ("ansible_ssh_pass", "hunter2"),
        ("become_pass", "root-pass"),
        ("api_key", "abcd1234"),
        ("private_key", "should-hide"),
        ("vault_secret", "hidden"),
        ("token", "tok_live_xxx"),
    ],
)
def test_callback_sanitize_sensitive_keys(callback_module, key: str, value: str) -> None:
    out = callback_module.CallbackModule._sanitize_value(key, value)
    assert out == callback_module.REDACTED


@pytest.mark.parametrize(
    "value",
    [
        "-----BEGIN OPENSSH PRIVATE KEY-----\nabc\n-----END OPENSSH PRIVATE KEY-----",
        "-----BEGIN RSA PRIVATE KEY-----\nabc\n-----END RSA PRIVATE KEY-----",
        "-----BEGIN PRIVATE KEY-----\nabc\n-----END PRIVATE KEY-----",
        "$ANSIBLE_VAULT;1.1;AES256\n00",
    ],
)
def test_callback_sanitize_sensitive_value_hints(callback_module, value: str) -> None:
    out = callback_module.CallbackModule._sanitize_value("msg", value)
    assert out == callback_module.REDACTED


def test_callback_sanitize_nested_dict(callback_module) -> None:
    payload = {
        "ok": True,
        "password": "nope",
        "nested": {"token": "abc", "safe": "value"},
    }
    out = callback_module.CallbackModule._sanitize_value("record", payload)
    assert out["password"] == callback_module.REDACTED
    assert out["nested"]["token"] == callback_module.REDACTED
    assert out["nested"]["safe"] == "value"
    assert out["ok"] is True


def test_callback_sanitize_list_under_sensitive_key(callback_module) -> None:
    # Sensitive keys redact the entire value (including lists) in one step.
    out = callback_module.CallbackModule._sanitize_value("password", ["a", "b"])
    assert out == callback_module.REDACTED


def test_callback_sanitize_list_nested_sensitive_items(callback_module) -> None:
    out = callback_module.CallbackModule._sanitize_value(
        "items",
        [{"token": "abc"}, {"ok": "keep"}],
    )
    assert out[0]["token"] == callback_module.REDACTED
    assert out[1]["ok"] == "keep"


def test_callback_is_no_log_from_task_flag(callback_module) -> None:
    class Task:
        no_log = True

    assert callback_module.CallbackModule._is_no_log(Task(), {}) is True


def test_callback_is_no_log_from_result_flag(callback_module) -> None:
    class Task:
        no_log = False

    assert (
        callback_module.CallbackModule._is_no_log(Task(), {"_ansible_no_log": True}) is True
    )


def test_callback_is_no_log_false_when_clear(callback_module) -> None:
    class Task:
        no_log = False

    assert callback_module.CallbackModule._is_no_log(Task(), {}) is False


def test_callback_needs_enabled(callback_module) -> None:
    assert callback_module.CallbackModule.CALLBACK_NEEDS_ENABLED is True


def test_callback_name(callback_module) -> None:
    assert callback_module.CallbackModule.CALLBACK_NAME == "automation_report"


def test_safe_string_not_redacted(callback_module) -> None:
    out = callback_module.CallbackModule._sanitize_value("msg", "SYNTHETIC DEMONSTRATION DATA")
    assert out == "SYNTHETIC DEMONSTRATION DATA"


def test_validate_main_exit_code_zero(validate_mod, repo_root: Path, monkeypatch) -> None:
    monkeypatch.setattr(validate_mod, "ROOT", repo_root)
    assert validate_mod.main() == 0


@pytest.mark.parametrize(
    "relative",
    [
        "scripts/validate-repository.py",
        "scripts/run-ci.py",
        "scripts/generate-sample-reports.py",
        "scripts/capture-report-screenshot.py",
    ],
)
def test_script_exists(repo_root: Path, relative: str) -> None:
    assert (repo_root / relative).is_file()


def test_no_package_latest_fleet_wide(validate_mod, repo_root: Path) -> None:
    assert validate_mod.scan_state_latest(repo_root) == []


def test_idempotence_no_random_in_j2(validate_mod, repo_root: Path) -> None:
    assert validate_mod.scan_random_filters(repo_root) == []
