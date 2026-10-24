"use strict";

/** Read-only mobile and desktop browser smoke test of public Blackthorn sites. */
const fs = require("node:fs");
const { chromium } = require("playwright");

const SITES = [
  ["enterprises", "Blackthorn Enterprises", "https://blackthorn.enterprises/"],
  ["rootworks", "Blackthorn Rootworks", "https://rootworks.technerd.tech/"],
  ["tropicals", "Tropical Plants", "https://tropicals.blackthorn.enterprises/"],
  ["personal", "Personal site", "https://corrinejblackthorn.com/"],
  ["field-notes", "Field Notes", "https://blackthornfieldnotes.ink/"],
  ["technerd", "TechNerd", "https://technerd.tech/"],
  ["glass-thorns", "Glass & Thorns", "https://glassandthorns.art/"],
  ["glass-rose", "Glass Rose Collective", "https://cjblackthorn.github.io/glass-rose-collective/"],
  ["petal-frame", "Petal & Frame", "https://petalsnframes.art/"],
  ["thorns2roses", "Thorns2Roses", "https://thorns2roses.com/"]
];

async function inspect(browser, slug, label, url, mode) {
  const context = await browser.newContext({
    viewport: mode === "mobile" ? { width: 390, height: 844 } : { width: 1440, height: 900 },
    deviceScaleFactor: 1,
    isMobile: mode === "mobile",
    hasTouch: mode === "mobile",
    reducedMotion: "reduce",
    ignoreHTTPSErrors: false
  });
  const page = await context.newPage();
  const result = { site: label, slug, mode, url, outcome: "UNVERIFIED", detail: "", httpStatus: null, finalUrl: null, title: "", hasMain: false, hasH1: false, skipLink: "absent", horizontalOverflowPx: null, pageErrors: [] };
  page.on("pageerror", (error) => result.pageErrors.push(String(error).slice(0, 180)));
  try {
    const response = await page.goto(url, { waitUntil: "domcontentloaded", timeout: 18_000 });
    // DOMContentLoaded alone may precede stylesheet completion and cause false
    // mobile-overflow reports. Wait for the load event before measurements.
    try {
      await page.waitForLoadState("load", { timeout: 20_000 });
      result.loadState = "complete";
    } catch {
      result.loadState = "timeout";
    }
    // Allow one layout tick after fonts/styles resolve, without hiding network errors.
    await page.waitForTimeout(350);
    const finalUrl = page.url();
    const status = response ? response.status() : null;
    result.finalUrl = finalUrl;
    result.httpStatus = status;
    if (!finalUrl.startsWith("https://")) throw new Error("Navigation ended at an insecure URL");
    if (!status || status >= 400) throw new Error("HTTP status " + status);
    result.title = await page.title();
    result.hasMain = await page.locator("main").count() > 0;
    result.hasH1 = await page.locator("h1").count() > 0;
    const skip = page.locator('a.skip-link, a.grc-skip-link').first();
    if (await skip.count() > 0) {
      await page.keyboard.press("Tab");
      const wasFocused = await skip.evaluate((el) => document.activeElement === el);
      result.skipLink = wasFocused ? "focusable-first" : "present-not-first-focus";
    }
    const width = await page.evaluate(() => document.documentElement.scrollWidth);
    result.horizontalOverflowPx = Math.max(0, width - (mode === "mobile" ? 390 : 1440));
    if (result.horizontalOverflowPx > 4) {
      result.overflowOffenders = await page.evaluate(() =>
        [...document.querySelectorAll("body *")].map((element) => {
          const box = element.getBoundingClientRect();
          const name = element.tagName.toLowerCase();
          const cls = typeof element.className === "string" ? element.className : "";
          return { tag: name, className: cls.slice(0, 70), id: element.id || "", right: Math.round(box.right), width: Math.round(box.width) };
        }).filter((entry) => entry.right > window.innerWidth + 4)
          .sort((a, b) => b.right - a.right).slice(0, 10)
      );
      console.log("OVERFLOW DIAGNOSTIC", label, mode, JSON.stringify(result.overflowOffenders));
    }
    // Observational image/resource telemetry: does not assume zero-byte cross-origin
    // resource timings mean an empty response, or that offscreen lazy images loaded.
    result.resourceEvidence = await page.evaluate(() => {
      const entries = performance.getEntriesByType("resource");
      const sameOrigin = entries.filter(resource => {
        try { return new URL(resource.name).origin === location.origin; }
        catch { return false; }
      });
      const transferred = sameOrigin.reduce((sum, r) => sum + (r.transferSize || 0), 0);
      const images = [...document.images];
      const brokenImages = images.filter(img => img.complete && img.naturalWidth === 0)
        .map(img => img.currentSrc || img.src).slice(0, 12);
      const loaded = images.filter(img => img.complete && img.naturalWidth > 0);
      const largest = sameOrigin.filter(r => r.transferSize > 0)
        .sort((a, b) => b.transferSize - a.transferSize).slice(0, 5)
        .map(r => ({ url: r.name, bytes: r.transferSize, type: r.initiatorType }));
      return {
        resourceCount: entries.length,
        sameOriginTimedBytes: transferred,
        loadedImageCount: loaded.length,
        totalImageElements: images.length,
        brokenLoadedImages: brokenImages,
        largestTimingVisibleResources: largest
      };
    });
    const warnings = [];
    if (result.loadState === "timeout") warnings.push("full resource load timed out (layout results may be incomplete)");
    if (!result.hasMain) warnings.push("no main landmark");
    if (!result.hasH1) warnings.push("no H1");
    if (result.skipLink !== "focusable-first") warnings.push("skip link: " + result.skipLink);
    if (result.horizontalOverflowPx > 4) warnings.push("horizontal overflow: " + result.horizontalOverflowPx + "px");
    if (result.pageErrors.length) warnings.push(result.pageErrors.length + " uncaught JS page error(s)");
    if (result.resourceEvidence.brokenLoadedImages.length) warnings.push(result.resourceEvidence.brokenLoadedImages.length + " broken loaded image(s)");
    result.outcome = warnings.length ? "REVIEW" : "PASS";
    result.detail = warnings.length ? warnings.join("; ") : "HTML rendered; landmarks and basic keyboard/mobile checks passed";
    if (mode === "mobile") {
      try { await page.screenshot({ path: "browser-artifacts/" + slug + "-mobile.png", fullPage: false, timeout: 8_000 }); }
      catch (error) { result.detail += "; screenshot unavailable"; }
    }
  } catch (error) {
    result.outcome = /certificate|ERR_CERT|SSL|CERT_/i.test(String(error)) ? "TLS_FAILED" : "NAVIGATION_UNVERIFIED";
    result.detail = String(error).replace(/\s+/g, " ").slice(0, 280);
  } finally {
    await context.close();
  }
  return result;
}

