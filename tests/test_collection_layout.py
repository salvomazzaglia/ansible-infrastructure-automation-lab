"""Collection layout and galaxy metadata tests."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.collection


def test_galaxy_yml_exists(repo_root: Path) -> None:
    assert (repo_root / "galaxy.yml").is_file()


def test_galaxy_namespace(galaxy: dict) -> None:
    assert galaxy["namespace"] == "salvomazzaglia"


def test_galaxy_name(galaxy: dict) -> None:
    assert galaxy["name"] == "infrastructure_automation"


def test_galaxy_version(galaxy: dict) -> None:
    assert str(galaxy["version"]) == "1.0.0"


def test_galaxy_version_matches_version_file(repo_root: Path, galaxy: dict) -> None:
    version = (repo_root / "VERSION").read_text(encoding="utf-8").strip()
    assert version == str(galaxy["version"])


def test_galaxy_has_authors(galaxy: dict) -> None:
    assert galaxy.get("authors")
    assert isinstance(galaxy["authors"], list)


def test_galaxy_license_mit(galaxy: dict) -> None:
    license_field = galaxy.get("license") or galaxy.get("license_file")
    assert license_field
    if isinstance(license_field, list):
        assert "MIT" in license_field


def test_galaxy_build_ignore_includes_reports(galaxy: dict) -> None:
    ignore = galaxy.get("build_ignore") or []
    assert "reports" in ignore


def test_galaxy_build_ignore_includes_tests(galaxy: dict) -> None:
    ignore = galaxy.get("build_ignore") or []
    assert "tests" in ignore


def test_galaxy_repository_url(galaxy: dict) -> None:
    assert "ansible-infrastructure-automation-lab" in galaxy.get("repository", "")


def test_runtime_yml_exists(repo_root: Path) -> None:
    assert (repo_root / "meta" / "runtime.yml").is_file()


def test_runtime_requires_ansible(runtime: dict) -> None:
    assert "requires_ansible" in runtime
    assert str(runtime["requires_ansible"]).startswith(">=")


def test_runtime_requires_ansible_2_20(runtime: dict) -> None:
    req = str(runtime["requires_ansible"])
    assert "2.20" in req


def test_expected_role_count(expected_roles: tuple[str, ...]) -> None:
    assert len(expected_roles) == 10


@pytest.mark.parametrize(
    "role",
    [
        "accounts",
        "automatic_updates",
        "common",
        "firewall_policy",
        "logging",
        "package_management",
        "service_health",
        "ssh_hardening",
        "time_sync",
        "web_service",
    ],
)
def test_role_directory_exists(repo_root: Path, role: str) -> None:
    assert (repo_root / "roles" / role).is_dir()


@pytest.mark.parametrize(
    "role",
    [
        "accounts",
        "automatic_updates",
        "common",
        "firewall_policy",
        "logging",
        "package_management",
        "service_health",
        "ssh_hardening",
        "time_sync",
        "web_service",
    ],
)
def test_role_tasks_main_exists(repo_root: Path, role: str) -> None:
    assert (repo_root / "roles" / role / "tasks" / "main.yml").is_file()


@pytest.mark.parametrize(
    "role",
    [
        "accounts",
        "automatic_updates",
        "common",
        "firewall_policy",
        "logging",
        "package_management",
        "service_health",
        "ssh_hardening",
        "time_sync",
        "web_service",
    ],
)
def test_role_defaults_main_exists(repo_root: Path, role: str) -> None:
    assert (repo_root / "roles" / role / "defaults" / "main.yml").is_file()


@pytest.mark.parametrize(
    "role",
    [
        "accounts",
        "automatic_updates",
        "common",
        "firewall_policy",
        "logging",
        "package_management",
        "service_health",
        "ssh_hardening",
        "time_sync",
        "web_service",
    ],
)
def test_role_meta_main_exists(repo_root: Path, role: str) -> None:
    assert (repo_root / "roles" / role / "meta" / "main.yml").is_file()


@pytest.mark.parametrize(
    "role",
    [
        "accounts",
        "automatic_updates",
        "common",
        "firewall_policy",
        "logging",
        "package_management",
        "service_health",
        "ssh_hardening",
        "time_sync",
        "web_service",
    ],
)
def test_role_readme_exists(repo_root: Path, role: str) -> None:
    assert (repo_root / "roles" / role / "README.md").is_file()


@pytest.mark.parametrize(
    "playbook",
    [
        "baseline.yml",
        "check.yml",
        "drift.yml",
        "health.yml",
        "security.yml",
        "site.yml",
        "web.yml",
    ],
)
def test_playbook_exists(repo_root: Path, playbook: str) -> None:
    assert (repo_root / "playbooks" / playbook).is_file()


def test_preflight_tasks_exist(repo_root: Path) -> None:
    assert (repo_root / "playbooks" / "tasks" / "preflight.yml").is_file()


def test_callback_plugin_exists(repo_root: Path) -> None:
    assert (repo_root / "plugins" / "callback" / "automation_report.py").is_file()


def test_plugins_init_exists(repo_root: Path) -> None:
    assert (repo_root / "plugins" / "callback" / "__init__.py").is_file()


def test_collection_structure_for_build(repo_root: Path) -> None:
    """Minimal paths required for ansible-galaxy collection build."""
    for relative in ("galaxy.yml", "meta/runtime.yml", "plugins", "roles", "playbooks"):
        assert (repo_root / relative).exists(), relative


def test_no_extra_unexpected_top_level_roles(repo_root: Path, expected_roles: tuple[str, ...]) -> None:
    found = sorted(p.name for p in (repo_root / "roles").iterdir() if p.is_dir())
    assert found == sorted(expected_roles)


def test_validate_collection_layout_passes(validate_mod, repo_root: Path) -> None:
    errors = validate_mod.check_collection_layout(repo_root)
    assert errors == []


def test_meta_main_yaml_valid_for_each_role(repo_root: Path, expected_roles: tuple[str, ...]) -> None:
    for role in expected_roles:
        path = repo_root / "roles" / role / "meta" / "main.yml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data is None or isinstance(data, dict)


@pytest.mark.parametrize(
    "relative",
    [
        "ansible.cfg",
        "requirements.yml",
        "requirements-dev.txt",
        ".yamllint",
        ".ansible-lint",
        ".gitignore",
        "schemas/automation-report.schema.json",
        "schemas/drift-report.schema.json",
    ],
)
def test_supporting_file_exists(repo_root: Path, relative: str) -> None:
    assert (repo_root / relative).is_file()
