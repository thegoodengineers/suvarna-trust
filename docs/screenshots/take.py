"""Retake every screenshot in this folder from the running demo.
Run: python -m uvicorn server:app --port 8770, then python docs/screenshots/take.py"""
import pathlib

from playwright.sync_api import sync_playwright

URL, OUT = "http://localhost:8770/", pathlib.Path(__file__).parent


def fresh(page):
    page.goto(URL)
    page.click("#reset")
    page.wait_for_selector("#j-gap:has-text('0.500 g')")
    page.evaluate("document.fonts.ready")
    page.evaluate("document.getElementById('heard').textContent = ''")  # hide the "Demo reset." note


def shot(page, name, el=None):
    page.wait_for_timeout(400)
    (page.locator(el) if el else page).screenshot(path=str(OUT / name))
    print("saved", name)


def reweigh(page):
    page.select_option("#kind", "scrap")
    page.fill("#wt", "3")
    page.check("#photo")
    page.click("#save")
    page.click("#j-todo [data-confirm]")
    page.wait_for_selector("#j-gap:has-text('0.000 g')")


with sync_playwright() as p:
    b = p.chromium.launch()
    d = b.new_page(viewport={"width": 1400, "height": 900})
    fresh(d)
    shot(d, "01-gap.png")
    shot(d, "05-agent-explains.png", "section.phone >> nth=0")
    reweigh(d)
    shot(d, "02-reweighed.png")
    d.click("[data-approve=jeweller]")
    d.click("[data-approve=karigar]")
    d.click("#pay")
    d.wait_for_selector("#j-settle .status.good")
    shot(d, "03-paid.png")
    d.click("#tamper")
    d.wait_for_selector("#chain.bad")
    shot(d, "04-broken-seal.png")
    fresh(d)
    d.click("[data-job=J-1043]")
    d.wait_for_selector("#j-due.risk")
    shot(d, "08-late-order.png")

    m = b.new_page(viewport={"width": 375, "height": 812}, device_scale_factor=2, is_mobile=True, has_touch=True)
    fresh(m)
    shot(m, "09-phone-gap.png")
    for name, lang in (("06-karigar-hindi.png", "hi"), ("07-karigar-kannada.png", "kn")):
        m.click(f"[data-lang={lang}]")
        m.evaluate("document.querySelector('#h-k').closest('section').scrollIntoView()")
        shot(m, name)
    m.click("[data-job=J-1043]")
    m.wait_for_selector("#k-due.risk")
    m.evaluate("document.querySelector('#h-k').closest('section').scrollIntoView()")
    shot(m, "10-phone-late-order.png")
    m.click("[data-lang=hi]")
    b.close()
