#!/usr/bin/env python3
"""Read-only real-browser smoke checks for public Blackthorn websites.

Never ignores invalid TLS certificates, submits forms, or changes site data.
Reports results and snapshots; does not equate a green runner with site acceptance.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

SITES = [
    ("Enterprises", "https://blackthorn.enterprises/"),
    ("Rootworks", "https://rootworks.technerd.tech/"),
    ("Corrine", "https://corrinejblackthorn.com/"),
    ("Field Notes", "https://blackthornfieldnotes.ink/"),
    ("TechNerd", "https://technerd.tech/"),
    ("Glass & Thorns", "https://glassandthorns.art/"),
    ("Glass Rose Collective", "https://cjblackthorn.github.io/glass-rose-collective/"),
    ("Petal & Frame", "https://petalsnframes.art/"),
    ("Thorns2Roses", "https://thorns2roses.com/"),
    ("Tropical Plants (known TLS failure)", "https://tropicals.blackthorn.enterprises/"),
]
VIEWPORTS = [("desktop", 1280, 800), ("mobile", 390, 844)]
ROOT = Path("browser-qa-results")
ROOT.mkdir(exist_ok=True)


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def check_site(browser, label: str, url: str, device: str, width: int, height: int) -> dict:
    result = {
        "site": label, "url": url, "viewport": device, "width": width,
        "status": "UNVERIFIED", "http_status": None, "final_url": None,
        "title": None, "h1_count": None, "main_count": None,
        "horizontal_overflow_px": None, "first_focus": None,
        "skip_links": None, "reduced_motion_matches": None,
        "page_errors": [], "issues": [],
    }
    ctx = browser.new_context(
        viewport={"width": width, "height": height},
        reduced_motion="reduce" if device == "mobile" else "no-preference",
        ignore_https_errors=False,
        java_script_enabled=True,
    )
    page = ctx.new_page()
    page_errors = []
    page.on("pageerror", lambda exc: page_errors.append(str(exc)[:200]))
    try:
        response = page.goto(url, wait_until="domcontentloaded", timeout=25000)
        if response is None:
            raise RuntimeError("No navigation response")
        result["http_status"] = response.status
        result["final_url"] = page.url
        page.wait_for_timeout(350)
        result["title"] = page.title()[:180]
        report = page.evaluate("""() => ({
            h1Count: document.querySelectorAll('h1').length,
            mainCount: document.querySelectorAll('main').length,
            overflow: Math.max(0, Math.round(document.documentElement.scrollWidth - window.innerWidth)),
            skipLinks: [...document.querySelectorAll('a[href^="#"]')].filter(a => /skip/i.test(a.textContent || '')).map(a => a.getAttribute('href')),
            motion: window.matchMedia('(prefers-reduced-motion: reduce)').matches
        })""")
        result.update(
            h1_count=report["h1Count"], main_count=report["mainCount"],
            horizontal_overflow_px=report["overflow"],
            skip_links=report["skipLinks"], reduced_motion_matches=report["motion"],
        )
        page.keyboard.press("Tab")
        result["first_focus"] = page.evaluate("""() => {
            const el = document.activeElement;
            if (!el || el === document.body) return '(none)';
            return (el.innerText || el.getAttribute('aria-label') || el.tagName || '').trim().slice(0, 100);
        }""")
        if not 200 <= response.status < 400:
            result["issues"].append(f"HTTP {response.status}")
        if not page.url.startswith("https://"):
            result["issues"].append("Insecure final navigation URL")
        if report["mainCount"] < 1:
            result["issues"].append("No main landmark")
        if report["h1Count"] < 1:
            result["issues"].append("No h1 heading")
        if report["overflow"] > 12:
            result["issues"].append(f"Horizontal overflow {report['overflow']}px")
        if len(page_errors) > 0:
            result["page_errors"] = page_errors[:3]
            result["issues"].append("Uncaught page JavaScript error")
        result["status"] = "FINDING" if result["issues"] else "PASS"
        if device == "mobile":
            page.screenshot(path=str(ROOT / (slug(label) + "-mobile.png")), full_page=False)
    except Exception as exc:
        detail = str(exc).splitlines()[0][:240]
        result["issues"].append(detail)
        if "CERT" in detail.upper() or "SSL" in detail.upper():
            result["status"] = "TLS_FAILED"
        else:
            result["status"] = "UNVERIFIED"
    finally:
        ctx.close()
    return result


def main():
    results = []
    with sync_playwright() as play:
        browser = play.chromium.launch(headless=True)
        try:
            for label, url in SITES:
                for device, width, height in VIEWPORTS:
                    value = check_site(browser, label, url, device, width, height)
                    results.append(value)
                    print(f"{value['site']}: {device}: {value['status']}: {', '.join(value['issues'])[:220]}")
        finally:
            browser.close()

    output = {"time_utc": datetime.now(timezone.utc).isoformat(), "results": results}
    (ROOT / "results.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    lines = [
        "## Blackthorn read-only browser smoke test",
        "",
        "This is a Chromium desktop/mobile source-of-evidence test, **not** a WCAG audit, performance score, approval, or proof all business functionality works.",
        "Browser enforces normal TLS and does not submit forms.",
        "",
        "| Site | Desktop | Mobile | Finding summary |",
        "| --- | --- | --- | --- |",
    ]
    for i in range(0, len(results), 2):
        desktop, mobile = results[i:i+2]
        issues = list(dict.fromkeys(desktop["issues"] + mobile["issues"]))
        summary = "; ".join(issues)[:155].replace("|", "/") or "No issues in checked assertions"
        lines.append(f"| {desktop['site']} | {desktop['status']} | {mobile['status']} | {summary} |")
    lines.extend(["", "Any findings require triage; see [remediation queue #4](https://github.com/cjblackthorn/blackthorn-enterprises/issues/4).", ""])
    markdown = "\n".join(lines)
    print(markdown)
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as handle:
            handle.write(markdown)
    findings = sum(item["status"] != "PASS" for item in results)
    print(f"Browser runs: {len(results)}, pass: {len(results)-findings}, triage: {findings}")
    # Monitor-style smoke job: preserve results even when known TLS or browser problems are detected.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
