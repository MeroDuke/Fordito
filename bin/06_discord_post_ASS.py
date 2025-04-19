import os
import sys
import json
from configparser import ConfigParser
import requests

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, PROJECT_DIR)

from scripts.logger import log_user_print, log_tech
LOG_NAME = "06_discord_post"

CONFIG_FILENAME = 'discord_config.ini'
DATA_DIRNAME = 'data'
TORRENT_DB_FILENAME = 'downloaded_torrents.json'
USERDATA_DIRNAME = 'userdata'

def load_config():
    cfg_path = os.path.join(PROJECT_DIR, 'config', CONFIG_FILENAME)
    if not os.path.isfile(cfg_path):
        log_user_print(LOG_NAME, f"❌ Konfig fájl nem található: {cfg_path}")
        log_tech(LOG_NAME, "Config file missing.")
        sys.exit(1)

    parser = ConfigParser()
    try:
        with open(cfg_path, 'r', encoding='utf-8') as f:
            parser.read_file(f)
        webhook_url = parser.get('discord', 'webhook_url')
        startup_message = parser.get('discord', 'startup_message', fallback="")
        log_tech(LOG_NAME, "Config betöltve sikeresen.")
        return webhook_url, startup_message
    except Exception as e:
        log_user_print(LOG_NAME, f"❌ Hiba a konfig beolvasása során: {e}")
        log_tech(LOG_NAME, f"Config read error: {e}")
        sys.exit(1)

def send_text_message(webhook_url, message):
    if not message:
        return
    payload = {"content": message}
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code in (200, 204):
            log_user_print(LOG_NAME, "🟢 Szöveges üzenet elküldve a Discordra.")
        else:
            log_user_print(LOG_NAME, f"❌ Hiba történt ({response.status_code}): {response.text}")
            log_tech(LOG_NAME, f"Webhook POST failed: {response.status_code} | {response.text}")
            sys.exit(1)
    except requests.RequestException as e:
        log_user_print(LOG_NAME, f"❌ Nem sikerült kapcsolódni a Discordhoz: {e}")
        log_tech(LOG_NAME, f"RequestException: {e}")
        sys.exit(1)

def find_subtitle_file(data_dir):
    for fname in os.listdir(data_dir):
        if fname.lower().endswith('.ass') and '_hungarian' in fname.lower():
            subtitle_path = os.path.join(data_dir, fname)
            log_user_print(LOG_NAME, f"📄 Feliratfájl megtalálva: {subtitle_path}")
            return subtitle_path
    log_user_print(LOG_NAME, "❌ Nem található .ass fájl a 'data' mappában.")
    log_tech(LOG_NAME, "Subtitle file not found in data directory.")
    sys.exit(1)

def match_torrent(project_root, subtitle_filename):
    db_path = os.path.join(project_root, USERDATA_DIRNAME, TORRENT_DB_FILENAME)
    if not os.path.isfile(db_path):
        log_tech(LOG_NAME, f"Torrent adatbázis nem található: {db_path}")
        return None

    with open(db_path, 'r', encoding='utf-8') as f:
        try:
            torrents = json.load(f)
        except json.JSONDecodeError as e:
            log_tech(LOG_NAME, f"JSON betöltési hiba: {e}")
            return None

    subtitle_lower = subtitle_filename.lower()

    for key, value in torrents.items():
        if not isinstance(value, dict):
            continue
        title = value.get("title", "").lower()
        episode_id = value.get("episode_id", "").lower()
        key_str = str(key).lower()

        if title and title in subtitle_lower:
            log_tech(LOG_NAME, f"Torrent match by title: {title}")
            return value.get("source")
        if episode_id and episode_id in subtitle_lower:
            log_tech(LOG_NAME, f"Torrent match by episode_id: {episode_id}")
            return value.get("source")
        if key_str and key_str in subtitle_lower:
            log_tech(LOG_NAME, f"Torrent match by key: {key_str}")
            return value.get("source")

    log_tech(LOG_NAME, "Nem sikerült torrenthez párosítani a feliratot.")
    return None

def main():
    webhook_url, startup_message = load_config()
    send_text_message(webhook_url, startup_message)

    data_path = os.path.join(PROJECT_DIR, DATA_DIRNAME)
    if not os.path.isdir(data_path):
        log_user_print(LOG_NAME, f"❌ Nincs '{DATA_DIRNAME}' mappa a projekt gyökerében.")
        log_tech(LOG_NAME, "Data mappa hiányzik.")
        sys.exit(1)

    file_path = find_subtitle_file(data_path)
    filename = os.path.basename(file_path)
    torrent_url = match_torrent(PROJECT_DIR, filename)
    extra_text = f"\nForrás torrent: {torrent_url}" if torrent_url else "\n🔍 Forrás torrent nem található."

    with open(file_path, 'rb') as f:
        payload = {"content": f"Új feliratfájl érkezett: **{filename}**{extra_text}"}
        files = {"file": (filename, f)}
        try:
            response = requests.post(webhook_url, data=payload, files=files)
            if response.status_code in (200, 204):
                log_user_print(LOG_NAME, "✅ Feliratfájl sikeresen elküldve a Discordra.")
                log_tech(LOG_NAME, f"Felirat feltöltve: {filename}")
            else:
                log_user_print(LOG_NAME, f"❌ Hiba történt ({response.status_code}): {response.text}")
                log_tech(LOG_NAME, f"File POST failed: {response.status_code} | {response.text}")
                sys.exit(1)
        except requests.RequestException as e:
            log_user_print(LOG_NAME, f"❌ Nem sikerült kapcsolódni a Discordhoz: {e}")
            log_tech(LOG_NAME, f"File upload exception: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main()
