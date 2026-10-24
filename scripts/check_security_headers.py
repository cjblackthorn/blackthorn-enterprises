#!/usr/bin/env python3
"""Observe production response security headers across public Blackthorn sites.

Read only, normal TLS verification, no cookies/login/forms. An absent header is
an observation, not proof of vulnerability: GitHub Pages may not allow custom
response headers, and security policy depends on the app's actual threat model.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json
import os

URLS = [
    ("Blackthorn Enterprises", "https://blackthorn.enterprises/"),
    ("Blackthorn Rootworks", "https://rootworks.technerd.tech/"),
    ("Tropical Plants", "https://tropicals.blackthorn.enterprises/"),
    ("Corrine personal", "https://corrinejblackthorn.com/"),
    ("Field Notes", "https://blackthornfieldnotes.ink/"),
    ("TechNerd", "https://technerd.tech/"),
    ("Glass & Thorns", "https://glassandthorns.art/"),
    ("Glass Rose Collective", "https://cjblackthorn.github.io/glass-rose-collective/"),
    ("Petal & Frame", "https://petalsnframes.art/"),
    ("Thorns2Roses", "https://thorns2roses.com/"),
]

HEADERS = [
    "strict-transport-security",
    "content-security-policy",
    "x-content-type-options",
    "referrer-policy",
    "permissions-policy",
    "x-frame-options",
    "cross-origin-opener-policy",
    "cache-control",
    "content-type",
]

def probe(item):
    name, url = item
    out = {"site": name, "url": url, "status": "UNVERIFIED", "http_status": None,
           "final_url": None, "observed_headers": {}, "notes": []}
    try:
        # A GET is used to reflect real navigation headers; only 1 byte is read.
        req = Request(url, headers={"User-Agent": "Blackthorn-header-audit/1.0", "Accept": "text/html"})
        with urlopen(req, timeout=18) as response:
            actual = response.geturl()
            out.update(http_status=response.status, final_url=actual,
                       observed_headers={k:response.headers.get(k) for k in HEADERS})
            response.read(1)
        if not actual.startswith("https://"):
            out["status"] = "INSECURE_FINAL_URL"
        elif not (200 <= out["http_status"] < 300):
            out["status"] = "HTTP_ERROR"
        else:
            out["status"] = "OBSERVED"
        headers = out["observed_headers"]
        if not headers["strict-transport-security"]:
            out["notes"].append("HSTS not observed")
        if not headers["content-security-policy"]:
            out["notes"].append("CSP not observed")
        if not headers["x-content-type-options"]:
            out["notes"].append("X-Content-Type-Options not observed")
        if not headers["referrer-policy"]:
            out["notes"].append("Referrer-Policy not observed")
        if not (headers["x-frame-options"] or
                "frame-ancestors" in (headers["content-security-policy"] or "").lower()):
            out["notes"].append("Framing restriction not observed")
    except HTTPError as e:
        out.update(status="HTTP_ERROR", http_status=e.code, notes=[f"HTTP {e.code}"])
    except (URLError, TimeoutError, OSError) as e:
        out.update(status="UNVERIFIED", notes=[str(getattr(e, "reason", e))[:220]])
    return out

def main():
    with ThreadPoolExecutor(max_workers=5) as pool:
        results=list(pool.map(probe, URLS))
    Path("header-audit-results.json").write_text(
        json.dumps({"checked_at_utc":datetime.now(timezone.utc).isoformat(),
                    "results":results}, indent=2)+"\n", encoding="utf-8")
    rows=["## Public website security-header baseline", "",
          "Read-only response observation with strict TLS. **Missing headers do not automatically mean a security vulnerability.** Some GitHub Pages/custom-domain deployments cannot set arbitrary HTTP headers; any remediation must respect the actual hosting platform and business functionality.",
          "", "| Site | Connection | HSTS | CSP | nosniff | Referrer | Frame restriction |",
          "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in results:
        h=r["observed_headers"]
        if r["status"]!="OBSERVED":
            cells=[r["site"],r["status"]]+["unverified"]*5
        else:
            cells=[r["site"],"Verified HTTPS",
                   "yes" if h.get("strict-transport-security") else "no",
                   "yes" if h.get("content-security-policy") else "no",
                   "yes" if h.get("x-content-type-options") else "no",
                   "yes" if h.get("referrer-policy") else "no",
                   "yes" if h.get("x-frame-options") or
                     "frame-ancestors" in (h.get("content-security-policy") or "").lower() else "no"]
        rows.append("| "+" | ".join(c.replace("|","/") for c in cells)+" |")
    rows.extend(["", "Do not recommend a CSP, HSTS change or proxy migration until deployed hosting, third-party scripts/forms, and redirect behavior have been reviewed. Full JSON with header values is retained in this workflow's artifact for triage.",
                 "", f"Verified observations: {sum(r['status']=='OBSERVED' for r in results)}/{len(results)}.",
                 "Issues requiring remediation belong in [final queue #4](https://github.com/cjblackthorn/blackthorn-enterprises/issues/4)."])
    md="\n".join(rows)
    print(md)
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf-8") as fp:fp.write(md+"\n")
    return 0  # A measurement run must not block unrelated site changes.

if __name__=="__main__":raise SystemExit(main())
