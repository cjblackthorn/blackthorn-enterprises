# Website portfolio security: private secret triage and release controls

**Status (October 24, 2026):** The read-only Gitleaks history audit has been exercised across ten public website repos. One repository requires private investigation. Public workflows intentionally show only pass/fail, not findings, credentials, exact file paths or matched text. A clean scan is limited to the scanner's configured signatures and available Git history; it is not a guarantee that no secrets were ever exposed.

## Review a potential historical secret **privately**

1. On a trusted personal/admin machine with Docker and Git installed, clone the relevant repo to a **private local working directory**, not a public CI fork or shared drive. Example: `git clone https://github.com/cjblackthorn/<repo>.git`. Then `cd <repo>` and run `git fetch --all --tags`. Do not paste secrets or raw scanner reports into public issues, PRs, this chat, or automated notifications.
2. Create a private report directory outside the checkout: `mkdir -p "$HOME/.blackthorn-security"` and `chmod 700 "$HOME/.blackthorn-security"`.
3. Scan with the same pinned scanner version; replace `<repo>` with the actual local checkout name:

```bash
cd /path/to/your/local/repository
docker run --rm \
  -v "$PWD:/repo:ro" \
  -v "$HOME/.blackthorn-security:/out" \
  ghcr.io/gitleaks/gitleaks:v8.30.1 \
  git /repo --no-banner --redact=100 --log-level warn \
  --report-format json --report-path /out/private-gitleaks-report.json
chmod 600 "$HOME/.blackthorn-security/private-gitleaks-report.json"
```

An exit status of `1` indicates findings; other failures may mean scanning was incomplete. The JSON file is for authorized local security review only. It may contain paths, commit metadata and contextual match information. Inspect any matches against your own local source without sharing their content publicly.

4. For each finding, distinguish an **active credential** from a placeholder/test fixture or false positive. Where a real credential was committed at any time, **revoke or rotate it with its issuing provider immediately**, inspect use/access logs when available, and remove it from current code. Removing a commit or ignoring an alert does not revoke the credential.
5. If the match is benign, document a narrowly scoped reason and evidence privately. Any Gitleaks exclusion must be limited to the exact known false positive; do not disable whole categories or add a blanket ignore. History rewrite requires coordination because it changes commit SHAs and does not prevent copies or logs elsewhere.
6. Rerun both the local scan and the central [ten-repository workflow](https://github.com/cjblackthorn/blackthorn-enterprises/actions/workflows/portfolio-secret-audit.yml) after remediation. Never claim a passing scan implies a complete independent security assessment.

## Admin-only GitHub release hardening — no hosting changes

The central [branch protection issue #18](https://github.com/cjblackthorn/blackthorn-enterprises/issues/18) includes the exact nine repositories whose `main` branch was unprotected in the October 24 API inspection. An administrator should set Rulesets/Branch protection (match `main`, prevent force-push/deletion, require pull requests and suitable status checks, constrain bypass). Field Notes currently reports protected.

**Avoid deadlocks:** inspect which actual CI jobs run on *every* PR, especially repos with path-filtered workflows. Do not require a job that only runs on `main` or a deploy job skipped by PR design. A required independent reviewer cannot be satisfied by the PR author's own comment. Agree on a feasible review and emergency rollback policy before enforcing.

After settings are applied, verify the repository branch API reports `protected:true`, and test on a harmless PR. Repository settings cannot be inferred from passing GitHub Actions; a green workflow is evidence of code validation, not evidence the merge gate is enforced.

## Safe completion definition

- A full-history secret scanner result must be either **verified clean for the configured rules** or **privately investigated with any active credentials rotated and false positives narrowly documented**.
- No raw finding/credential should be published in public CI logs or PR comments.
- `main` releases should be gated by supported checks and rules without stopping valid rollbacks.
- Security headers and edge-policy limitations on GitHub Pages remain separate risk decisions; do not migrate hosts merely to produce a scanner score.
