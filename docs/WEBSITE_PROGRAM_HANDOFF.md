# Blackthorn website improvement program — owner handoff
Last updated: October 24, 2026

Source of truth: [six-phase tracker #2](https://github.com/cjblackthorn/blackthorn-enterprises/issues/2). Outstanding findings: [final remediation queue #4](https://github.com/cjblackthorn/blackthorn-enterprises/issues/4).

## Verified engineering outcomes

The repositories have gained reviewable PR/build validation, incremental accessibility improvements, dependency repairs, SEO canonical/sitemap updates, and production Pages verification. In particular:

- The personal Astro site's checkout/setup/upload/deploy action upgrades and résumé replacement shipped with successful production checks.
- TechNerd's Pages permissions are limited to deployment jobs. Upload-pages-artifact@v5 and deploy-pages@v5 have each been validated on `main`. Its Jekyll sitemap and robots discovery are tested.
- Enterprises, Rootworks, Tropical Plants static storefront, Thorns2Roses, Petal & Frame, Glass & Thorns, and Glass Rose Collective received incremental source/CI/SEO/accessibility improvements. The What's That Thing? project remains local-only and has Node 24 smoke tests; it was **not** deployed.
- [Read-only public-site probe PR #5](https://github.com/cjblackthorn/blackthorn-enterprises/pull/5) checks 16 public homepage/resource URLs without disabling TLS verification. [Validation run 40102281615](https://github.com/cjblackthorn/blackthorn-enterprises/actions/runs/40102281615) verified **15/16**. The personal homepage and résumé URL returned HTTPS HTTP 200, and the résumé returned PDF MIME and signature bytes. Only Tropical Plants failed due a custom-domain certificate hostname mismatch.

A successful build/upload/deployment and an HTTP 200 smoke test **do not** certify browser functionality, WCAG conformance, business accuracy, or complete security.

## Owner/admin action — do not defer

### P0: Repair Tropical Plants custom-domain HTTPS

[Detailed issue #14](https://github.com/cjblackthorn/blackthorn-tropicals/issues/14) contains reproduction and original certificate evidence. `tropicals.blackthorn.enterprises` resolves via CNAME to GitHub Pages but presented a certificate for `*.github.io` instead of the requested custom hostname. Normal HTTPS verification failed, and GitHub Pages redirected its alias to HTTP.

1. Sign in to GitHub and navigate to [Blackthorn Tropical Plants → Settings → Pages](https://github.com/cjblackthorn/blackthorn-tropicals/settings/pages).
2. Verify the intended source of the deployed **static** GitHub Pages storefront and that the custom domain is exactly `tropicals.blackthorn.enterprises`.
3. Check the custom-domain certificate provisioning status and any GitHub Pages reported errors. In DNS management, verify the intended CNAME `tropicals.blackthorn.enterprises → cjblackthorn.github.io`, absence of conflicting records, and CAA restrictions (if any).
4. Follow GitHub Pages guidance to complete/retry certificate provisioning. Avoid deleting the domain or making broad DNS changes without considering downtime and ownership.
5. Once GitHub provides a certificate that includes this hostname, enable **Enforce HTTPS** in Pages settings. Do not treat the existing `curl --insecure` 200 response as success.
6. Run [Public site health checks](https://github.com/cjblackthorn/blackthorn-enterprises/actions/workflows/public-site-health.yml) manually from the Actions tab, and require that the Tropical Plants result changes to `PASS`; verify redirects remain HTTPS. Keep issue #14 open until there is evidence of a matching certificate and successful TLS validation.

### P1: Confirm any separate Cloudflare/Vinext Worker

The custom-domain web page was proven to be the **GitHub Pages static storefront**; that does not prove a separate Worker does not exist. In the Cloudflare dashboard, inspect Workers & Pages projects, routes, custom domains, and last deployed revision for the Tropical Plants app. Record its live URL, deployed source SHA/version, and whether it is intended for production. If active, confirm it includes the already-merged source dependency and Next.js fixes; plan a controlled deploy if not. If no Worker is live, record that conclusion. See [Tropical issue #1](https://github.com/cjblackthorn/blackthorn-tropicals/issues/1).

## Owner/content approvals — needed before final acceptance, not for every engineering PR

- **Thorns2Roses:** confirm coaching policy and intake language, third-party form disclosures, consent/recording expectations and retention commitments accurately describe actual practices. Consult a qualified reviewer as appropriate. Broken policy downloads were repaired but the legal accuracy of their contents was not certified.
- **Petal & Frame:** approve photography display rights and actual service descriptions/pricing; use only real testimonials with client consent. Unverified example quotations were removed.
- **TechNerd / Rootworks / all brands:** approve service offerings, prices, credentials, public claims, consultation and inquiry routes, and intended external services.
- **Final usability acceptance:** review the finished public pages on a phone and desktop (with keyboard and screen reader testing ideally performed by a qualified tester) for visible, usable navigation, galleries/cart/forms, readability and the intended look. The [remediation queue #4](https://github.com/cjblackthorn/blackthorn-enterprises/issues/4) lists concrete tests.

## Work that remains in the engineering/QA backlog — not transferred to the owner

- Full browser-level functional regression and WCAG 2.2 AA assessment; visual contrast, screen-reader semantics, cart/quote and contact flows, print-to-PDF, narrow layouts.
- Performance measurements and selective large-image optimizations, SEO/structured data review, complete external-link, secrets and security-header audit.
- TechNerd duplicate GitHub native/custom Pages deployment consolidation after verifying the intended Pages source of truth.
- Maintenance/rollback coverage on remaining repositories and final acceptance evidence by site.
- Local-only What's That Thing? prototype privacy, export/backup and full interaction tests before any decision to host it publicly.

## Release acceptance

Close an individual finding only with issue/PR evidence, the exact deployed commit and successful CI/Pages run where applicable, a real-world verification result when possible, and documented remaining risk. The [master tracker #2](https://github.com/cjblackthorn/blackthorn-enterprises/issues/2) and [queue #4](https://github.com/cjblackthorn/blackthorn-enterprises/issues/4) should stay open until critical hosting work and remaining acceptance checks are complete.
