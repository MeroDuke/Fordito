import sys
import os
import json
import datetime
import configparser

# Projektgyökér hozzáadása az import útvonalakhoz
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))

from logger import log_user, log_user_print, log_tech

# 📌 Projekt gyökérmappa felvétele az elérési útba
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

# --- Beállítások ---
SCRIPT_NAME = "07_cleanup_downloaded_torrents"
CONFIG_PATH = os.path.join(PROJECT_DIR, "config", "cleanup_config.ini")
TORRENT_JSON_PATH = os.path.join(PROJECT_DIR, "userdata", "downloaded_torrents.json")
BACKUP_PATH = os.path.join(PROJECT_DIR, "userdata", "downloaded_torrents_backup.json")

# --- Segédfüggvények ---
def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH, encoding="utf-8")
    return config

def load_torrent_data():
    with open(TORRENT_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def backup_torrent_data():
    with open(TORRENT_JSON_PATH, "r", encoding="utf-8") as src, open(BACKUP_PATH, "w", encoding="utf-8") as dst:
        dst.write(src.read())

def save_torrent_data(data):
    with open(TORRENT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --- Fő folyamat ---
def cleanup_downloaded_torrents():
    config = load_config()
    max_age_days = int(config["cleanup"].get("max_age_days", 0))
    backup_enabled = config["cleanup"].getboolean("backup_enabled", False)

    torrent_data = load_torrent_data()
    now = datetime.datetime.now()

    keys_to_delete = []

    for key, record in torrent_data.items():
        added_at_str = record.get("added_at")
        if not added_at_str:
            # Ha nincs timestamp, most még nem törüljük
            continue
        try:
            added_at = datetime.datetime.fromisoformat(added_at_str)
        except ValueError:
            log_tech(SCRIPT_NAME, f"Hibás dátumformátum: {key} - {added_at_str}")
            continue

        age_days = (now - added_at).days
        if age_days > max_age_days:
            keys_to_delete.append(key)

    if keys_to_delete:
        if backup_enabled:
            backup_torrent_data()
        for key in keys_to_delete:
            log_tech(SCRIPT_NAME, f"Törölt rekord: {key}")
            torrent_data.pop(key, None)
        save_torrent_data(torrent_data)
        log_user_print(SCRIPT_NAME, f"A legrégebbi {len(keys_to_delete)} rekord törölve a downloaded_torrents.json fájlból.")
        log_user(SCRIPT_NAME, f"A legrégebbi {len(keys_to_delete)} rekord törölve a downloaded_torrents.json fájlból.")
    else:
        log_user(SCRIPT_NAME, "Nem volt törölhető rekord.")
        log_user_print(SCRIPT_NAME, "Nem volt törölhető rekord.")

if __name__ == "__main__":
    cleanup_downloaded_torrents()
