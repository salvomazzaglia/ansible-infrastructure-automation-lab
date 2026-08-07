"""Dependency manifest tests."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.deps


def test_requirements_yml_exists(repo_root: Path) -> None:
    assert (repo_root / "requirements.yml").is_file()


def test_requirements_yml_valid(repo_root: Path) -> None:
    data = yaml.safe_load((repo_root / "requirements.yml").read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert "collections" in data


def test_requirements_includes_community_docker(repo_root: Path) -> None:
    data = yaml.safe_load((repo_root / "requirements.yml").read_text(encoding="utf-8"))
    names = [c.get("name") for c in data.get("collections") or []]
    assert "community.docker" in names


def test_requirements_dev_exists(repo_root: Path) -> None:
    assert (repo_root / "requirements-dev.txt").is_file()


@pytest.mark.parametrize(
    "package",
    [
        "ansible-core",
        "ansible-lint",
        "yamllint",
        "pytest",
        "jsonschema",
        "PyYAML",
        "molecule",
    ],
)
def test_requirements_dev_lists_package(repo_root: Path, package: str) -> None:
    text = (repo_root / "requirements-dev.txt").read_text(encoding="utf-8")
    assert package in text


def test_galaxy_dependencies_empty_or_dict(galaxy: dict) -> None:
    deps = galaxy.get("dependencies", {})
    assert deps == {} or isinstance(deps, dict)


def test_pyproject_exists(repo_root: Path) -> None:
    assert (repo_root / "pyproject.toml").is_file()


def test_pyproject_has_pytest_config(repo_root: Path) -> None:
    text = (repo_root / "pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.pytest.ini_options]" in text
    assert 'testpaths = ["tests"]' in text or "testpaths" in text


def test_validate_repository_script_exists(repo_root: Path) -> None:
    assert (repo_root / "scripts" / "validate-repository.py").is_file()


def test_run_ci_script_exists(repo_root: Path) -> None:
    assert (repo_root / "scripts" / "run-ci.py").is_file()


def test_ansible_core_floor_in_dev_requirements(repo_root: Path) -> None:
    text = (repo_root / "requirements-dev.txt").read_text(encoding="utf-8")
    assert "2.20" in text


def test_community_docker_version_constraint(repo_root: Path) -> None:
    data = yaml.safe_load((repo_root / "requirements.yml").read_text(encoding="utf-8"))
    docker = next(c for c in data["collections"] if c["name"] == "community.docker")
    assert "version" in docker
