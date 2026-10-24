#!/usr/bin/env python3
"""Dependency-free structural checks for the Blackthorn Enterprises static homepage."""

from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]


class SiteHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.local_references: list[tuple[str, str]] = []
        self.fragments: list[str] = []
        self.errors: list[str] = []
        self.mains: list[dict[str, str]] = []
        self.brand_logos: list[dict[str, str]] = []
        self.h1_count = 0
        self.skip_links: list[str] = []
        self.html_lang: str | None = None
        self.header_seen = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html":
            self.html_lang = values.get("lang")
        if tag == "header":
            self.header_seen = True
        if tag == "main":
            self.mains.append(values)
        if tag == "h1":
            self.h1_count += 1
        if values.get("id"):
            self.ids.append(values["id"])
        if tag == "img" and "brand-logo" in (values.get("class") or "").split():
            self.brand_logos.append(values)
        if tag == "img" and "alt" not in values:
            self.errors.append(f"Image {values.get('src', '(missing src)')} has no alt attribute")
        if tag == "a" and "skip-link" in (values.get("class") or "").split():
            if self.header_seen:
                self.errors.append("Skip link must precede the site header")
            self.skip_links.append(values.get("href") or "")
        for attribute in ("src", "href"):
            url = values.get(attribute)
            if not url:
                continue
            parts = urlsplit(url)
            if parts.scheme or parts.netloc or url.startswith("//"):
                continue
            if parts.path:
                self.local_references.append((tag, unquote(parts.path)))
            if parts.fragment:
                self.fragments.append(parts.fragment)


def main() -> int:
    html_path = ROOT / "index.html"
    css_path = ROOT / "styles.css"
    issues: list[str] = []
    page = SiteHTML()
    page.feed(html_path.read_text(encoding="utf-8"))
    issues.extend(page.errors)
    if not page.brand_logos:
        issues.append("No brand-card logos found")
    for image in page.brand_logos:
        if image.get("loading") != "lazy" or image.get("decoding") != "async":
            issues.append(f"Brand-card image lacks lazy/async loading: {image.get('src')}")

    if page.html_lang != "en":
        issues.append("Expected html lang=en")
    if len(page.mains) != 1 or page.mains[0].get("id") != "top":
        issues.append("Expected exactly one main landmark with id=top")
    if page.h1_count != 1:
        issues.append(f"Expected one H1, got {page.h1_count}")
    if page.skip_links != ["#top"]:
        issues.append("Expected one skip link targeting #top")

    duplicates = sorted(name for name, count in Counter(page.ids).items() if count > 1)
    if duplicates:
        issues.append(f"Duplicate HTML IDs: {duplicates}")

    target_ids = set(page.ids)
    for fragment in page.fragments:
        if fragment not in target_ids:
            issues.append(f"Broken in-page fragment: #{fragment}")

    for tag, path in page.local_references:
        target = (ROOT / path.lstrip("/")).resolve()
        if not target.is_relative_to(ROOT.resolve()) or not target.is_file():
            issues.append(f"Missing local {tag} reference: {path}")

    if not (ROOT / "CNAME").read_text(encoding="utf-8").strip():
        issues.append("CNAME is empty")
    css = css_path.read_text(encoding="utf-8")
    if ":focus-visible" not in css or "prefers-reduced-motion" not in css:
        issues.append("Expected focus-visible and reduced-motion styles")

    canonical = "https://blackthorn.enterprises/"
    if f'<link rel="canonical" href="{canonical}" />' not in html_path.read_text(encoding="utf-8"):
        issues.append("Enterprise homepage canonical URL missing")
    if "Sitemap: https://blackthorn.enterprises/sitemap.xml" not in (ROOT / "robots.txt").read_text(encoding="utf-8"):
        issues.append("robots.txt missing homepage sitemap reference")
    try:
        tree = ElementTree.parse(ROOT / "sitemap.xml")
        tag = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        urls = [v.text for v in tree.findall(f"{tag}url/{tag}loc")]
        if urls != [canonical]:
            issues.append(f"Incorrect sitemap URLs: {urls}")
    except (OSError, ElementTree.ParseError) as exc:
        issues.append(f"Invalid sitemap.xml: {exc}")

    if issues:
        print("Static site validation FAILED:")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print(
        "Static site validation PASSED: semantic main/H1, skip navigation, "
        "unique IDs, in-page links, local assets, alt attributes, CNAME, "
        "focus-visible and reduced-motion styles."
    )
    print(f"Checked {len(page.local_references)} local asset references.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
