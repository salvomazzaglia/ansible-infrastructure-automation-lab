"""Sample report and schema validation tests."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

pytestmark = pytest.mark.reports

SAMPLE_JSON = [
    "sample-check-report.json",
    "sample-apply-report.json",
    "sample-idempotence-report.json",
    "sample-drift-report.json",
]


@pytest.mark.parametrize("filename", SAMPLE_JSON)
def test_sample_json_exists(repo_root: Path, filename: str) -> None:
    assert (repo_root / "examples" / filename).is_file()


@pytest.mark.parametrize("filename", SAMPLE_JSON)
def test_sample_json_valid(repo_root: Path, filename: str) -> None:
    path = repo_root / "examples" / filename
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)


@pytest.mark.parametrize(
    "filename",
    [
        "sample-check-report.json",
        "sample-apply-report.json",
        "sample-idempotence-report.json",
    ],
)
def test_automation_report_schema_validation(repo_root: Path, filename: str) -> None:
    schema = json.loads(
        (repo_root / "schemas" / "automation-report.schema.json").read_text(encoding="utf-8")
    )
    data = json.loads((repo_root / "examples" / filename).read_text(encoding="utf-8"))
    jsonschema.validate(instance=data, schema=schema)


def test_drift_report_schema_validation(repo_root: Path) -> None:
    schema = json.loads(
        (repo_root / "schemas" / "drift-report.schema.json").read_text(encoding="utf-8")
    )
    data = json.loads(
        (repo_root / "examples" / "sample-drift-report.json").read_text(encoding="utf-8")
    )
    jsonschema.validate(instance=data, schema=schema)


@pytest.mark.parametrize("filename", SAMPLE_JSON)
def test_sample_json_has_synthetic_banner(repo_root: Path, filename: str) -> None:
    data = json.loads((repo_root / "examples" / filename).read_text(encoding="utf-8"))
    assert data.get("banner") == "SYNTHETIC DEMONSTRATION DATA"


def test_html_contains_synthetic_banner(repo_root: Path) -> None:
    html = (repo_root / "examples" / "sample-automation-report.html").read_text(encoding="utf-8")
    assert "SYNTHETIC DEMONSTRATION DATA" in html


def test_html_exists(repo_root: Path) -> None:
    assert (repo_root / "examples" / "sample-automation-report.html").is_file()


def test_png_screenshot_exists(repo_root: Path) -> None:
    png = repo_root / "docs" / "images" / "sample-automation-report.png"
    assert png.is_file()
    assert png.stat().st_size > 0


@pytest.mark.parametrize("filename", SAMPLE_JSON)
def test_sample_hosts_use_example_invalid(repo_root: Path, filename: str) -> None:
    text = (repo_root / "examples" / filename).read_text(encoding="utf-8")
    data = json.loads(text)
    blob = json.dumps(data)
    assert "gmail.com" not in blob.lower()
    # hosts if present must be synthetic
    hosts = []
    if "inventory" in data and isinstance(data["inventory"], dict):
        hosts.extend(data["inventory"].get("hosts") or [])
    for finding in data.get("findings") or []:
        if isinstance(finding, dict) and "host" in finding:
            hosts.append(finding["host"])
    for host in hosts:
        assert str(host).endswith(".example.invalid")


@pytest.mark.parametrize(
    "needle",
    [
        "@" + "gmail.com",
        "password123",
        "BEGIN RSA PRIVATE " + "KEY",
        "BEGIN OPENSSH PRIVATE " + "KEY",
        "AKIA",  # AWS access key prefix
    ],
)
def test_reports_have_no_personal_or_secret_data(repo_root: Path, needle: str) -> None:
    for path in (repo_root / "examples").iterdir():
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".json", ".html", ".yml", ".yaml"}:
            continue
        text = path.read_text(encoding="utf-8")
        assert needle.lower() not in text.lower(), path.name


@pytest.mark.parametrize("filename", SAMPLE_JSON)
def test_sample_reports_mark_sanitized_or_check_mode(repo_root: Path, filename: str) -> None:
    data = json.loads((repo_root / "examples" / filename).read_text(encoding="utf-8"))
    assert data.get("sanitized") is True or data.get("check_mode") is True or data.get("schema") == "drift-report"


def test_automation_schema_requires_sanitized(repo_root: Path) -> None:
    schema = json.loads(
        (repo_root / "schemas" / "automation-report.schema.json").read_text(encoding="utf-8")
    )
    assert "sanitized" in schema.get("required", [])


def test_schemas_are_draft7(repo_root: Path) -> None:
    for name in ("automation-report.schema.json", "drift-report.schema.json"):
        schema = json.loads((repo_root / "schemas" / name).read_text(encoding="utf-8"))
        assert "draft-07" in schema.get("$schema", "")
