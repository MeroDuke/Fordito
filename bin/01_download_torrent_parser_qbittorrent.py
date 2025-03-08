import os
import xml.etree.ElementTree as ET
import requests
import qbittorrentapi
import time

# 📌 RSS feed URL – Automatikusan beállítva
RSS_FEED_URL = "https://nyaa.si/?page=rss&c=0_0&f=2"

# 📌 Szűrési feltételek
KEYWORDS = ["1080p", "multisub"]
TRUSTED_TAG = "Yes"

# 📌 Minőségi szűrés – Csak a legjobb verziót tölti le
PREFERRED_QUALITY = ["WEB-DL", "HEVC", "EAC3"]

# 📌 qBittorrent Web API beállítások
QB_HOST = "localhost"
QB_PORT = 8080  # Ha módosítottad, változtasd meg!
QB_USERNAME = "pythonteszt"
QB_PASSWORD = "pythonteszt"

# 📌 Projektmappa és 'data' mappa meghatározása
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")

# 📌 Csatlakozás qBittorrenthez
qb = qbittorrentapi.Client(host=QB_HOST, port=QB_PORT, username=QB_USERNAME, password=QB_PASSWORD)
qb.auth_log_in()

def download_rss():
    """ Letölti a legfrissebb RSS feedet """
    response = requests.get(RSS_FEED_URL)
    if response.status_code == 200:
        return response.content
    else:
        print(f"⚠️ Hiba történt az RSS letöltésekor: {response.status_code}")
        return None

def parse_rss(rss_data):
    """ Kiolvassa az RSS-ből a megfelelő torrenteket """
    root = ET.fromstring(rss_data)
    namespaces = {'nyaa': 'https://nyaa.si/xmlns/nyaa'}

    best_torrent = None

    for item in root.findall(".//item"):
        title = item.find("title").text
        link = item.find("link").text
        trusted = item.find("nyaa:trusted", namespaces)

        if all(keyword.lower() in title.lower() for keyword in KEYWORDS) and (trusted is not None and trusted.text == TRUSTED_TAG):
            if any(q in title for q in PREFERRED_QUALITY):
                best_torrent = {"title": title, "link": link}

    return best_torrent

def add_torrent_to_qbittorrent(torrent_url):
    """ Hozzáadja a torrentet a qBittorrent klienshez a 'data' mappába """
    try:
        qb.torrents_add(urls=torrent_url, save_path=DATA_DIR)  # 📌 Itt adjuk meg a letöltési mappát
        print(f"✅ Torrent sikeresen hozzáadva a qBittorrenthez: {torrent_url}")
        print(f"📁 Letöltési mappa: {DATA_DIR}")

        # 📌 Várunk egy pár másodpercet, hogy a torrent biztosan regisztrálódjon
        time.sleep(10)  # 10 másodperc várakozási idő

    except Exception as e:
        print(f"⚠️ Hiba történt a torrent hozzáadásakor: {e}")

def get_torrents_list():
    """ Lekéri az összes torrentet a qBittorrent kliensből """
    try:
        torrents = qb.torrents_info()  # Lekérjük a torrentek listáját
        if torrents:
            for torrent in torrents:
                print(f"🎯 {torrent.name} | Állapot: {torrent.state} | Haladás: {torrent.progress * 100:.2f}%")
                if torrent.progress == 1.0:  # 100%-os letöltés
                    print(f"✅ A torrent letöltése befejeződött: {torrent.name}")
                    return True  # Ha a torrent letöltése befejeződött, visszatérünk True-val
        else:
            print("⚠️ Nincsenek aktív torrentek a qBittorrent kliensben.")
    except Exception as e:
        print(f"⚠️ Hiba történt a torrentek lekérésekor: {e}")

    return False

# 📌 Főprogram
if __name__ == "__main__":
    print("🔄 RSS feed letöltése...")
    rss_data = download_rss()

    if rss_data:
        print("🔍 RSS fájl elemzése...")
        best_torrent = parse_rss(rss_data)

        if best_torrent:
            print(f"🎯 **Legjobb torrent kiválasztva:** {best_torrent['title']}")
            add_torrent_to_qbittorrent(best_torrent["link"])
        else:
            print("⚠️ **Nem találtunk megfelelő torrentet!**")

    # 📌 Folyamatos figyelés a torrent letöltési állapotáról
    print("🔄 Letöltés figyelése...")
    while True:
        download_complete = get_torrents_list()
        if download_complete:
            print("✅ A letöltés befejeződött. Folytathatjuk a munkát a fájllal.")
            break
        time.sleep(5)  # Várjunk 5 másodpercet az újabb ellenőrzés előtt
