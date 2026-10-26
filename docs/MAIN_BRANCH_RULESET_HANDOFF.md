# Main-branch release-control administrator handoff

**Inventory verified:** October 25, 2026 (Pacific).  
**Owner:** authorized repository administrator, authenticated as `cjblackthorn`.  
**Tracker:** [release controls #18](https://github.com/cjblackthorn/blackthorn-enterprises/issues/18) and [six-phase website tracker #2](https://github.com/cjblackthorn/blackthorn-enterprises/issues/2).  
**Scope:** nine public-site repositories listed below. No DNS, hosting, or CDN changes.

> This document is an administrator handoff, **not a claim that branch protection has been enabled**. Do not mark issue #18 complete based on this file or on passing Actions jobs.

## 1. Verified as of October 25

GitHub branch API: all nine target `main` branches reported `protected: false`.  
GitHub ruleset API: each of the nine returned `[]`.  
GitHub repository metadata: `permissions.admin: true` for the authenticated `cjblackthorn` account across **all nine**. The connected GitHub integration **does not expose ruleset/branch-protection writes**, even when the account has admin access.

**Excluded:** `cjblackthorn.github.io` (Field Notes) reported `main.protected: true` and an active existing ruleset [#15951891](https://github.com/cjblackthorn/cjblackthorn.github.io/rules/15951891). Do not reset or alter that ruleset during this rollout. Field Notes credential triage is a separate security item and must remain private.

### Exact candidate required GitHub Actions check names

These names were inspected in checked-in `main` workflow YAML **and observed successful on the GitHub Actions check-runs for the October 24 merged secret-scan PR head SHAs**. Names are job check contexts, not workflow display names. All nine have an unconditional PR `secret-scan` job pinned to Gitleaks v8.30.1.

| Repository | Require on PR | Not suitable as a required check without a workflow change |
| --- | --- | --- |
| `blackthorn-enterprises` | `secret-scan`, `static-validation` | `read-branch-status` (path-filtered); observation/deployment jobs |
| `blackthorn-rootworks` | `secret-scan`, `static-checks` | Deployment |
| `blackthorn-tropicals` | `secret-scan` **initially only** | `app-checks`, `static-checks`, `cart-browser-regression` (path-filtered) |
| `corrine-j-blackthorn` | `secret-scan`, `build` | `deploy` (skipped on PR) |
| `technerd` | `secret-scan`, `build` | `deploy` (skipped on PR) |
| `glass-and-thorns` | `secret-scan`, `verify` | Deployment |
| `glass-rose-collective` | `secret-scan`, `source-integrity`, `render-smoke` | Deployment |
| `petals-and-frames` | `secret-scan`, `site-integrity` | `gallery-browser` (path-filtered) |
| `thorns2roses` | `secret-scan`, `site-integrity` | `policy-browser` (path-filtered) |

**Tropical Plants residual gap:** `secret-scan` prevents checked-in scanner findings from passing the PR gate, but does **not** make app/static/cart tests mandatory for every relevant change. Design a separate **unconditional, path-aware aggregate release check**, verify it for app-only, static-only, docs-only, mixed, and workflow-only PRs, then require its stable check context in addition to `secret-scan`. Do not select the three filtered jobs directly as universally required checks.

For Petal & Frame and Thorns2Roses, preserve the path-filtered browser tests as supplemental checks until an unconditional aggregate is available. Review actual test runs for relevant file changes.

## 2. Apply in GitHub Settings (authorized administrator)

For **each** of the nine repositories above:

1. Open `https://github.com/cjblackthorn/<repository>/settings/rules`, choose **New branch ruleset**, name it `Protect main - required PR checks`, and target **default branch** / `main`. If a suitable active rule already exists at time of execution, **inspect and update it instead of creating a conflicting duplicate**.
2. Set **Enforcement status = Active** (not Evaluate or Disabled).
3. Enable **Restrict deletions** and **Block force pushes / Restrict non-fast-forward updates**.
4. Enable **Require a pull request before merging**, with **0 required approving reviews** under the current sole-maintainer model. Require conversation resolution where practical. If a second qualified authorized reviewer becomes routinely available, set **1 approval** and review sensitive changes independently. A self-review comment is not independent approval.
5. Enable **Require status checks to pass**. Select the check contexts in the table, sourced from **GitHub Actions** when GitHub offers the source selector; do not mistake workflow titles for job names. Consider requiring the PR to be up to date with `main` once verified workable with the existing workflows.
6. Do **not** allow force pushes or branch deletion as a routine emergency exception. Avoid standing bypass actors; inspect admins, collaborators, and automation identities. Do not assume user-level admin rights automatically permit bypass when no bypass actors are configured.
7. Save and inspect the resulting ruleset URL, rules, bypass list, and active status. Re-check `GET /repos/cjblackthorn/<repo>/branches/main` and `GET /repos/cjblackthorn/<repo>/rulesets`. `protected: true` alone is not enough to certify policy details.

Do not require skipped deployment jobs, path-filtered jobs, scheduled-only jobs, or status names not yet observed on an actual PR. Confirm naming and provenance on the PR's **Checks** view before activating each check gate.

## 3. Review and release policy

- **Normal change:** create a scoped branch and PR; state purpose, changed trust boundaries, relevant QA, rollback plan, and whether application/public content is affected. Wait for required checks on the **current PR head** and relevant optional path-specific QA. Review and address any changes requested in comments. The sole maintainer may merge a self-authored PR after automated validation with the decision recorded; do not falsely record it as peer-approved.
- **High-impact change:** deployment/publishing logic, Actions permissions, dependencies, forms, secrets handling, payment or customer data flow, security headers, and identity/permissions changes receive a documented manual security review. Ask a genuinely independent maintainer when available; if none is available, record the owner decision and elevated residual risk.
- **After merge:** record the merge SHA, ensure the appropriate site build and Pages deployment succeeded, and run live HTTPS/site checks. A green PR check does not guarantee successful public delivery.
- **No force pushes, direct pushes to main, bulk approval, or quiet administrative bypass.** Keep the exception path exceptional and auditable.

## 4. Emergency revert and recovery

1. **Assess and contain:** identify affected repository, deployed URL, incident priority, last-known-good SHA, failure symptoms, and potential data/security consequences. Retain evidence without publishing suspected credentials.
2. **Prefer a safe revert PR:** branch from current `main`, use GitHub **Revert** or `git revert <commit>` for the problematic change (revert merged changes carefully, respecting merge parents), open a PR with incident link, and run the normal required checks and relevant app/browser QA.
3. **Merge and prove recovery:** verify PR merged without rule bypass, successful main Actions/Pages deployment, public HTTPS checks and actual restored behavior. Document original and revert SHAs, run IDs, and user impact.
4. **Only if normal checks cannot run during an urgent outage:** an authorized repository administrator may document and approve a narrowly scoped, time-bounded emergency exception. Record who authorized it, why the standard revert path was blocked, exactly which rule/check is temporarily changed, start/end time, affected commit, validation performed, and the post-incident review. Restore active protections immediately afterward and re-query the live rules. Never use destructive force push/deletion to recover the published site.
5. **Investigate root cause and prevent recurrence** in the existing relevant issue. Do not claim full recovery solely from a completed workflow.

## 5. Acceptance and issue closure evidence

For **each** repository, capture and link:

- [ ] Active ruleset URL, targeted `main`, its PR, checks, deletion/non-fast-forward and bypass settings.
- [ ] `main.protected: true` plus inspected ruleset parameters (not just the boolean).
- [ ] Harmless test PR number, head SHA, required-check runs, and confirmation a missing/failing required check blocks merge (without intentionally exposing a secret).
- [ ] Successful normal PR merge, resulting main SHA, main build/deploy run, and any live verification.
- [ ] Revert PR and successful restoration, or another harmless rollback demonstration that proves compliance with the same rules.
- [ ] Explicit residual risks and any justified exceptions.

**Keep other tickets separate:** Field Notes current-tree/historical credential investigation (private triage, never publish findings) and [HTTP response-header remediation #16](https://github.com/cjblackthorn/blackthorn-enterprises/issues/16). Ruleset work does not require changing hosting, DNS, or CDN.
