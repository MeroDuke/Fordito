import subprocess
import datetime
import json
import os
from scripts.logger import log_tech, LOG_ENABLED

# Legyen mindig a futó fájl könyvtára az alap
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Konfiguráció: a futtatandó scriptek relatív útvonala
SCRIPT_PATHS = [
    "bin/01_download_torrent_parser_qbittorrent.py",
    "bin/02_extract_subtitles.py",
    "bin/03_OpenAI_API_ONLY_4-Turbo_translate_ass.py",
    "bin/04_update_character_gender_map.py",
    "bin/05_mkvtool_add_subtitle_to_mkv.py",
    "bin/06_discord_post_ASS.py",
]

# Logfájl útvonala
STATUS_LOG_PATH = "logs/master_status.json"

# Státusz napló írása
def log_status(script_name, status):
    if not LOG_ENABLED:
        return

    os.makedirs(os.path.dirname(STATUS_LOG_PATH), exist_ok=True)

    entry = {
        "script": script_name,
        "status": status,
        "timestamp": datetime.datetime.now().isoformat()
    }

    # Fájl olvasása, ha létezik
    if os.path.exists(STATUS_LOG_PATH):
        try:
            with open(STATUS_LOG_PATH, "r", encoding="utf-8") as f:
                log_data = json.load(f)
        except json.JSONDecodeError:
            log_data = []
    else:
        log_data = []

    log_data.append(entry)

    # Fájl mentése
    with open(STATUS_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)

    log_tech("master_runner", f"Státusz naplózva: {entry}")

# Script futtatása subprocess-szel
def run_script(script_path):
    print(f"\n▶ Futtatás: {script_path}")
    log_status(script_path, "started")
    try:
        result = subprocess.run(["python", script_path], check=False)
        code = result.returncode
        if code == 0:
            print(f"✓ Sikeresen lefutott: {script_path}")
            log_status(script_path, "succeeded")
            return True
        elif code == 1:
            print(f"⚠ Figyelmeztetéssel lefutott: {script_path}")
            log_status(script_path, "warning")
            return True  # nem végzetes hiba
        else:
            print(f"✗ Hiba történt: {script_path} (exit code: {code})")
            log_status(script_path, f"failed (exit code: {code})")
            return False
    except Exception as e:
        print(f"✗ Kivétel történt a futtatás során: {e}")
        log_status(script_path, f"exception: {str(e)}")
        return False

# MASTER főfüggvény
def main():
    print("== MASTER SCRIPT ELINDULT ==")
    for script in SCRIPT_PATHS:
        success = run_script(script)
        if not success:
            print("\n⛔ A futás megszakadt egy hiba miatt.")
            break
    else:
        print("\n✅ Minden script sikeresen lefutott!")

if __name__ == "__main__":
    main()
