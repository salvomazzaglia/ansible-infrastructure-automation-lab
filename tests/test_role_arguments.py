"""Role argument_specs validation tests."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.roles

ROLES = [
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
]


@pytest.mark.parametrize("role", ROLES)
def test_argument_specs_file_exists(repo_root: Path, role: str) -> None:
    assert (repo_root / "roles" / role / "meta" / "argument_specs.yml").is_file()


@pytest.mark.parametrize("role", ROLES)
def test_argument_specs_yaml_valid(repo_root: Path, role: str) -> None:
    path = repo_root / "roles" / role / "meta" / "argument_specs.yml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert "argument_specs" in data
    assert "main" in data["argument_specs"]


@pytest.mark.parametrize("role", ROLES)
def test_argument_specs_main_has_options(repo_root: Path, role: str) -> None:
    path = repo_root / "roles" / role / "meta" / "argument_specs.yml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    options = data["argument_specs"]["main"].get("options")
    assert isinstance(options, dict)
    assert len(options) >= 1


@pytest.mark.parametrize("role", ROLES)
def test_every_top_level_option_has_type(repo_root: Path, role: str) -> None:
    path = repo_root / "roles" / role / "meta" / "argument_specs.yml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    options = data["argument_specs"]["main"]["options"]
    for name, option in options.items():
        assert isinstance(option, dict), name
        assert "type" in option, f"{role}.{name} missing type"


@pytest.mark.parametrize("role", ROLES)
def test_load_argument_specs_helper(validate_mod, role: str, repo_root: Path) -> None:
    specs = validate_mod.load_argument_specs(role, root=repo_root)
    assert "main" in specs


@pytest.mark.parametrize(
    "port",
    [0, -1, 65536, 99999, 70000, -22],
)
def test_invalid_ports_rejected_by_schema_logic(validate_mod, port: int) -> None:
    assert validate_mod.validate_port(port) is False


@pytest.mark.parametrize(
    "port",
    [1, 22, 80, 443, 8080, 65535],
)
def test_valid_ports_accepted_by_schema_logic(validate_mod, port: int) -> None:
    assert validate_mod.validate_port(port) is True


@pytest.mark.parametrize(
    "port",
    [0, -1, 65536, 99999],
)
def test_web_listen_port_option_rejects_invalid(validate_mod, repo_root: Path, port: int) -> None:
    specs = validate_mod.load_argument_specs("web_service", root=repo_root)
    option = specs["main"]["options"]["aial_web_listen_port"]
    assert validate_mod.port_option_accepts(option, port) is False


@pytest.mark.parametrize(
    "port",
    [0, -1, 65536],
)
def test_logging_remote_port_rejects_invalid(validate_mod, repo_root: Path, port: int) -> None:
    specs = validate_mod.load_argument_specs("logging", root=repo_root)
    option = specs["main"]["options"]["aial_logging_remote_port"]
    assert validate_mod.port_option_accepts(option, port) is False


@pytest.mark.parametrize(
    "protocol",
    ["http", "sctp", "all", "tcp/udp", "", "TCPP"],
)
def test_invalid_firewall_protocol_rejected(validate_mod, protocol: str) -> None:
    assert validate_mod.validate_firewall_protocol(protocol) is False


@pytest.mark.parametrize(
    "protocol",
    ["tcp", "udp", "icmp"],
)
def test_valid_firewall_protocol_accepted(validate_mod, protocol: str) -> None:
    assert validate_mod.validate_firewall_protocol(protocol) is True


def test_firewall_protocol_choices_in_argument_specs(validate_mod, repo_root: Path) -> None:
    option = validate_mod.find_firewall_protocol_option(root=repo_root)
    choices = {c.lower() for c in option.get("choices", [])}
    assert choices == {"tcp", "udp", "icmp"}


@pytest.mark.parametrize(
    "protocol",
    ["http", "sctp", "foo"],
)
def test_firewall_option_rejects_invalid_via_choices(validate_mod, repo_root: Path, protocol: str) -> None:
    option = validate_mod.find_firewall_protocol_option(root=repo_root)
    assert validate_mod.option_accepts_value(option, protocol) is False


@pytest.mark.parametrize(
    "env",
    ["production", "prod", "staging", "dev", "live", "", "SYNTHETIC"],
)
def test_invalid_environment_enum_rejected(validate_mod, env: str) -> None:
    assert validate_mod.validate_environment(env) is False


@pytest.mark.parametrize(
    "env",
    ["synthetic", "lab", "authorized", "molecule"],
)
def test_valid_environment_enum_accepted(validate_mod, env: str) -> None:
    assert validate_mod.validate_environment(env) is True


def test_preflight_documents_environment_enum(repo_root: Path, validate_mod) -> None:
    text = (repo_root / "playbooks" / "tasks" / "preflight.yml").read_text(encoding="utf-8")
    for env in validate_mod.ALLOWED_ENVIRONMENTS:
        assert env in text


def test_ssh_permit_root_login_choices_exclude_yes(validate_mod, repo_root: Path) -> None:
    specs = validate_mod.load_argument_specs("ssh_hardening", root=repo_root)
    option = specs["main"]["options"]["aial_ssh_permit_root_login"]
    choices = option.get("choices") or []
    assert "yes" not in choices
    assert validate_mod.option_accepts_value(option, "yes") is False


def test_ssh_permit_root_login_accepts_prohibit_password(validate_mod, repo_root: Path) -> None:
    specs = validate_mod.load_argument_specs("ssh_hardening", root=repo_root)
    option = specs["main"]["options"]["aial_ssh_permit_root_login"]
    assert validate_mod.option_accepts_value(option, "prohibit-password") is True


def test_find_port_options_nonempty(validate_mod, repo_root: Path) -> None:
    found = validate_mod.find_port_options(root=repo_root)
    assert len(found) >= 2
    names = {name for _, name, _ in found}
    assert any("listen_port" in n or "remote_port" in n for n in names)


@pytest.mark.parametrize("role", ROLES)
def test_iter_option_specs_yields_typed_entries(validate_mod, role: str, repo_root: Path) -> None:
    specs = validate_mod.load_argument_specs(role, root=repo_root)
    options = list(validate_mod.iter_option_specs(specs))
    assert options
    for name, option in options:
        assert "type" in option, name


def test_bool_option_rejects_string(validate_mod, repo_root: Path) -> None:
    specs = validate_mod.load_argument_specs("ssh_hardening", root=repo_root)
    option = specs["main"]["options"]["aial_ssh_password_authentication"]
    assert validate_mod.option_accepts_value(option, "yes") is False
    assert validate_mod.option_accepts_value(option, False) is True


def test_web_pool_state_choices(validate_mod, repo_root: Path) -> None:
    specs = validate_mod.load_argument_specs("web_service", root=repo_root)
    option = specs["main"]["options"]["aial_web_pool_member_state"]
    assert validate_mod.option_accepts_value(option, "draining") is True
    assert validate_mod.option_accepts_value(option, "bogus") is False
