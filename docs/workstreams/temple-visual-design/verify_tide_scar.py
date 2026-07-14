"""Targeted Playwright evidence for the standalone Tide Scar visual prototype."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from playwright.sync_api import ConsoleMessage, sync_playwright

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "mockups"
STATE_EXPECTED = {
    "normal-run": {"score": 1280, "distance": 186, "shards": 7, "flow": 1, "chaseGap": 5.7, "obstacle": "beam"},
    "close-chase": {"score": 1484, "distance": 242, "shards": 8, "flow": 1, "chaseGap": 1.35, "obstacle": "ring"},
    "milestone": {"score": 5101, "distance": 250, "shards": 1, "flow": 2, "chaseGap": 4.2, "obstacle": "column"},
    "paused": {"score": 1484, "distance": 242, "shards": 8, "flow": 1, "chaseGap": 1.35, "obstacle": "gap"},
}


def inside(rect: dict, width: int, height: int) -> bool:
    return rect["left"] >= 0 and rect["top"] >= 0 and rect["right"] <= width and rect["bottom"] <= height


def capture(page, label: str, state: str | None, obstacle: str | None, width: int, height: int) -> dict:
    if state:
        page.evaluate("state => window.__tideScarSetState(state)", state)
    if obstacle:
        page.evaluate("obstacle => window.__tideScarSetObstacle(obstacle)", obstacle)
    page.wait_for_timeout(220 if state == "milestone" else 90)
    diagnostics = page.evaluate("window.__tideScarDiagnostics()")
    expected = dict(STATE_EXPECTED[state]) if state else {}
    if obstacle:
        expected["obstacle"] = obstacle
    actual = diagnostics["mockState"]
    for key, value in expected.items():
        assert actual[key] == value, f"{label}: {key} is {actual[key]!r}, expected {value!r}"
    assert diagnostics["canvasCount"] == 1 and diagnostics["gameplayDomEntities"] == 0
    assert diagnostics["overflowX"] == 0
    assert all(inside(rect, width, height) for rect in diagnostics["hud"]), f"{label}: HUD escaped viewport"
    assert diagnostics["runner"]["area"] > 0 and diagnostics["pursuer"]["area"] > 0
    assert diagnostics["pursuerGapPx"] >= 6, f"{label}: pursuer gap is {diagnostics['pursuerGapPx']}px"
    assert diagnostics["obstacle"]["bounds"]["area"] > 0
    assert diagnostics["contrast"]["hudOnSky"] >= 4.5
    assert diagnostics["contrast"]["coralOnSand"] >= 3
    assert page.locator("#score").text_content() == f"{actual['score']:,}"
    assert page.locator("#distance").text_content() == str(actual["distance"])
    assert page.locator("#flow").text_content() == f"×{actual['flow']}"
    assert page.locator("#shards").text_content() == str(actual["shards"])
    shot = OUT / f"{label}.png"
    page.screenshot(path=str(shot), full_page=True)
    diagnostics["screenshot"] = shot.name
    diagnostics["sha256"] = hashlib.sha256(shot.read_bytes()).hexdigest()
    return diagnostics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    records, problems = [], []
    scenarios = [
        ("mobile-normal", "normal-run", "beam", 390, 844),
        ("mobile-close-chase", "close-chase", "ring", 390, 844),
        ("mobile-milestone", "milestone", "column", 390, 844),
        ("desktop-run", "normal-run", "beam", 1440, 900),
        ("desktop-beam", "normal-run", "beam", 1440, 900),
        ("desktop-ring", "normal-run", "ring", 1440, 900),
        ("desktop-column", "normal-run", "column", 1440, 900),
        ("desktop-gap", "normal-run", "gap", 1440, 900),
        ("desktop-paused", "paused", "gap", 1440, 900),
        ("mobile-landscape", "normal-run", "column", 844, 390),
    ]
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        for label, state, obstacle, width, height in scenarios:
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
            page.on("console", lambda msg: problems.append(f"{label}: {msg.type}: {msg.text}") if msg.type == "error" else None)
            page.on("pageerror", lambda exc: problems.append(f"{label}: pageerror: {exc}"))
            page.goto(f"{args.base_url}/tide-scar-prototype.html?capture=1", wait_until="networkidle")
            records.append(capture(page, label, state, obstacle, width, height))
            page.close()
        reduced = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1, reduced_motion="reduce")
        reduced.on("console", lambda msg: problems.append(f"reduced: {msg.type}: {msg.text}") if msg.type == "error" else None)
        reduced.on("pageerror", lambda exc: problems.append(f"reduced: pageerror: {exc}"))
        reduced.goto(f"{args.base_url}/tide-scar-prototype.html?capture=1", wait_until="networkidle")
        reduced_record = capture(reduced, "mobile-reduced-motion", "normal-run", "beam", 390, 844)
        assert reduced_record["reducedMotion"] is True
        records.append(reduced_record)
        reduced.close()
        interaction = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
        interaction.on("console", lambda msg: problems.append(f"interaction: {msg.type}: {msg.text}") if msg.type == "error" else None)
        interaction.on("pageerror", lambda exc: problems.append(f"interaction: pageerror: {exc}"))
        interaction.goto(f"{args.base_url}/tide-scar-prototype.html", wait_until="networkidle")
        interaction.get_by_role("button", name="Chase", exact=True).click()
        interaction.get_by_role("button", name="Gap", exact=True).click()
        interaction_state = interaction.evaluate("window.__tideScarDiagnostics()")
        assert interaction_state["state"] == "close-chase" and interaction_state["obstacle"]["kind"] == "gap"
        interaction.close()
        browser.close()
    assert not problems, "\n".join(problems)
    summary = {"baseUrl": args.base_url, "records": records, "consoleProblems": problems}
    (ROOT / "prototype-acceptance.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"verified {len(records)} captures")


if __name__ == "__main__":
    main()
