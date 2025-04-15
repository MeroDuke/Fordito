import os
import xml.etree.ElementTree as ET
import requests
import qbittorrentapi
import time
import configparser
import sys
import json

# 📌 Elérési út hozzáadása a scripts mappához
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))
from episode_utils import extract_episode_id
from download_log import is_episode_already_downloaded, add_episode_to_log

# 📌 Konfiguráció beolvasása a config.ini fájlból
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "qbittorrent_config.ini")
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
if TRUSTED_TAG == "Yes":
    RSS_FEED_URL = "https://nyaa.si/?page=rss&c=0_0&f=2"
else:
    RSS_FEED_URL = "https://nyaa.si/?page=rss"

# 📌 qBittorrent Web API beállítások
QB_HOST = config.get("QBITTORRENT", "HOST", fallback="localhost")
QB_PORT = config.getint("QBITTORRENT", "PORT", fallback=8080)
QB_USERNAME = config.get("QBITTORRENT", "USERNAME")
QB_PASSWORD = config.get("QBITTORRENT", "PASSWORD")

# 📌 Projektmappa és 'data' mappa meghatározása
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
USERDATA_DIR = os.path.join(PROJECT_DIR, "userdata")
TORRENT_LOG_PATH = os.path.join(USERDATA_DIR, "downloaded_torrents.json")

# 📌 Csatlakozás qBittorrenthez
qb = qbittorrentapi.Client(host=QB_HOST, port=QB_PORT, username=QB_USERNAME, password=QB_PASSWORD)
qb.auth_log_in()

def load_downloaded_hashes():
    if os.path.exists(TORRENT_LOG_PATH):
        with open(TORRENT_LOG_PATH, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def is_title_already_downloaded(episode_id):
    downloaded = load_downloaded_hashes()
    return any(
        key == episode_id or entry.get("episode_id") == episode_id
        for key, entry in downloaded.items()
    )

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

def get_torrent_status(torrent_hash):
    try:
        torrent = qb.torrents_info(torrent_hashes=torrent_hash)
        if torrent:
            t = torrent[0]
            print(f"🌟 {t.name} | Állapot: {t.state} | Haladás: {t.progress * 100:.2f}%")
            if t.progress == 1.0:
                print(f"✅ A torrent letöltése befejeződött: {t.name}")
                return True
        else:
            print("⚠️ A torrent nem található.")
    except Exception as e:
        print(f"⚠️ Hiba történt a torrent lekérdezésekor: {e}")
    return False

def download_rss():
    response = requests.get(RSS_FEED_URL)
    if response.status_code == 200:
        return response.content
    else:
        print(f"⚠️ Hiba történt az RSS letöltésekor: {response.status_code}")
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
            continue
        if new_hash and any(entry.get("hash", "").lower() == new_hash for entry in downloaded.values()):
            print(f"⚠️ Torrent már le lett töltve ugyanazzal a hash-sel: {title}")
            continue

        print(f"🌟 Kiválasztott torrent: {title}")

        if episode_id:
            temp_id = add_episode_id_to_log_stub(episode_id, title, link)
            return {"title": title, "link": link, "episode_id": episode_id, "log_id": temp_id}
        else:
            return {"title": title, "link": link, "episode_id": None, "log_id": None}

    return None

def add_torrent_to_qbittorrent(torrent_url, expected_title):
    try:
        qb.torrents_add(urls=torrent_url, save_path=DATA_DIR)
        print(f"✅ Torrent sikeresen hozzáadva a qBittorrenthez: {torrent_url}")
        time.sleep(5)

        matching = [t for t in qb.torrents_info() if expected_title in t.name]
        if matching:
            torrent = matching[0]
            print(f"🔑 Követett torrent: {torrent.name} | Hash: {torrent.hash}")
            return torrent.hash

        print(f"⚠️ Nem találtuk meg a hozzáadott torrentet: {expected_title}")
        return None
    except Exception as e:
        print(f"⚠️ Hiba történt a torrent hozzáadásakor: {e}")
        return None

if __name__ == "__main__":
    print("🔄 RSS feed letöltése...")
    rss_data = download_rss()

    if rss_data:
        print("🔍 RSS fájl elemzése...")
        best_torrent = parse_rss(rss_data)

        if best_torrent:
            torrent_hash = add_torrent_to_qbittorrent(best_torrent["link"], best_torrent["title"])
            if torrent_hash:
                print("🔄 Letöltés figyelése...")
                while True:
                    if get_torrent_status(torrent_hash):
                        print("✅ A letöltés befejeződött. Folytathatjuk a munkát a fájllal.")

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
            print("ℹ️ A legfrissebb torrent már le lett töltve korábban. Nincs új tartalom.")
