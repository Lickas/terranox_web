import os
import time
from playwright.sync_api import sync_playwright

os.makedirs("/home/jules/verification/videos", exist_ok=True)
os.makedirs("/home/jules/verification/screenshots", exist_ok=True)

def run_cuj(page):
    print("Navigating to index.html...")
    page.goto("http://localhost:3000/index.html", wait_until="commit")
    page.wait_for_timeout(2000)

    # Scroll slowly to Gallery to trigger WOW.js animations
    page.evaluate("window.scrollTo(0, document.body.scrollHeight - 1500)")
    page.wait_for_timeout(500)
    page.evaluate("window.scrollTo(0, document.body.scrollHeight - 1000)")
    page.wait_for_timeout(500)
    page.evaluate("window.scrollTo(0, document.body.scrollHeight - 500)")
    page.wait_for_timeout(1000)

    # To properly test hovering/clicking, we need to inject dummy images temporarily
    # into the browser context so the items have dimensions
    page.evaluate("""
        const items = document.querySelectorAll('.gallery-item .portfolio-inner');
        items.forEach((item, idx) => {
            item.innerHTML = `
                <a href="img/about.jpg" data-lightbox="gallery" data-title="Galeria TerraNox ${idx}">
                    <img class="img-fluid w-100 gallery-img" src="img/about.jpg" alt="Galeria">
                    <div class="portfolio-text">
                        <h4 class="text-white mb-4">Ver Imagem</h4>
                        <div class="d-flex">
                            <i class="fa fa-eye text-primary fs-3"></i>
                        </div>
                    </div>
                </a>
            `;
        });
    """)
    page.wait_for_timeout(1000)

    page.screenshot(path="/home/jules/verification/screenshots/gallery_new_design.png")
    print("Saved gallery_new_design.png")

    # The owl-carousel duplicates items for infinite loop. Let's find an active one to hover.
    active_item = page.locator(".owl-item.active .gallery-item").first
    if active_item.is_visible():
        active_item.hover()
        page.wait_for_timeout(1000)
        page.screenshot(path="/home/jules/verification/screenshots/gallery_hover.png")
        print("Saved gallery_hover.png")

        # Click to open lightbox
        active_item.locator("a").click()
        page.wait_for_timeout(1500)

        page.screenshot(path="/home/jules/verification/screenshots/gallery_lightbox_open.png")
        print("Saved gallery_lightbox_open.png")

        # Click next
        next_btn = page.locator(".lb-next")
        if next_btn.is_visible():
            next_btn.click()
            page.wait_for_timeout(1000)
            page.screenshot(path="/home/jules/verification/screenshots/gallery_lightbox_next.png")

        # Close lightbox
        close_btn = page.locator(".lb-close")
        if close_btn.is_visible():
            close_btn.click()
            page.wait_for_timeout(1000)
    else:
        print("Could not find active gallery item.")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir="/home/jules/verification/videos",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        try:
            run_cuj(page)
        finally:
            context.close()
            browser.close()
