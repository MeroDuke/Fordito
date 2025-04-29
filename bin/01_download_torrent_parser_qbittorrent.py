import os
import xml.etree.ElementTree as ET
import requests
import time
import configparser
import sys
import json

# 📌 Projekt gyökérmappa felvétele az elérési útba
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, PROJECT_DIR)

# 📌 Elérési út hozzáadása a scripts mappához
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))
from episode_utils import extract_episode_id
from download_log import is_episode_already_downloaded, add_episode_to_log
from scripts.logger import log_user, log_tech, log_user_print
from scripts.qbittorrent_client import create_client_from_config

# 📌 Konfiguráció beolvasása a config.ini fájlból
CONFIG_PATH = os.path.join(PROJECT_DIR, "config", "qbittorrent_config.ini")
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

# 📌 RSS szűrési feltételek (configból)
KEYWORDS = [k.strip() for k in config.get("FILTER", "KEYWORDS", fallback="1080p, multisub").split(",")]
PREFERRED_QUALITY = [q.strip() for q in config.get("FILTER", "PREFERRED_QUALITY", fallback="WEB-DL, HEVC, EAC3").split(",")]
TARGET_TORRENT_MATCH = [t.strip().lower() for t in config.get("DOWNLOAD", "TARGET_TORRENT_MATCH", fallback="").split(",") if t.strip()]

# 📌 TRUSTED_TAG beolvasása konfigból
trusted_tag_raw = config.get("DOWNLOAD", "TRUSTED_TAG", fallback="Yes").strip().lower()
TRUSTED_TAG = "Yes" if trusted_tag_raw == "yes" else "No"

# 📌 RSS feed URL a TRUSTED_TAG alapján
RSS_FEED_URL = "https://nyaa.si/?page=rss&c=0_0&f=2" if TRUSTED_TAG == "Yes" else "https://nyaa.si/?page=rss"

# 📌 Projektmappa és log/adata mappák
SCRIPT_DIR = CURRENT_DIR
DATA_DIR = os.path.join(PROJECT_DIR, "data")
USERDATA_DIR = os.path.join(PROJECT_DIR, "userdata")
TORRENT_LOG_PATH = os.path.join(USERDATA_DIR, "downloaded_torrents.json")

# 📌 Log név
LOG_NAME = "01_download_torrent_parser_qbittorrent"

# 📌 qBittorrent kliens inicializálása
log_tech(LOG_NAME, "🔗 qBittorrent API kapcsolat inicializálása...")
client = create_client_from_config(CONFIG_PATH)
log_tech(LOG_NAME, "✅ qBittorrent API kapcsolat sikeres.")
log_user(LOG_NAME, "✅ qBittorrent API kapcsolat sikeres.")

