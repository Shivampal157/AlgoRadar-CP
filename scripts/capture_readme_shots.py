from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path("social_assets")
BASE = "http://127.0.0.1:8501/?embed=true"
REDACT = {
    "_ShivA_10": "nova_cf",
    "shiva0405": "nova_lc",
}


def redact_handles(page) -> None:
    page.evaluate(
        """(pairs) => {
          const walk = (node) => {
            if (node.nodeType === 3) {
              let text = node.textContent || "";
              for (const [from, to] of pairs) text = text.split(from).join(to);
              node.textContent = text;
            }
            for (const child of node.childNodes) walk(child);
          };
          walk(document.body);
          const proto = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value");
          for (const input of document.querySelectorAll("input")) {
            let value = proto.get.call(input);
            for (const [from, to] of pairs) value = value.split(from).join(to);
            proto.set.call(input, value);
          }
        }""",
        list(REDACT.items()),
    )


def fill_handles(page) -> None:
    page.get_by_role("textbox", name="Codeforces handle").fill("_ShivA_10")
    page.get_by_role("textbox", name="LeetCode username").fill("shiva0405")
    page.get_by_role("button", name="Analyze handles").click()
    page.get_by_text("Total solved").wait_for(timeout=90000)
    page.wait_for_selector(".js-plotly-plot", timeout=30000)
    page.wait_for_timeout(2500)


def shot(page, name: str) -> None:
    path = OUT / name
    page.screenshot(path=str(path), full_page=False, type="png")
    print("wrote", path, path.stat().st_size)


def main() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 980}, device_scale_factor=2)
        page.goto(BASE, wait_until="networkidle", timeout=60000)
        page.wait_for_selector(".splash-hero", timeout=30000)
        page.wait_for_timeout(800)
        shot(page, "algoradar-screenshot-landing.png")
        hero = page.locator(".splash-hero")
        if hero.count():
            hero.screenshot(path=str(OUT / "algoradar-hero.png"), type="png")
            print("wrote", OUT / "algoradar-hero.png")
        fill_handles(page)
        page.get_by_text("Combined analysis", exact=True).click()
        page.get_by_text("Total solved").wait_for(timeout=30000)
        page.wait_for_selector(".js-plotly-plot", timeout=30000)
        page.wait_for_timeout(2000)
        redact_handles(page)
        shot(page, "algoradar-screenshot-combined-analysis.png")
        page.get_by_text("Recommendations", exact=True).click()
        page.get_by_text("Platform practice queues").wait_for(timeout=60000)
        page.wait_for_timeout(2000)
        redact_handles(page)
        shot(page, "algoradar-screenshot-recommendations-overview.png")
        page.get_by_text("Solve estimate", exact=True).click()
        page.wait_for_timeout(4000)
        redact_handles(page)
        shot(page, "algoradar-screenshot-solve-probability.png")
        browser.close()


if __name__ == "__main__":
    main()
