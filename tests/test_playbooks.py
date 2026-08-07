"""Playbook structure, FQCN, preflight, tags, and serial tests."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.playbooks

PLAYBOOKS = [
    "baseline.yml",
    "check.yml",
    "drift.yml",
    "health.yml",
    "security.yml",
    "site.yml",
    "web.yml",
]

STATE_CHANGING = ["baseline.yml", "security.yml", "site.yml", "web.yml"]


@pytest.mark.parametrize("playbook", PLAYBOOKS)
def test_playbook_file_exists(repo_root: Path, playbook: str) -> None:
    assert (repo_root / "playbooks" / playbook).is_file()


@pytest.mark.parametrize("playbook", PLAYBOOKS)
def test_playbook_yaml_valid(repo_root: Path, playbook: str) -> None:
    path = repo_root / "playbooks" / playbook
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.parametrize("playbook", PLAYBOOKS)
def test_playbook_has_named_plays(repo_root: Path, playbook: str) -> None:
    data = yaml.safe_load((repo_root / "playbooks" / playbook).read_text(encoding="utf-8"))
    for play in data:
        assert "name" in play
        assert "hosts" in play


def test_web_yml_has_serial_one(repo_root: Path) -> None:
    data = yaml.safe_load((repo_root / "playbooks" / "web.yml").read_text(encoding="utf-8"))
    assert data[0].get("serial") == 1


def test_site_yml_web_play_has_serial(repo_root: Path) -> None:
    data = yaml.safe_load((repo_root / "playbooks" / "site.yml").read_text(encoding="utf-8"))
    web_plays = [p for p in data if p.get("hosts") == "web"]
    assert web_plays
    assert web_plays[0].get("serial") == 1


@pytest.mark.parametrize("playbook", STATE_CHANGING)
def test_state_changing_playbook_includes_preflight(repo_root: Path, playbook: str) -> None:
    text = (repo_root / "playbooks" / playbook).read_text(encoding="utf-8")
    assert "preflight.yml" in text
    assert "preflight" in text


@pytest.mark.parametrize("playbook", PLAYBOOKS)
def test_playbook_prefers_fqcn_modules(repo_root: Path, playbook: str) -> None:
    import re

    path = repo_root / "playbooks" / playbook
    text = path.read_text(encoding="utf-8")
    bare_line = re.compile(
        r"(?m)^\s{2,}(apt|yum|template|copy|file|service|set_fact|debug|assert|"
        r"import_tasks|import_role|include_role|package|uri|command|shell)\s*:\s*$"
    )
    bare_hits = [m.group(1) for m in bare_line.finditer(text)]
    assert bare_hits == [], f"bare modules in {playbook}: {bare_hits}"
    assert "ansible.builtin." in text


@pytest.mark.parametrize("playbook", PLAYBOOKS)
def test_playbook_has_tags(repo_root: Path, playbook: str) -> None:
    text = (repo_root / "playbooks" / playbook).read_text(encoding="utf-8")
    assert "tags:" in text


@pytest.mark.parametrize(
    "tag",
    ["preflight", "always"],
)
def test_state_changing_has_preflight_tags(repo_root: Path, tag: str) -> None:
    for playbook in STATE_CHANGING:
        text = (repo_root / "playbooks" / playbook).read_text(encoding="utf-8")
        assert tag in text


def test_check_yml_enables_check_mode(repo_root: Path) -> None:
    data = yaml.safe_load((repo_root / "playbooks" / "check.yml").read_text(encoding="utf-8"))
    assert data[0].get("check_mode") is True


def test_preflight_asserts_environment(repo_root: Path) -> None:
    text = (repo_root / "playbooks" / "tasks" / "preflight.yml").read_text(encoding="utf-8")
    assert "aial_environment" in text
    assert "aial_safe_to_apply" in text


def test_preflight_rejects_localhost_outside_molecule(repo_root: Path) -> None:
    text = (repo_root / "playbooks" / "tasks" / "preflight.yml").read_text(encoding="utf-8")
    assert "localhost" in text
    assert "molecule" in text


def test_fqcn_preference_helper_clean_for_playbooks(validate_mod, repo_root: Path) -> None:
    errors = [e for e in validate_mod.check_fqcn_preference(repo_root) if e.startswith("bare module")]
    assert errors == []


@pytest.mark.parametrize(
    "playbook,expected_role",
    [
        ("security.yml", "ssh_hardening"),
        ("security.yml", "firewall_policy"),
        ("baseline.yml", "common"),
        ("baseline.yml", "package_management"),
        ("web.yml", "web_service"),
        ("health.yml", "service_health"),
    ],
)
def test_playbook_references_role(repo_root: Path, playbook: str, expected_role: str) -> None:
    text = (repo_root / "playbooks" / playbook).read_text(encoding="utf-8")
    assert expected_role in text


@pytest.mark.parametrize("playbook", PLAYBOOKS)
def test_playbook_does_not_disable_host_key_checking(repo_root: Path, playbook: str) -> None:
    text = (repo_root / "playbooks" / playbook).read_text(encoding="utf-8")
    assert "host_key_checking" not in text.lower() or "true" in text.lower()