def load_downloaded_hashes():
    if os.path.exists(TORRENT_LOG_PATH):
        with open(TORRENT_LOG_PATH, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                log_tech(LOG_NAME, "⚠️ Hiba: JSON dekódolás sikertelen a logfájlban.")
                return {}
    log_tech(LOG_NAME, "🔍 Letöltési napló nem található. ")
    return {}

def is_title_already_downloaded(episode_id):
    downloaded = load_downloaded_hashes()
    found = any(key == episode_id or entry.get("episode_id") == episode_id for key, entry in downloaded.items())
    if found:
        log_tech(LOG_NAME, f"❌ Epizód már le van töltve: {episode_id}")
    return found

def add_episode_id_to_log_stub(episode_id, title, source_url):
    from datetime import datetime
    downloaded = load_downloaded_hashes()
    used_keys = set(downloaded.keys())
    new_id = 1
    while str(new_id) in used_keys:
        new_id += 1
    downloaded[str(new_id)] = {
        "episode_id": episode_id,
        "title": title,
        "hash": "",
        "source": source_url,
        "added_at": datetime.utcnow().isoformat()
    }
    with open(TORRENT_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(downloaded, f, indent=2, ensure_ascii=False)
    log_tech(LOG_NAME, f"✍️ Epizód ideiglenesen naplózva: {episode_id} -> {title}")
    return str(new_id)

def update_episode_log_hash(entry_id, new_hash):
    downloaded = load_downloaded_hashes()
    if entry_id not in downloaded:
        downloaded[entry_id] = {
            "episode_id": entry_id,
            "title": "UNKNOWN",
            "hash": new_hash,
            "source": "UNKNOWN"
        }
    else:
        downloaded[entry_id]["hash"] = new_hash
        if "episode_id" not in downloaded[entry_id]:
            downloaded[entry_id]["episode_id"] = entry_id
    with open(TORRENT_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(downloaded, f, indent=2, ensure_ascii=False)
    log_tech(LOG_NAME, f"🔄 Epizód hash frissítve: {entry_id} -> {new_hash}")

def get_torrent_status(torrent_hash):
    try:
        torrent = client.get_torrent_status_by_hash(torrent_hash)
        if torrent:
            print(f"\r🌟 {torrent.name} | Állapot: {torrent.state} | Haladás: {torrent.progress * 100:.2f}%", end="", flush=True)
            log_tech(LOG_NAME, f"🌟 Torrent állapot: {torrent.name} | {torrent.state} | {torrent.progress * 100:.2f}%")
            if torrent.progress == 1.0:
                print()
                print(f"✅ A torrent letötése befejeződött: {torrent.name}")
                log_user(LOG_NAME, f"✅ Torrent letötve: {torrent.name}")
                return True
        else:
            print("⚠️ A torrent nem található.")
            log_tech(LOG_NAME, "⚠️ Torrent nem található.")
    except Exception as e:
        print(f"⚠️ Hiba történt a torrent lekérdezésekor: {e}")
        log_tech(LOG_NAME, f"⚠️ Torrent lekérési hiba: {e}")
    return False

def download_rss():
    response = requests.get(RSS_FEED_URL)
    if response.status_code == 200:
        print("🔄 RSS feed letöltve.")
        log_tech(LOG_NAME, "🔄 RSS feed letöltve.")
        return response.content
    else:
        print(f"⚠️ Hiba történt az RSS letöltésekor: {response.status_code}")
        log_tech(LOG_NAME, f"⚠️ Hiba az RSS letöltésénél: {response.status_code}")
        return None

def parse_rss(rss_data):
    root = ET.fromstring(rss_data)
    namespaces = {'nyaa': 'https://nyaa.si/xmlns/nyaa'}
    downloaded = load_downloaded_hashes()

    def extract_info_hash_from_magnet(magnet_url: str) -> str:
        import re
        match = re.search(r'btih:([a-fA-F0-9]+)', magnet_url)
        return match.group(1).lower() if match else None

    for item in root.findall(".//item"):
        title = item.find("title").text
        link = item.find("link").text
        trusted = item.find("nyaa:trusted", namespaces)
        episode_id = extract_episode_id(title)
        title_lc = title.lower()

        if episode_id and is_title_already_downloaded(episode_id):
            continue

        if TARGET_TORRENT_MATCH and not all(term in title_lc for term in TARGET_TORRENT_MATCH):
            continue
        if TRUSTED_TAG == "Yes" and not (trusted is not None and trusted.text == "Yes"):
            continue
        if not all(keyword.lower() in title_lc for keyword in KEYWORDS):
            continue
        if not any(q in title for q in PREFERRED_QUALITY):
            continue

        new_hash = extract_info_hash_from_magnet(link)
        if any(entry.get("source") == link for entry in downloaded.values()):
            print(f"⚠️ Torrent már le lett töltve ezzel a linkkel: {title}")
            log_tech(LOG_NAME, f"❌ Skip: duplikált linkkel {title}")
            continue
        if new_hash and any(entry.get("hash", "").lower() == new_hash for entry in downloaded.values()):
            print(f"⚠️ Torrent már le lett töltve ugyanazzal a hash-sel: {title}")
            log_tech(LOG_NAME, f"❌ Skip: duplikált hash-sel {title}")
            continue

        log_user(LOG_NAME, f"✨ Torrent kiválasztva: {title}")

        if episode_id:
            temp_id = add_episode_id_to_log_stub(episode_id, title, link)
            return {"title": title, "link": link, "episode_id": episode_id, "log_id": temp_id}
        else:
            return {"title": title, "link": link, "episode_id": None, "log_id": None}

    log_user(LOG_NAME, "ℹ️ Nincs megfelelő torrent az RSS-ben.")
    return None

def add_torrent_to_qbittorrent(torrent_url, expected_title):
    try:
        client.add_torrent_by_url(torrent_url, DATA_DIR)
        print(f"✅ Torrent sikeresen hozzáadva: {torrent_url}")
        log_user(LOG_NAME, f"✅ Torrent hozzáadva: {torrent_url}")
        time.sleep(5)
        matching = [t for t in client.get_torrents_info() if expected_title.lower() in t.name.lower()]
        torrent = matching[0] if matching else sorted(client.get_torrents_info(), key=lambda t: t.added_on, reverse=True)[0]
        if torrent:
            print(f"🔑 Torrent felismerve: {torrent.name} | Hash: {torrent.hash}")
            log_tech(LOG_NAME, f"🔑 Torrent felismerve: {torrent.name} | Hash: {torrent.hash}")
            return torrent.hash
        print(f"⚠️ Nem találtuk meg a hozzáadott torrentet: {expected_title}")
        log_tech(LOG_NAME, f"⚠️ Nem találtuk a hozzáadott torrentet: {expected_title}")
        return None
    except Exception as e:
        print(f"⚠️ Hiba történt a torrent hozzáadásakor: {e}")
        log_tech(LOG_NAME, f"⚠️ Hiba torrent hozzáadásakor: {e}")
        return None

if __name__ == "__main__":
    log_user(LOG_NAME, "🔄 Script indul, RSS feed letöltés kezdődik...")
    rss_data = download_rss()
    if rss_data:
        log_user_print(LOG_NAME, "🔍 RSS fájl elemzése...")
        log_tech(LOG_NAME, "🔍 RSS adat beolvasva, feldolgozás következik...")
        best_torrent = parse_rss(rss_data)
        if best_torrent:
            log_user_print(LOG_NAME, f"📅 Torrent kiválasztva: {best_torrent['title']}")
            torrent_hash = add_torrent_to_qbittorrent(best_torrent["link"], best_torrent["title"])
            if torrent_hash:
                print("🔄 Letöltés figyelése...")
                log_tech(LOG_NAME, f"🔄 Letöltés elindult hash-sel: {torrent_hash}")
                while True:
                    if get_torrent_status(torrent_hash):
                        print("✅ A letöltés befejeződött.")
                        if best_torrent.get("log_id"):
                            update_episode_log_hash(best_torrent["log_id"], torrent_hash)
                        elif best_torrent.get("episode_id"):
                            add_episode_to_log(
                                episode_id=best_torrent["episode_id"],
                                title=best_torrent["title"],
                                hash_=torrent_hash,
                                source_url=best_torrent["link"]
                            )
                        break
                    time.sleep(5)
        else:
            print("ℹ️ A legfrissebb torrent már le van töltve. Nincs új tartalom.")
            log_user(LOG_NAME, "ℹ️ A legfrissebb torrent már le van töltve. Nincs új tartalom.")