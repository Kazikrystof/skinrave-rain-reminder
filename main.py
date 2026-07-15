import threading
import asyncio
import json
from pathlib import Path

from bot import bot, TOKEN, send_rain, send_pot_alert
from scraper import start_scraper

BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "configs.json"

pot_alert_sent = {}
rain_sent = {}


pot_alert_sent = {}
rain_sent = {}

def rain_found(amount, online, current_rain):

    

    if amount is None:
        return

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("❌ Nepodařilo se načíst configs.json")
        return

    for guild_id, guild in data.items():

        channel_id = guild["channel_id"]
        min_pot = guild.get("min_pot")

        if guild_id not in pot_alert_sent:
            pot_alert_sent[guild_id] = False

        if guild_id not in rain_sent:
            rain_sent[guild_id] = False

        

        # ---------------- POT ALERT ----------------

        if min_pot is not None:

            if float(amount) >= float(min_pot):

                

                if not pot_alert_sent[guild_id]:

                    

                    future = asyncio.run_coroutine_threadsafe(
                        send_pot_alert(channel_id, amount, role_id),
                        bot.loop
                    )

                    try:
                        future.result()
                        pot_alert_sent[guild_id] = True
                        
                    except Exception as e:
                        print("❌ Pot Alert chyba:", repr(e))

            else:
                pot_alert_sent[guild_id] = False

        # ---------------- RAIN ----------------

        if current_rain:

            if not rain_sent[guild_id]:

                print("🌧️ Odesílám Rain")

                future = asyncio.run_coroutine_threadsafe(
                    send_rain(channel_id, amount, online),
                    bot.loop
                )

                try:
                    future.result()
                    rain_sent[guild_id] = True
                    print("✅ Rain odeslán")
                except Exception as e:
                    print("❌ Rain chyba:", repr(e))

        else:
            rain_sent[guild_id] = False
    

    if amount is None:
        return

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("❌ Nepodařilo se načíst configs.json")
        return

    for guild_id, guild in data.items():

        channel_id = guild["channel_id"]
        min_pot = guild.get("min_pot")
        role_id = guild.get("pot_role")

        if guild_id not in pot_alert_sent:
            pot_alert_sent[guild_id] = False

        if guild_id not in rain_sent:
            rain_sent[guild_id] = False

        # ---------------- POT ALERT ----------------

        if min_pot is not None:

            if float(amount) >= float(min_pot):

                if not pot_alert_sent[guild_id]:

                    future = asyncio.run_coroutine_threadsafe(
                        send_pot_alert(channel_id, amount),
                        bot.loop
                    )

                    try:
                        future.result()
                        pot_alert_sent[guild_id] = True
                        print(f"💰 Pot alert -> {guild_id}")
                    except Exception as e:
                        print(e)

            else:
                pot_alert_sent[guild_id] = False

        # ---------------- RAIN ----------------

        if current_rain:

            if not rain_sent[guild_id]:

                future = asyncio.run_coroutine_threadsafe(
                    send_rain(channel_id, amount, online),
                    bot.loop
                )

                try:
                    future.result()
                    rain_sent[guild_id] = True
                    print(f"🌧️ Rain -> {guild_id}")
                except Exception as e:
                    print(e)

        else:
            rain_sent[guild_id] = False
    if amount is None:
        return

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("❌ Nepodařilo se načíst configs.json")
        return

    for guild_id, guild in data.items():

        channel_id = guild["channel_id"]
        min_pot = guild.get("min_pot")

        if guild_id not in pot_alert_sent:
            pot_alert_sent[guild_id] = False

        if guild_id not in rain_sent:
            rain_sent[guild_id] = False

        # -----------------------------
        # POT ALERT
        # -----------------------------
        if min_pot is not None:

            if float(amount) >= float(min_pot):

                if not pot_alert_sent[guild_id]:

                    print(f"💰 Pot Alert | Guild {guild_id}")

                    future = asyncio.run_coroutine_threadsafe(
                        send_pot_alert(channel_id, amount),
                        bot.loop
                    )

                    try:
                        future.result()
                        pot_alert_sent[guild_id] = True
                        print("✅ Pot Alert odeslán")
                    except Exception as e:
                        print("❌", e)

            else:
                pot_alert_sent[guild_id] = False

        # -----------------------------
        # RAIN START
        # -----------------------------
        if online is not None:

            if not rain_sent[guild_id]:

                future = asyncio.run_coroutine_threadsafe(
                    send_rain(channel_id, amount, online),
                    bot.loop
                )

                try:
                    future.result()
                    rain_sent[guild_id] = True
                    print("🌧️ Rain notifikace odeslána")
                except Exception as e:
                    print("❌", e)

        else:
            rain_sent[guild_id] = False


threading.Thread(
    target=start_scraper,
    args=(rain_found,),
    daemon=True
).start()

bot.run(TOKEN)