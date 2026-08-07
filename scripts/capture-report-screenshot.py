#!/usr/bin/env python3
"""Capture docs/images/sample-automation-report.png from the synthetic HTML report.

Prefer Playwright when available; otherwise render a professional PNG summary with
Pillow. Verifies SYNTHETIC DEMONSTRATION DATA before capture.

No browser profile persistence, no remote assets, no user data.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "examples" / "sample-automation-report.html"
OUT_PATH = ROOT / "docs" / "images" / "sample-automation-report.png"
MARKER = "SYNTHETIC DEMONSTRATION DATA"
WIDTH = 1440
HEIGHT = 1000


def _require_marker(html_text: str) -> None:
    if MARKER not in html_text:
        raise SystemExit(
            f"Refusing capture: {HTML_PATH.as_posix()} missing marker {MARKER!r}"
        )


def _validate_png(path: Path) -> None:
    data = path.read_bytes()
    if len(data) < 8 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"{path.name}: not a valid PNG")
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if abs(width - WIDTH) > 80 or abs(height - HEIGHT) > 80:
        raise SystemExit(f"{path.name}: unexpected dimensions {width}x{height}")
    if len(data) < 20_000:
        raise SystemExit(f"{path.name}: file too small ({len(data)} bytes)")


def _capture_playwright(html_path: Path, out_path: Path) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False

    uri = html_path.resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Ephemeral context — no persistent profile / user data dir.
        context = browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT},
            device_scale_factor=1,
            java_script_enabled=True,
            offline=True,
        )
        page = context.new_page()
        page.goto(uri, wait_until="load")
        content = page.content()
        _require_marker(content)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(out_path), full_page=False)
        context.close()
        browser.close()
    return True


def _capture_pillow(html_text: str, out_path: Path) -> None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise SystemExit(
            "Neither playwright nor Pillow is available. "
            "Install one of: pip install playwright pillow"
        ) from exc

    _require_marker(html_text)

    img = Image.new("RGB", (WIDTH, HEIGHT), "#eef3f7")
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arial.ttf", 36)
        head_font = ImageFont.truetype("arial.ttf", 20)
        body_font = ImageFont.truetype("arial.ttf", 16)
        small_font = ImageFont.truetype("arial.ttf", 13)
    except OSError:
        title_font = ImageFont.load_default()
        head_font = title_font
        body_font = title_font
        small_font = title_font

    # Soft background wash
    draw.rectangle((0, 0, WIDTH, 180), fill="#ffffff")
    draw.rectangle((0, 180, WIDTH, 181), fill="#d5dde5")

    # Banner
    draw.rectangle((40, 28, 420, 58), fill="#7a1f1f")
    draw.text((52, 34), MARKER, fill="#ffffff", font=small_font)

    draw.text((40, 72), "Ansible Infrastructure Automation Lab", fill="#15202b", font=title_font)
    draw.text(
        (40, 122),
        "Synthetic automation report summary · sanitized metadata only",
        fill="#5b6b7c",
        font=body_font,
    )

    # Stats cards
    stats = [
        ("Hosts", "6"),
        ("Changed", "3"),
        ("Unchanged", "2"),
        ("Failed", "0"),
        ("Skipped", "1"),
        ("Check changes", "2"),
    ]
    card_w = 200
    gap = 16
    x0 = 40
    y0 = 210
    for i, (label, value) in enumerate(stats):
        x = x0 + (i % 3) * (card_w + gap)
        y = y0 + (i // 3) * 110
        draw.rectangle((x, y, x + card_w, y + 92), fill="#ffffff", outline="#d5dde5")
        draw.rectangle((x, y, x + 6, y + 92), fill="#0f6a5c")
        draw.text((x + 18, y + 16), label.upper(), fill="#5b6b7c", font=small_font)
        draw.text((x + 18, y + 40), value, fill="#15202b", font=title_font)

    # Sections
    sections = [
        (
            "Inventory / roles",
            "Groups: web, app, database, monitoring, bastion\n"
            "Hosts: web01/web02/app01/db01/mon01/bastion01.lab.example.invalid\n"
            "Roles: common → service_health (10 roles)",
        ),
        (
            "Check-mode / idempotence / drift",
            "Check-mode: 2 proposed changes, 3 compliant, 1 skipped\n"
            "Idempotence: second run changed=0 (passed)\n"
            "Drift: compliant, change_required, unavailable, failed, skipped",
        ),
        (
            "Security controls",
            "no_log → REDACTED only · no vault/password/SSH key capture\n"
            "Runtime reports under reports/ (AIAL_REPORT_DIR) · gitignored\n"
            "Vault placeholders only in examples/vault.example.yml",
        ),
        (
            "Limitations",
            "SYNTHETIC DEMONSTRATION DATA — not real infrastructure\n"
            ".example.invalid aliases only · no RFC1918 · no ansible_host\n"
            "Not an Ansible Automation Platform certification artifact",
        ),
    ]

    y = 450
    for title, body in sections:
        draw.rectangle((40, y, WIDTH - 40, y + 118), fill="#ffffff", outline="#d5dde5")
        draw.text((56, y + 14), title.upper(), fill="#0f6a5c", font=head_font)
        draw.multiline_text((56, y + 44), body, fill="#15202b", font=body_font, spacing=4)
        y += 130

    draw.text(
        (40, HEIGHT - 36),
        "salvomazzaglia/ansible-infrastructure-automation-lab · portfolio screenshot",
        fill="#5b6b7c",
        font=small_font,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="PNG", optimize=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force-pillow",
        action="store_true",
        help="Skip Playwright and render with Pillow.",
    )
    args = parser.parse_args()

    if not HTML_PATH.is_file():
        raise SystemExit(
            f"Missing {HTML_PATH.as_posix()}. Run scripts/generate-sample-reports.py first."
        )

    html_text = HTML_PATH.read_text(encoding="utf-8")
    _require_marker(html_text)

    used = "pillow"
    if not args.force_pillow and _capture_playwright(HTML_PATH, OUT_PATH):
        used = "playwright"
    else:
        _capture_pillow(html_text, OUT_PATH)

    _validate_png(OUT_PATH)
    rel = OUT_PATH.relative_to(ROOT).as_posix()
    size = OUT_PATH.stat().st_size
    print(f"wrote {rel} ({size} bytes) via {used}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
