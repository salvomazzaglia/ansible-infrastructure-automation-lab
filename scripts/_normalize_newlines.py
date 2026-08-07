#!/usr/bin/env python3
"""Normalize YAML document starts and CRLF -> LF."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent if False else Path(".")
# When run from repo root:
ROOT = Path.cwd()

TEXT_SUFFIXES = {".yml", ".yaml", ".py", ".md", ".j2", ".json", ".cfg", ".txt", ".sh", ".html"}
TEXT_NAMES = {
    ".ansible-lint",
    ".yamllint",
    ".editorconfig",
    ".gitattributes",
    ".gitignore",
    "LICENSE",
    "VERSION",
}

GITHUB_YMLS = [
    ROOT / ".github/dependabot.yml",
    ROOT / ".github/ISSUE_TEMPLATE/bug_report.yml",
    ROOT / ".github/ISSUE_TEMPLATE/feature_request.yml",
    ROOT / ".github/workflows/ci.yml",
]

for path in GITHUB_YMLS:
    if not path.is_file():
        print("missing", path)
        continue
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if not text.startswith("---"):
        text = "---\n" + text
        print("added document-start", path)
    path.write_text(text, encoding="utf-8", newline="\n")

for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    if any(p in {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules"} for p in path.parts):
        continue
    if path.suffix not in TEXT_SUFFIXES and path.name not in TEXT_NAMES:
        continue
    data = path.read_bytes()
    if b"\r\n" in data or (b"\r" in data and b"\n" in data):
        path.write_bytes(data.replace(b"\r\n", b"\n").replace(b"\r", b"\n"))
        print("normalized newlines", path)

print("done")
