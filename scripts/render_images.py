#!/usr/bin/env python3
"""Render the home-page images from their HTML sources.

    pip install playwright && playwright install chromium
    python3 scripts/render_images.py            # from the docs root

Sources live in images/src/*.html (edit them, not the PNGs). Each page draws
into a #canvas element; the script screenshots it at 2x for sharp retina images.
Set INTER_DIR to a folder with inter-latin-{400..800}-normal.woff2 files to
render offline; otherwise Inter loads from Google Fonts.
"""
import os
import pathlib

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "images" / "src"
OUT = ROOT / "images"
JOBS = {"home-hero.html": "home-hero.png", "architecture.html": "cyberwave-architecture.png"}


def local_fonts_css() -> str:
    d = os.environ.get("INTER_DIR")
    if not d:
        return ""
    faces = []
    for w in (400, 500, 600, 700, 800):
        f = pathlib.Path(d) / f"inter-latin-{w}-normal.woff2"
        if f.exists():
            faces.append(f'@font-face{{font-family:"Inter";font-weight:{w};src:url("{f.as_uri()}") format("woff2")}}')
    return "\n".join(faces)


def main() -> None:
    fonts = local_fonts_css()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=2, viewport={"width": 1300, "height": 1200})
        for src, out in JOBS.items():
            page.goto((SRC / src).as_uri())
            if fonts:
                page.add_style_tag(content=fonts)
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(300)
            page.locator("#canvas").screenshot(path=str(OUT / out), omit_background=True)
            print("wrote", OUT / out)
        browser.close()


if __name__ == "__main__":
    main()
