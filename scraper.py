from playwright.sync_api import sync_playwright
import time
from logger import log
from datetime import datetime
import re
import csv
import os
import bot
import traceback
amount = None
online = None


URL = "https://skinrave.gg/"
def open_page(browser):
    page = browser.new_page()

    print("Načítám stránku...")

    page.goto(
    URL,
    wait_until="domcontentloaded",
    timeout=30000
    )
    page.wait_for_timeout(5000)

    print("Stránka načtena!")

    return page

CSV_FILE = "kick_links.csv"


def save_kick_link(link):
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            pass

    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        existing = {row[0] for row in csv.reader(f) if row}

    if link not in existing:
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([link])

        print(f"🎥 New Kick link: {link}")


def start_scraper(callback):
    print("SCRAPER FUNCTION STARTED")
    global amount, online

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)
        page = open_page(browser)
        

        rain_active = False
        last_reload = time.time()
        

        while True:
            print(f"Loop {datetime.now().strftime('%H:%M:%S')}")
            try:
                try:
                    print("Reading chat...")

                    messages = page.locator("#chat-container p").all_inner_texts()

                    print("Chat loaded.")
                    messages.reverse()

                    for msg in messages:

                            
                        

                        links = re.findall(
                            r"(?:https?://)?(?:www\.)?kick\.com/[^\s]+",
                            msg,
                            flags=re.IGNORECASE
                        )

                        

                    for link in links:
                        if not link.startswith("http"):
                            link = "https://" + link
                        save_kick_link(link)

                except Exception:
                    traceback.print_exc()

                # Aktualizace potu
                try:
                    print("Reading pot...")
                    amount = page.get_by_test_id("rain-pot").inner_text(timeout=1000)
                    print("Pot loaded.")
                except:
                    traceback.print_exc()
                    amount = None

                # Kontrola rainu
                join_button = page.locator('button[aria-label="join-rain-button"]')

                try:
                    print("Checking rain...")

                    count = join_button.count()
                    print(f"Join count: {count}")

                    if count > 0:
                        visible = join_button.first.is_visible()
                        enabled = join_button.first.is_enabled()
                        text = join_button.first.inner_text()

                        print(f"Visible: {visible}")
                        print(f"Enabled: {enabled}")
                        print(f"Text: {text}")

                    current_rain = count > 0

                    print(f"current_rain = {current_rain}")
                    print("Rain checked.")

                except Exception:
                    traceback.print_exc()
                    current_rain = False

                # Online hráči
                if current_rain:
                    try:
                        print("Reading online...")
                        online = page.locator(
                            "span.text-sm.font-medium.text-white"
                        ).nth(1).inner_text(timeout=1000)
                        print("Online loaded.")
                    except:
                        traceback.print_exc()
                        online = None
                else:
                    online = None

                # Log při začátku rainu
                if current_rain and not rain_active:

                    rain_active = True
                    bot.last_rain = datetime.now()
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
                print("Calling callback...")
                callback(amount, online, current_rain)
                print("Callback finished.")
                print("Sleeping...")
                print(" ")
                time.sleep(5)
                print("Awake.")
                if time.time() - last_reload > 1800:
                    print("Refreshing page...")

                    try:
                        page.close()
                    except Exception:
                        traceback.print_exc()

                    page = open_page(browser)
                    last_reload = time.time()
                
            except Exception as e:
                print("SCRAPER ERROR:", repr(e))
                time.sleep(1)
       