from playwright.sync_api import sync_playwright
import time
from logger import log

amount = None
online = None

URL = "https://skinrave.gg/"


def start_scraper(callback):
    global amount, online

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("Načítám stránku...")

        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        

        print("Stránka načtena!")
        

        rain_active = False

        while True:
            try:

                # Aktualizace potu
                try:
                    amount = page.get_by_test_id("rain-pot").inner_text(timeout=1000)
                except:
                    amount = None

                # Kontrola rainu
                join_button = page.locator(
                    'button[aria-label="join-rain-button"]'
                )

                current_rain = (
                    join_button.count() > 0
                    and join_button.is_visible()
                )

                # Online hráči
                if current_rain:
                    try:
                        online = page.locator(
                            "span.text-sm.font-medium.text-white"
                        ).nth(1).inner_text(timeout=1000)
                    except:
                        online = None
                else:
                    online = None

                # Log při začátku rainu
                if current_rain and not rain_active:

                    rain_active = True

                    log(
                        f"Rain detected | Amount: ${amount} | Online: {online}"
                    )

                    print("=" * 40)
                    print("🌧️ RAIN DETECTED")
                    print(f"💰 Amount: {amount}")
                    print(f"👥 Online: {online}")
                    print("=" * 40)

                elif not current_rain and rain_active:

                    rain_active = False
                    print("❌ Rain skončil.")

                # Callback až po načtení dat
                callback(amount, online, current_rain)

                time.sleep(1)

            except Exception as e:
                print("SCRAPER ERROR:", repr(e))
                time.sleep(1)