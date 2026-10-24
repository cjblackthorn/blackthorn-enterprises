# Blackthorn website improvement program — owner handoff
Last updated: October 24, 2026

Source of truth: [six-phase tracker #2](https://github.com/cjblackthorn/blackthorn-enterprises/issues/2). Outstanding findings: [final remediation queue #4](https://github.com/cjblackthorn/blackthorn-enterprises/issues/4).

## Verified engineering outcomes

The repositories have gained reviewable PR/build validation, incremental accessibility improvements, dependency repairs, SEO canonical/sitemap updates, and production Pages verification. In particular:

- The personal Astro site's checkout/setup/upload/deploy action upgrades and résumé replacement shipped with successful production checks.
- TechNerd's Pages permissions are limited to deployment jobs. Upload-pages-artifact@v5 and deploy-pages@v5 have each been validated on `main`. Its Jekyll sitemap and robots discovery are tested.
- Enterprises, Rootworks, Tropical Plants static storefront, Thorns2Roses, Petal & Frame, Glass & Thorns, and Glass Rose Collective received incremental source/CI/SEO/accessibility improvements. The What's That Thing? project remains local-only and has Node 24 smoke tests; it was **not** deployed.
- The [cross-site public health test PR #11](https://github.com/cjblackthorn/blackthorn-enterprises/pull/11) verifies **18 of 18 live URLs/resources** with normal certificate verification, including the Tropical Plants HTTP→HTTPS and GitHub Pages alias redirects; [PR report #40116592515](https://github.com/cjblackthorn/blackthorn-enterprises/actions/runs/40116592515), [main Pages deployment #40116635506](https://github.com/cjblackthorn/blackthorn-enterprises/actions/runs/40116635506).
- Tropical Plants static storefront quote/cart arithmetic, localStorage resilience, and keyboard dialog behavior are covered by Playwright tests and verified production Pages builds ([PRs #17 and #18](https://github.com/cjblackthorn/blackthorn-tropicals/pulls?q=is%3Apr+is%3Amerged)).
- Petal & Frame desktop/mobile gallery keyboard focus, Escape/arrow navigation and focus restoration now pass Chromium regression tests; [PR #4](https://github.com/cjblackthorn/petals-and-frames/pull/4) deployed.
- Thorns2Roses policy print behavior and 320px/390px/desktop navigation passed local Chromium tests; [PR #3](https://github.com/cjblackthorn/thorns2roses/pull/3) deployed. This does not establish legal accuracy.

A successful build/upload/deployment and an HTTP 200 smoke test **do not** certify browser functionality, WCAG conformance, business accuracy, or complete security.

## Owner/admin action — do not defer

### Resolved: Tropical Plants HTTPS — no action required

On October 24, 2026, the owner successfully enabled **Enforce HTTPS** in GitHub Pages. [Read-only post-change verification #40114934696](https://github.com/cjblackthorn/blackthorn-tropicals/actions/runs/40114934696) confirmed:

- GitHub Pages API reported `https_enforced=true` and an approved, hostname-matching certificate.
- Plain HTTP redirects 301 to the secure custom domain.
- HTTPS returns HTTP 200 with successful strict certificate verification.
- The default GitHub Pages alias redirects 301 to the HTTPS custom domain.

[Original HTTPS issue #14 was closed](https://github.com/cjblackthorn/blackthorn-tropicals/issues/14). The [cross-site monitoring suite](https://github.com/cjblackthorn/blackthorn-enterprises/actions/workflows/public-site-health.yml) now checks the redirects weekly. Do not change DNS/certificate settings without a new observed failure.

### P1: Confirm any separate Cloudflare/Vinext Worker

The custom-domain web page was proven to be the **GitHub Pages static storefront**; that does not prove a separate Worker does not exist. In the Cloudflare dashboard, inspect Workers & Pages projects, routes, custom domains, and last deployed revision for the Tropical Plants app. Record its live URL, deployed source SHA/version, and whether it is intended for production. If active, confirm it includes the already-merged source dependency and Next.js fixes; plan a controlled deploy if not. If no Worker is live, record that conclusion. See [Tropical issue #1](https://github.com/cjblackthorn/blackthorn-tropicals/issues/1).

## Owner/content approvals — needed before final acceptance, not for every engineering PR

- **Thorns2Roses:** confirm coaching policy and intake language, third-party form disclosures, consent/recording expectations and retention commitments accurately describe actual practices. Consult a qualified reviewer as appropriate. Broken policy downloads were repaired but the legal accuracy of their contents was not certified.
- **Petal & Frame:** approve photography display rights and actual service descriptions/pricing; use only real testimonials with client consent. Unverified example quotations were removed.
- **TechNerd / Rootworks / all brands:** approve service offerings, prices, credentials, public claims, consultation and inquiry routes, and intended external services.
- **Final usability acceptance:** review the finished public pages on a phone and desktop (with keyboard and screen reader testing ideally performed by a qualified tester) for visible, usable navigation, galleries/cart/forms, readability and the intended look. The [remediation queue #4](https://github.com/cjblackthorn/blackthorn-enterprises/issues/4) lists concrete tests.

## Work that remains in the engineering/QA backlog — not transferred to the owner

- Remaining browser-level functional regression and WCAG 2.2 AA assessment; visual contrast, screen-reader semantics, contact/inquiry flows, actual print appearance and narrow-layout edge cases. Automated cart/quote, gallery, mobile menu and policy print checks now exist; these are not full certification.
- Performance measurements and selective large-image optimizations, SEO/structured data review, complete external-link, secrets and security-header audit.
- TechNerd duplicate GitHub native/custom Pages deployment consolidation after verifying the intended Pages source of truth.
- Maintenance/rollback coverage on remaining repositories and final acceptance evidence by site.
- Local-only What's That Thing? prototype privacy, export/backup and full interaction tests before any decision to host it publicly.

## Release acceptance

Close an individual finding only with issue/PR evidence, the exact deployed commit and successful CI/Pages run where applicable, a real-world verification result when possible, and documented remaining risk. The [master tracker #2](https://github.com/cjblackthorn/blackthorn-enterprises/issues/2) and [queue #4](https://github.com/cjblackthorn/blackthorn-enterprises/issues/4) should stay open until critical hosting work and remaining acceptance checks are complete.
