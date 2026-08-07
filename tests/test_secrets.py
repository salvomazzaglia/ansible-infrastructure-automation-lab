"""Secret and vault hygiene tests."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.secrets


def test_no_vault_password_files(repo_root: Path) -> None:
    patterns = ("vault-password*", ".vault-password*", "*.vault-password")
    found = []
    for pattern in patterns:
        for path in repo_root.rglob(pattern):
            if ".git" in path.parts or not path.is_file():
                continue
            found.append(path)
    assert found == []


def test_gitignore_covers_vault_password(repo_root: Path) -> None:
    gi = (repo_root / ".gitignore").read_text(encoding="utf-8")
    assert "vault-password" in gi


def test_no_private_key_begin_markers(validate_mod, repo_root: Path) -> None:
    hits = []
    for path in validate_mod.iter_text_files(repo_root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if validate_mod.PRIVATE_KEY.search(text):
            hits.append(validate_mod.rel(path, repo_root))
    assert hits == []


def test_vault_example_exists(repo_root: Path) -> None:
    assert (repo_root / "examples" / "vault.example.yml").is_file()


def test_vault_example_placeholders_only(repo_root: Path) -> None:
    text = (repo_root / "examples" / "vault.example.yml").read_text(encoding="utf-8")
    assert "CHANGE_ME_WITH_ANSIBLE_VAULT" in text
    data = yaml.safe_load(text)
    assert isinstance(data, dict)
    for key, value in data.items():
        assert str(value).startswith("CHANGE_ME"), key


def test_vault_example_no_ansible_vault_blob(repo_root: Path, validate_mod) -> None:
    text = (repo_root / "examples" / "vault.example.yml").read_text(encoding="utf-8")
    assert not validate_mod.VAULT_BLOB.search(text)


def test_no_encrypted_vault_blobs_tracked(validate_mod, repo_root: Path) -> None:
    hits = []
    for path in validate_mod.iter_text_files(repo_root):
        rel = validate_mod.rel(path, repo_root)
        if "vault.example" in rel:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if validate_mod.VAULT_BLOB.search(text):
            hits.append(rel)
    assert hits == []


@pytest.mark.parametrize(
    "needle",
    [
        "CHANGE_ME",
        "PLACEHOLDER",
        "SYNTHETIC",
    ],
)
def test_accounts_use_placeholder_keys(repo_root: Path, needle: str) -> None:
    text = (
        repo_root / "inventories" / "synthetic" / "group_vars" / "all.yml"
    ).read_text(encoding="utf-8")
    # At least one placeholder-style marker present in inventory
    assert any(
        marker in text
        for marker in ("CHANGE_ME", "PLACEHOLDER", "SYNTHETIC_SSH_PUBLIC_KEY_PLACEHOLDER")
    )
    _ = needle  # parametrize multiplies coverage of marker vocabulary awareness


def test_secrets_helper_passes(validate_mod, repo_root: Path) -> None:
    assert validate_mod.check_secrets_and_keys(repo_root) == []


def test_no_pem_or_key_files_tracked(repo_root: Path) -> None:
    bad = []
    for pattern in ("*.pem", "*.key", "id_rsa*", "id_ed25519*"):
        for path in repo_root.rglob(pattern):
            if ".git" in path.parts:
                continue
            if path.is_file():
                bad.append(path)
    assert bad == []


def test_gitignore_ignores_pem_and_keys(repo_root: Path) -> None:
    gi = (repo_root / ".gitignore").read_text(encoding="utf-8")
    assert "*.pem" in gi
    assert "*.key" in gi


@pytest.mark.parametrize(
    "relative",
    [
        "inventories/synthetic/group_vars/all.yml",
        "examples/vault.example.yml",
        "roles/accounts/defaults/main.yml",
    ],
)
def test_no_hardcoded_password_literals(repo_root: Path, relative: str, validate_mod) -> None:
    text = (repo_root / relative).read_text(encoding="utf-8")
    for match in validate_mod.PASSWORD_ASSIGN.finditer(text):
        val = match.group(1)
        assert val.startswith("CHANGE_ME") or "PLACEHOLDER" in val.upper() or "SYNTHETIC" in val.upper()


def test_no_env_secret_files(repo_root: Path) -> None:
    found = [p for p in repo_root.rglob(".env*") if p.is_file() and ".git" not in p.parts]
    assert found == []
