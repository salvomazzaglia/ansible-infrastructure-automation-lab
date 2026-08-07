"""Shared pytest fixtures for ansible-infrastructure-automation-lab."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def validate_mod():
    """Import scripts/validate-repository.py as a module."""
    path = SCRIPTS / "validate-repository.py"
    spec = importlib.util.spec_from_file_location("validate_repository", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["validate_repository"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def galaxy(repo_root: Path) -> dict[str, Any]:
    return yaml.safe_load((repo_root / "galaxy.yml").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def runtime(repo_root: Path) -> dict[str, Any]:
    return yaml.safe_load((repo_root / "meta" / "runtime.yml").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def hosts_yml(repo_root: Path) -> dict[str, Any]:
    path = repo_root / "inventories" / "synthetic" / "hosts.yml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def all_group_vars(repo_root: Path) -> dict[str, Any]:
    path = repo_root / "inventories" / "synthetic" / "group_vars" / "all.yml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def expected_roles(validate_mod) -> tuple[str, ...]:
    return validate_mod.EXPECTED_ROLES


@pytest.fixture(scope="session")
def expected_playbooks(validate_mod) -> tuple[str, ...]:
    return validate_mod.EXPECTED_PLAYBOOKS


@pytest.fixture(scope="session")
def expected_hosts(validate_mod) -> tuple[str, ...]:
    return validate_mod.EXPECTED_HOSTS


@pytest.fixture(scope="session")
def callback_module(repo_root: Path):
    """Import the automation_report callback with or without ansible installed."""
    name = "automation_report_under_test"
    if name in sys.modules:
        return sys.modules[name]

    try:
        import ansible.plugins.callback  # noqa: F401
    except ImportError:
        ansible = ModuleType("ansible")
        plugins = ModuleType("ansible.plugins")
        callback = ModuleType("ansible.plugins.callback")

        class CallbackBase:  # minimal stub
            def __init__(self, *args, **kwargs):
                self._display = type("D", (), {"display": staticmethod(lambda *a, **k: None), "warning": staticmethod(lambda *a, **k: None)})()

        callback.CallbackBase = CallbackBase
        sys.modules["ansible"] = ansible
        sys.modules["ansible.plugins"] = plugins
        sys.modules["ansible.plugins.callback"] = callback

    path = repo_root / "plugins" / "callback" / "automation_report.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def text_files(repo_root: Path, validate_mod) -> list[Path]:
    return validate_mod.iter_text_files(repo_root)