async function main() {
  fs.mkdirSync("browser-artifacts", { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const results = [];
  try {
    for (const [slug, label, url] of SITES) {
      for (const mode of ["desktop", "mobile"]) {
        const result = await inspect(browser, slug, label, url, mode);
        results.push(result);
        console.log(label, mode, result.outcome, result.detail);
        if (result.outcome !== "PASS") console.log("::warning title=Browser QA - " + label + " " + mode + "::" + result.outcome + " " + result.detail.replaceAll("%", " percent "));
      }
    }
  } finally {
    await browser.close();
  }

  fs.writeFileSync("browser-artifacts/results.json", JSON.stringify({ at_utc: new Date().toISOString(), results }, null, 2) + "\n");
  const lines = [
    "## Read-only browser smoke tests",
    "",
    "Chromium desktop (1440px) and mobile (390px), reduced-motion preference, strict HTTPS. Checks navigation, H1/main landmark, first keyboard skip link, horizontal overflow, uncaught page errors, and images that finished loading but failed. Passive performance-resource data is recorded as diagnostic evidence only.",
    "",
    "| Site | Desktop | Mobile | Notes |",
    "| --- | --- | --- | --- |"
  ];
  for (let i = 0; i < results.length; i += 2) {
    const desktop = results[i];
    const mobile = results[i + 1];
    const note = [desktop, mobile].filter(x => x.outcome !== "PASS").map(x => x.mode + ": " + x.detail).join(" / ").replaceAll("|", "/").slice(0, 300);
    lines.push("| " + desktop.site + " | " + desktop.outcome + " | " + mobile.outcome + " | " + (note || "No smoke-test findings") + " |");
  }
  lines.push("", "### Passive asset evidence (unthrottled CI)", "",
    "| Site | Images loaded / page elements | Broken loaded images | Timing-visible same-origin KiB |",
    "| --- | ---: | ---: | ---: |");
  for (const result of results.filter(item => item.mode === "desktop")) {
    const e = result.resourceEvidence;
    if (!e) { lines.push("| " + result.site + " | unverified | unverified | unverified |"); continue; }
    const kb = Math.round(e.sameOriginTimedBytes / 1024);
    lines.push("| " + result.site + " | " + e.loadedImageCount + " / " +
      e.totalImageElements + " | " + e.brokenLoadedImages.length + " | " + kb + " |");
  }
  lines.push("", "Resource timing bytes are an **incomplete lower bound** (cross-origin resources and cached responses may be excluded). Offscreen lazy images may not have loaded. This is not LCP, a Lighthouse score, bandwidth simulation, or a complete asset audit.",
    "", "This is **not** a WCAG audit, user consent/form submission test, performance benchmark, or production security assessment. Noncritical findings belong in [queue #4](https://github.com/cjblackthorn/blackthorn-enterprises/issues/4). Tropical Plants HTTPS enforcement was fixed and independently verified in [closed issue #14](https://github.com/cjblackthorn/blackthorn-tropicals/issues/14).");
  if (process.env.GITHUB_STEP_SUMMARY) fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, lines.join("\n") + "\n");
  console.log(lines.join("\n"));
  // Do not block unrelated changes for known domain/network and accessibility findings.
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
