"""Render deck.html to SUVARNA_TRUST.pdf and one PNG per slide (to check before sharing).
Run: python docs/deck/build.py"""
import pathlib

import pymupdf
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
PDF = HERE / "SUVARNA_TRUST.pdf"

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 1280, "height": 720})
    page.goto((HERE / "deck.html").as_uri(), wait_until="networkidle")
    page.evaluate("document.fonts.ready")
    page.pdf(path=str(PDF), width="1280px", height="720px", print_background=True)
    b.close()

doc = pymupdf.open(PDF)
for i, pg in enumerate(doc, 1):
    pg.get_pixmap(dpi=96).save(HERE / f"slide-{i}.png")
print(len(doc), "pages")
