# Blackthorn website operations and security runbook

**Version:** October 24, 2026. **Scope:** public websites only. This runbook does not assert ownership of third-party services, guarantee continuous availability, or approve business/legal content.

Source of truth: [six-phase tracker](https://github.com/cjblackthorn/blackthorn-enterprises/issues/2), [final remediation queue](https://github.com/cjblackthorn/blackthorn-enterprises/issues/4), and [owner handoff](WEBSITE_PROGRAM_HANDOFF.md). This document favors **security and operational readiness without hosting migrations, DNS redesign or new CDN dependencies**.

## 1. Public site and release inventory

| Service | Repo | Published target | Source/build model |
| --- | --- | --- | --- |
| Blackthorn Enterprises | `cjblackthorn/blackthorn-enterprises` | `https://blackthorn.enterprises/` | Static GitHub Pages, source validation, Pages deployment |
| Blackthorn Rootworks | `cjblackthorn/blackthorn-rootworks` | `https://rootworks.technerd.tech/` | Static GitHub Pages, source validation |
| Tropical Plants storefront | `cjblackthorn/blackthorn-tropicals` | `https://tropicals.blackthorn.enterprises/` | **Static GitHub Pages** storefront with browser cart tests; **separate Vinext Worker deployment unverified** |
| Corrine personal | `cjblackthorn/corrine-j-blackthorn` | `https://corrinejblackthorn.com/` | Astro build, pinned npm lockfile, Pages artifact/deploy |
| Field Notes | `cjblackthorn/cjblackthorn.github.io` | `https://blackthornfieldnotes.ink/` | Jekyll + html-proofer, GitHub Pages |
| TechNerd | `cjblackthorn/technerd` | `https://technerd.tech/` | Jekyll; **custom and native Pages publication both currently observed** |
| Glass & Thorns | `cjblackthorn/glass-and-thorns` | `https://glassandthorns.art/` | Static GitHub Pages |
| Glass Rose Collective | `cjblackthorn/glass-rose-collective` | `https://cjblackthorn.github.io/glass-rose-collective/` | Jekyll GitHub Pages project subpath |
| Petal & Frame | `cjblackthorn/petals-and-frames` | `https://petalsnframes.art/` | Static GitHub Pages, gallery interaction/browser tests |
| Thorns2Roses | `cjblackthorn/thorns2roses` | `https://thorns2roses.com/` | Static GitHub Pages, policy print/browser tests |

**Out of scope for live uptime:** `cjblackthorn/whats-that-thing` is a local-only prototype, not a published site. Exact project domain/route ownership requires repository Pages settings or DNS-provider administrative evidence if disputed.

## 2. Daily release gate and proof of production

1. Use an isolated PR with a specific scope, rollback note, and documented test plan. Never commit passwords, API keys, private tokens, customer submissions or `.env` secrets. Review all changed third-party script URLs and dependency updates. No auto-merge of breaking major versions.
2. Require the **exact PR head** to pass relevant source/build tests before merge. Tropical Plants contains **two different applications**; a static Pages test does not validate the Vinext Worker and vice versa.
3. Protect the default branch through repository rules where available: required tests, no force pushes, minimal write access, and review by a different authorized person for sensitive changes. The connected GitHub owner cannot approve their own PR; a self-review comment is evidence but **not independent approval**.
4. After merge, confirm the **main-branch SHA** and the appropriate GitHub Pages deployment succeeded. A passing CI build alone does not prove that production received it.
5. Verify the **published HTTPS URL** with normal certificate verification, following redirects. Run relevant interaction QA against the actual deployed version where possible. Capture the exact SHA, Actions run URL, observed behavior, unresolved risks and any owner signoff in the tracker.
6. If any check fails, hold acceptance, open an issue with reproducible evidence, and either correct in another PR or revert the bad commit.

## 3. Monitoring and alert response

Current scheduled/read-only monitors in `blackthorn-enterprises`:

- [Public-site health](https://github.com/cjblackthorn/blackthorn-enterprises/actions/workflows/public-site-health.yml): selected public URLs, strict HTTPS, expected HTML/PDF/sitemap payloads and Tropical Plants HTTP-to-HTTPS and Pages-alias redirects. Monitor does not automatically conclude availability incidents on a network-limited result.
- [Desktop/mobile Chromium checks](https://github.com/cjblackthorn/blackthorn-enterprises/actions/workflows/browser-qa.yml): ten public homepages, rendered landmarks, basic keyboard behavior, viewport overflow, page JS errors, image failures and limited resource-timing evidence. Not a full WCAG or page-weight audit.
- [Public response-header audit](https://github.com/cjblackthorn/blackthorn-enterprises/actions/workflows/security-header-audit.yml): strict-TLS HSTS, CSP, nosniff, referrer and framing response observations. **Missing security headers are open for hosting-specific risk assessment**, not evidence of an active compromise.

**Every monitor is an observation**, not an automated incident response or guaranteed notification. Someone must check failed runs and warnings; GitHub Actions artifact retention is limited. Recommended cadence: inspect scheduled runs weekly, dependency advisories as received, DNS/registrar/certificate status monthly and before important launches, and form delivery/contractual disclosures after meaningful changes. Set independent domain-registration renewal reminders with the registrar; GitHub Pages certificate renewal does not renew a domain.

## 4. Triage and recovery

| Severity | Example | First response |
| --- | --- | --- |
| P0 | HTTPS certificate fails for visitors, malicious content or exposed credentials | Stop risky release, preserve evidence, remove exposed credential access, rotate affected credentials through their provider, verify live paths, coordinate with owner and GitHub/provider support |
| P1 | Contact/quote flow broken, wrong account permissions, production dependency exploit exposure, significant outage | Reproduce safely, assess scope, mitigate or revert, keep tracking issue open until live verification |
| P2 | Broken noncritical page, performance regression, isolated accessibility issue | Open issue with reproducible evidence and test the change in a PR |
| P3 | Design polish or deferred optimization | Schedule after functional/security gates |

**If a newly deployed change breaks the site:** identify the first failing SHA in `Actions` and the PR commit history. Prefer `git revert`/a GitHub Revert PR over force-pushing `main`. Run PR validation, merge safely, verify the restored Pages deployment and strict HTTPS. Do **not** assume that GitHub Actions passing means the real domain works.

**If a custom-domain HTTPS check fails:** first distinguish DNS, certificate, redirects and browser cache. Confirm GitHub Pages Settings → custom domain, verified DNS and `Enforce HTTPS` state. Tropical Plants [issue #14](https://github.com/cjblackthorn/blackthorn-tropicals/issues/14) documents the repair; HTTPS was independently verified. Avoid removing and re-adding an approved certificate or changing DNS without evidence. Re-run public health and strict-TLS checks.

**If GitHub Pages builds twice for TechNerd:** both native Pages and custom workflow deployments have been observed; do not delete either without confirming the repository Pages **Build and deployment** source in Settings and the active deployed SHA. Track consolidation in [final queue #4](https://github.com/cjblackthorn/blackthorn-enterprises/issues/4).

**If a Tropical Plants Worker issue is suspected:** do not infer deployment from `worker/` or `app/` source. Check Cloudflare Workers & Pages routes, custom domains, deployments and revision. The public `tropicals.blackthorn.enterprises` currently serves the static GitHub Pages storefront. [Worker verification issue #1](https://github.com/cjblackthorn/blackthorn-tropicals/issues/1) remains open until administrative evidence resolves deployment status.

## 5. Security and data handling

- **Access:** least-privilege CI `GITHUB_TOKEN`, disabled checkout credential persistence, separate write privileges only for Pages deployment jobs. Audit repository collaborators and branch rules in GitHub Settings; do not publish actual collaborator names, secrets or access tokens in issue comments.
- **Secrets and dependencies:** enable and review repository-supported secret scanning, Dependabot security alerts and dependency review where available. Conduct a deliberate history and built-site scan before claiming no exposed keys. CI lint and `npm audit` are **not** an exhaustive application-security review.
- **Forms:** do not send real inquiries or client data in automated smoke tests. Document actual third-party processors, information collected, retention, and consent; verify business inbox/mailto handoff with the owner outside destructive automation. Do not claim confidentiality or encryption for an email compose handoff.
- **Browser rendering:** avoid interpolating user- or catalog-provided values into `innerHTML`; use DOM APIs/`textContent`, validate URLs, restrict redirect destinations and storage-derived values. Test malicious strings and corrupt localStorage without sending data.
- **Headers:** [security header assessment #16](https://github.com/cjblackthorn/blackthorn-enterprises/issues/16) tracks HSTS/CSP/nosniff/referrer/framing controls. Native GitHub Pages may not support custom response headers. Do not deploy untested CSP, a new proxy or platform migration just to achieve green scanning.
- **Privacy/permissions:** final approval of photography rights, coaching legal language, service claims and privacy disclosures belongs to responsible owners/qualified reviewers. The software tests cannot make those commitments accurate.

## 6. Operational exit criteria per site

Use this checklist independently for **each** published site; only then call the site operationally accepted:

- [ ] Domain ownership and current DNS/hosting source recorded; verified TLS and secure redirects
- [ ] Main-branch release and Pages deployment confirmed at known SHA with passing source/build tests
- [ ] Page navigation, 320px/mobile and desktop layouts, keyboard path, forms/quotes and asset loading verified, or explicit *not testable* finding tracked
- [ ] Security advisories, reachable trust boundaries, credentials, input sinks, third-party services, permissions and available hosting-layer hardening reviewed
- [ ] Monitoring ownership, rollback approach and incident contact documented
- [ ] Business owner approved published service/claim/privacy/legal/photography content
- [ ] Residual risks and final signoff captured in [queue #4](https://github.com/cjblackthorn/blackthorn-enterprises/issues/4)

**Status definition:** passing the 18-resource health checks and ten-homepage browser smoke checks is important baseline evidence but is **not** certification of these exit criteria. Do not mark a site fully accepted when its Worker exposure, forms, content or assistive-tech review remain unverified.
