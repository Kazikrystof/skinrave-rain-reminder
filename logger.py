from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
LOG_FILE = BASE_DIR / "bot.log"


def log(message, level="INFO"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line = f"[{now}] [{level}] {message}"

    print(line)

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(line + "\n")