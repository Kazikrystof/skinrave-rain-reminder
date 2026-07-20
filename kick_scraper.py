from playwright.sync_api import sync_playwright
import time
import csv
import os
import re

CSV_FILE = "kick_links.csv"


def load_links():
    if not os.path.exists(CSV_FILE):
        return set()

    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        return {row[0] for row in reader if row}


def save_link(link):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([link])


def start_kick_scraper():
    known_links = load_links()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        page.goto("https://skinrave.gg")

        print("Kick scraper started.")

        while True:
            try:
                text = page.locator("body").inner_text()
                

                print(text[:1000])  # vypíše prvních 1000 znaků stránky

                links = re.findall(
                    r"(?:https?://)?(?:www\.)?kick\.com/[^\s]+",
                    text
                )

                for link in links:
                    if not link.startswith("http"):
                        link = "https://" + link

                    if link not in known_links:
                        known_links.add(link)
                        save_link(link)
                        print(f"New Kick link found: {link}")

            except Exception as e:
                print(f"Kick scraper error: {e}")

            time.sleep(30)