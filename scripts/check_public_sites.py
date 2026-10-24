#!/usr/bin/env python3
"""Read-only HTTPS/asset verification of published Blackthorn properties.

Uses normal OS certificate verification. Never falls back to insecure HTTP/TLS.
Source tests and GitHub Actions deploy success do not replace these live checks.
"""
from __future__ import annotations

import concurrent.futures
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

CHECKS = [
    ("Blackthorn Enterprises", "https://blackthorn.enterprises/", "html"),
    ("Blackthorn Rootworks", "https://rootworks.technerd.tech/", "html"),
    ("Tropical Plants (known TLS issue)", "https://tropicals.blackthorn.enterprises/", "html"),
    ("Corrine personal site", "https://corrinejblackthorn.com/", "html"),
    ("Corrine resume PDF", "https://corrinejblackthorn.com/resume/Corrine-J-Blackthorn-Resume.pdf", "pdf"),
    ("Field Notes", "https://blackthornfieldnotes.ink/", "html"),
    ("TechNerd", "https://technerd.tech/", "html"),
    ("Glass & Thorns", "https://glassandthorns.art/", "html"),
    ("Glass & Thorns lyrics", "https://glassandthorns.art/lyrics/", "html"),
    ("Glass & Thorns sitemap", "https://glassandthorns.art/sitemap.xml", "sitemap"),
    ("Glass Rose Collective", "https://cjblackthorn.github.io/glass-rose-collective/", "html"),
    ("Petal & Frame", "https://petalsnframes.art/", "html"),
    ("Petal & Frame sitemap", "https://petalsnframes.art/sitemap.xml", "sitemap"),
    ("Thorns2Roses", "https://thorns2roses.com/", "html"),
    ("Thorns2Roses privacy policy", "https://thorns2roses.com/privacy.html", "html"),
    ("Rootworks sitemap", "https://rootworks.technerd.tech/sitemap.xml", "sitemap"),
]

def probe(item):
    label, url, kind = item
    result = {"site": label, "url": url, "kind": kind, "status": "UNVERIFIED", "detail": "", "http_status": None, "final_url": None}
    try:
        req = Request(url, headers={"User-Agent": "Blackthorn-site-audit/1.0 (+GitHub Actions)", "Accept": "*/*"})
        with urlopen(req, timeout=18) as response:
            final = response.geturl()
            body = response.read(100_000)
            ctype = response.headers.get("content-type", "").lower()
            code = response.status
        result.update(http_status=code, final_url=final)
        if not final.startswith("https://"):
            result["status"], result["detail"] = "INSECURE_REDIRECT", "Final URL is not HTTPS"
        elif not (200 <= code < 300):
            result["status"], result["detail"] = "HTTP_ERROR", f"HTTP {code}"
        elif kind == "pdf" and (not body.startswith(b"%PDF") or "pdf" not in ctype):
            result["status"], result["detail"] = "CONTENT_MISMATCH", f"Expected PDF bytes and MIME; got {ctype}"
        elif kind == "html" and b"<html" not in body.lower():
            result["status"], result["detail"] = "CONTENT_MISMATCH", f"Expected HTML; got {ctype}"
        elif kind == "sitemap" and not (b"<urlset" in body and b"<loc>" in body):
            result["status"], result["detail"] = "CONTENT_MISMATCH", "Expected XML sitemap with URL entries"
        else:
            result["status"], result["detail"] = "PASS", f"HTTP {code}; type {ctype or 'unspecified'}"
    except HTTPError as exc:
        result["status"], result["detail"], result["http_status"] = "HTTP_ERROR", f"HTTP {exc.code}", exc.code
    except (URLError, TimeoutError, OSError) as exc:
        reason = str(getattr(exc, "reason", exc))
        result["status"] = "TLS_FAILED" if ("certificate" in reason.lower() or "ssl:" in reason.lower()) else "NETWORK_UNVERIFIED"
        result["detail"] = reason[:350]
    return result

def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(probe, CHECKS))
    output = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "results": results}
    Path("site-health-results.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    lines = [
        "## Blackthorn public-site verification (read-only)",
        "",
        "All checks use normal TLS certificate validation. A failed probe can indicate a site issue **or** a runner/network limitation; investigate before claiming an outage.",
        "",
        "| Site / resource | Result | Detail |",
        "| --- | --- | --- |"
    ]
    for entry in results:
        label = entry["site"].replace("|", "/")
        detail = entry["detail"].replace("|", "/").replace("\n", " ")[:160]
        lines.append(f'| {label} | {entry["status"]} | {detail} |')
        if entry["status"] != "PASS":
            print(f'::warning title=Public verification - {label}::{entry["status"]}: {detail}')
    lines.extend([
        "",
        "Unverified or failing entries must be triaged in the [final remediation queue](https://github.com/cjblackthorn/blackthorn-enterprises/issues/4).",
        "Tropical Plants certificate mismatch is already documented in [issue #14](https://github.com/cjblackthorn/blackthorn-tropicals/issues/14).",
        "This is not an interactive browser, content, security-header, or WCAG audit.",
        ""
    ])
    markdown = "\n".join(lines)
    print(markdown)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as stream:
            stream.write(markdown + "\n")
    print(f'\nChecks: {len(results)}, verified: {sum(x["status"] == "PASS" for x in results)}, needs triage: {sum(x["status"] != "PASS" for x in results)}')
    # Network observations must not prevent unrelated website code merges.
    # Critical TLS findings still require tracked, immediate remediation.
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
