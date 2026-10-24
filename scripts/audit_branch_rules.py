#!/usr/bin/env python3
"""Read-only GitHub branch protection status inventory. Never modifies rules."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json
import os

REPOS = (
    "blackthorn-enterprises",
    "blackthorn-rootworks",
    "blackthorn-tropicals",
    "corrine-j-blackthorn",
    "cjblackthorn.github.io",
    "technerd",
    "glass-and-thorns",
    "glass-rose-collective",
    "petals-and-frames",
    "thorns2roses",
)

def inspect(repo):
    url=f"https://api.github.com/repos/cjblackthorn/{repo}/branches/main"
    headers={"Accept":"application/vnd.github+json",
             "User-Agent":"blackthorn-readonly-branch-audit",
             "X-GitHub-Api-Version":"2022-11-28"}
    if os.environ.get("GH_TOKEN"):
        headers["Authorization"]="Bearer "+os.environ["GH_TOKEN"]
    try:
        with urlopen(Request(url, headers=headers), timeout=15) as response:
            data=json.load(response)
        state=data.get("protected")
        if not isinstance(state,bool):
            return {"repo":repo,"state":"UNVERIFIED","reason":"No protection boolean returned"}
        return {"repo":repo,"state":"PROTECTED" if state else "NOT_PROTECTED"}
    except (HTTPError,URLError,TimeoutError,ValueError,OSError) as exc:
        # Do not assert unprotected if GitHub access failed.
        return {"repo":repo,"state":"UNVERIFIED","reason":type(exc).__name__}

def main():
    rows=[inspect(repo) for repo in REPOS]
    Path("branch-protection-audit.json").write_text(
        json.dumps({"checked_at_utc":datetime.now(timezone.utc).isoformat(),
                    "results":rows},indent=2)+"\n",encoding="utf-8")
    counts={name:sum(x["state"]==name for x in rows)
            for name in ("PROTECTED","NOT_PROTECTED","UNVERIFIED")}
    text=["## Public website branch-release gate status",
          "",
          "Read-only GitHub branch metadata. `protected=true` means at least one protection mechanism applies; it **does not prove** appropriate required checks, reviewers, bypass restrictions or an effective emergency revert process.",
          "",
          "| Repository | GitHub `main.protected` |",
          "| --- | --- |"]
    for r in rows:
        text.append(f"| `cjblackthorn/{r['repo']}` | {r['state']} |")
    text.extend(["",f"Protected: **{counts['PROTECTED']}/10** · Not protected: **{counts['NOT_PROTECTED']}** · Unverified: **{counts['UNVERIFIED']}**.",
                 "", "Final acceptance requires an administrator to inspect the actual rulesets/branch protection settings and test required check behavior. See [issue #18](https://github.com/cjblackthorn/blackthorn-enterprises/issues/18)."])
    report="\n".join(text)+"\n"
    print(report)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf-8") as file:
            file.write(report)
    # Observation-only; pending admin action is not a CI infra failure.
    return 0

if __name__=="__main__":
    raise SystemExit(main())
