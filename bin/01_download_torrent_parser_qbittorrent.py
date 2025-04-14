# bin/01_download_torrent_parser_qbittorrent.py

import os
import xml.etree.ElementTree as ET
import requests
import qbittorrentapi
import time
import configparser
import sys

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

# 📌 Alap RSS feed URL – Ez maradhat hardcode-olva, ha nem akarjuk configból
RSS_FEED_URL = "https://nyaa.si/?page=rss&c=0_0&f=2"
TRUSTED_TAG = "Yes"

# 📌 qBittorrent Web API beállítások
QB_HOST = config.get("QBITTORRENT", "HOST", fallback="localhost")
QB_PORT = config.getint("QBITTORRENT", "PORT", fallback=8080)
QB_USERNAME = config.get("QBITTORRENT", "USERNAME")
QB_PASSWORD = config.get("QBITTORRENT", "PASSWORD")

# 📌 Projektmappa és 'data' mappa meghatározása
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")

# 📌 Csatlakozás qBittorrenthez
qb = qbittorrentapi.Client(host=QB_HOST, port=QB_PORT, username=QB_USERNAME, password=QB_PASSWORD)
qb.auth_log_in()

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
    best_torrent = None
    for item in root.findall(".//item"):
        title = item.find("title").text
        link = item.find("link").text
        trusted = item.find("nyaa:trusted", namespaces)

        episode_id = extract_episode_id(title)
        if episode_id and is_episode_already_downloaded(episode_id):
            print(f"🔁 Skip – már letöltve: {episode_id}")
            continue

        title_lc = title.lower()
        if TARGET_TORRENT_MATCH and not all(term in title_lc for term in TARGET_TORRENT_MATCH):
            continue

        if all(keyword.lower() in title_lc for keyword in KEYWORDS) and (trusted is not None and trusted.text == TRUSTED_TAG):
            if any(q in title for q in PREFERRED_QUALITY):
                print(f"🌟 Kiválasztott torrent: {title}")
                best_torrent = {"title": title, "link": link, "episode_id": episode_id}
                break
    return best_torrent

def add_torrent_to_qbittorrent(torrent_url):
    try:
        qb.torrents_add(urls=torrent_url, save_path=DATA_DIR)
        print(f"✅ Torrent sikeresen hozzáadva a qBittorrenthez: {torrent_url}")
        time.sleep(5)
        torrents = sorted(qb.torrents_info(), key=lambda t: t.added_on, reverse=True)
        if torrents:
            latest_torrent = torrents[0]
            print(f"🔑 Követett torrent: {latest_torrent.name} | Hash: {latest_torrent.hash}")
            return latest_torrent.hash
        else:
            print("⚠️ Nem találtunk torrentet a listában a hozzáadás után.")
            return None
    except Exception as e:
        print(f"⚠️ Hiba történt a torrent hozzáadásakor: {e}")
        return None

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

# 📌 Főprogram
if __name__ == "__main__":
    print("🔄 RSS feed letöltése...")
    rss_data = download_rss()

    if rss_data:
        print("🔍 RSS fájl elemzése...")
        best_torrent = parse_rss(rss_data)

        if best_torrent:
            print(f"🌟 **Legjobb torrent kiválasztva:** {best_torrent['title']}")
            torrent_hash = add_torrent_to_qbittorrent(best_torrent["link"])
            if torrent_hash:
                print("🔄 Letöltés figyelése...")
                while True:
                    if get_torrent_status(torrent_hash):
                        print("✅ A letöltés befejeződött. Folytathatjuk a munkát a fájllal.")

                        if best_torrent.get("episode_id"):
                            add_episode_to_log(
                                episode_id=best_torrent["episode_id"],
                                title=best_torrent["title"],
                                hash_=torrent_hash,
                                source_url=best_torrent["link"]
                            )
                        break
                    time.sleep(5)
        else:
            print("⚠️ **Nem találtunk megfelelő torrentet!**")