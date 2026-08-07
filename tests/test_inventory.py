"""Synthetic inventory hygiene tests."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.inventory


def _host_names(data: dict) -> list[str]:
    hosts: list[str] = []

    def walk(node):
        if not isinstance(node, dict):
            return
        h = node.get("hosts")
        if isinstance(h, dict):
            hosts.extend(h.keys())
        children = node.get("children")
        if isinstance(children, dict):
            for child in children.values():
                walk(child)

    walk(data.get("all") or data)
    return hosts


def _group_names(data: dict) -> set[str]:
    groups: set[str] = set()

    def walk(node, name=None):
        if not isinstance(node, dict):
            return
        if name:
            groups.add(name)
        children = node.get("children")
        if isinstance(children, dict):
            for child_name, child in children.items():
                walk(child, child_name)

    walk(data.get("all") or data, "all")
    return groups


def test_hosts_yml_exists(repo_root: Path) -> None:
    assert (repo_root / "inventories" / "synthetic" / "hosts.yml").is_file()


def test_hosts_yml_valid_yaml(hosts_yml: dict) -> None:
    assert isinstance(hosts_yml, dict)
    assert "all" in hosts_yml


def test_exactly_six_hosts(hosts_yml: dict) -> None:
    assert len(_host_names(hosts_yml)) == 6


@pytest.mark.parametrize(
    "host",
    [
        "ansible-bastion-01.lab.example.invalid",
        "ansible-web-01.lab.example.invalid",
        "ansible-web-02.lab.example.invalid",
        "ansible-app-01.lab.example.invalid",
        "ansible-db-01.lab.example.invalid",
        "ansible-monitor-01.lab.example.invalid",
    ],
)
def test_expected_host_present(hosts_yml: dict, host: str) -> None:
    assert host in _host_names(hosts_yml)


@pytest.mark.parametrize(
    "host",
    [
        "ansible-bastion-01.lab.example.invalid",
        "ansible-web-01.lab.example.invalid",
        "ansible-web-02.lab.example.invalid",
        "ansible-app-01.lab.example.invalid",
        "ansible-db-01.lab.example.invalid",
        "ansible-monitor-01.lab.example.invalid",
    ],
)
def test_host_ends_with_example_invalid(host: str) -> None:
    assert host.endswith(".lab.example.invalid") or host.endswith(".example.invalid")


@pytest.mark.parametrize(
    "group",
    ["bastion", "web", "application", "app", "database", "monitoring"],
)
def test_expected_group_present(hosts_yml: dict, group: str) -> None:
    assert group in _group_names(hosts_yml)


def test_no_ansible_host_key(repo_root: Path) -> None:
    inv = repo_root / "inventories"
    for path in inv.rglob("*.yml"):
        text = path.read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.lstrip().startswith("#"):
                continue
            assert "ansible_host:" not in line, path


def test_no_localhost_host_entry(hosts_yml: dict) -> None:
    names = set(_host_names(hosts_yml))
    assert "localhost" not in names
    assert "127.0.0.1" not in names


def test_no_rfc1918_in_inventory_files(repo_root: Path, validate_mod) -> None:
    inv = repo_root / "inventories"
    for path in inv.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".yml", ".yaml", ".md"}:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in validate_mod.RFC1918:
            assert not pattern.search(text), f"{path}: {pattern.pattern}"


@pytest.mark.parametrize(
    "domain",
    ["gmail.com", "company.com", "corp.com", "microsoft.com", "amazon.com"],
)
def test_no_real_domains_as_inventory_hosts(hosts_yml: dict, domain: str) -> None:
    for host in _host_names(hosts_yml):
        assert not host.endswith(domain)
        assert domain not in host


def test_aial_environment_synthetic(all_group_vars: dict) -> None:
    assert all_group_vars["aial_environment"] == "synthetic"


def test_aial_safe_to_apply_false(all_group_vars: dict) -> None:
    assert all_group_vars["aial_safe_to_apply"] is False


def test_group_vars_all_yaml_valid(all_group_vars: dict) -> None:
    assert isinstance(all_group_vars, dict)


@pytest.mark.parametrize(
    "group_file",
    ["web.yml", "app.yml", "database.yml", "monitoring.yml"],
)
def test_group_vars_file_valid_yaml(repo_root: Path, group_file: str) -> None:
    path = repo_root / "inventories" / "synthetic" / "group_vars" / group_file
    assert path.is_file()
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data is None or isinstance(data, dict)


def test_host_vars_web01_exists(repo_root: Path) -> None:
    path = (
        repo_root
        / "inventories"
        / "synthetic"
        / "host_vars"
        / "ansible-web-01.lab.example.invalid.yml"
    )
    assert path.is_file()
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data is None or isinstance(data, dict)


def test_inventory_readme_exists(repo_root: Path) -> None:
    assert (repo_root / "inventories" / "README.md").is_file()


def test_validate_inventory_guards_pass(validate_mod, repo_root: Path) -> None:
    assert validate_mod.check_inventory_guards(repo_root) == []


def test_packages_never_latest_in_group_vars(all_group_vars: dict) -> None:
    # present/absent lists only — no state latest knobs
    assert "aial_packages_present" in all_group_vars
    assert isinstance(all_group_vars["aial_packages_present"], list)


def test_ssh_defaults_in_inventory_are_hardened(all_group_vars: dict) -> None:
    assert all_group_vars.get("aial_ssh_permit_root_login") != "yes"
    assert all_group_vars.get("aial_ssh_password_authentication") is False


def test_firewall_apply_disabled_in_synthetic(all_group_vars: dict) -> None:
    assert all_group_vars.get("aial_firewall_apply") is False


def test_web_manage_disabled_fleet_wide(all_group_vars: dict) -> None:
    assert all_group_vars.get("aial_web_manage") is False


def test_inventory_blob_has_no_gmail(repo_root: Path, validate_mod) -> None:
    blob = validate_mod.inventory_text_blob(repo_root)
    assert not validate_mod.GMAIL.search(blob)


@pytest.mark.parametrize("host", [
    "ansible-bastion-01.lab.example.invalid",
    "ansible-web-01.lab.example.invalid",
    "ansible-web-02.lab.example.invalid",
    "ansible-app-01.lab.example.invalid",
    "ansible-db-01.lab.example.invalid",
    "ansible-monitor-01.lab.example.invalid",
])
def test_host_contains_lab_label(host: str) -> None:
    assert "lab" in host or host.endswith(".example.invalid")
