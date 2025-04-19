import json
import requests
import os
import re

# --- Projekt gyökér elérése ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TORRENT_JSON_PATH = os.path.join(ROOT_DIR, "userdata", "downloaded_torrents.json")
CACHE_OUTPUT = os.path.join(ROOT_DIR, "userdata", "context_preview.json")

# --- Egyszerű címkinyerés az episode_id mezőből ---
def extract_series_title(episode_id: str) -> str:
    # Alap stratégia: az első " - " előtti rész
    return episode_id.split(" - ")[0].strip()

# --- Jikan API hívás ---
def search_anime_jikan(title: str) -> dict:
    url = f"https://api.jikan.moe/v4/anime?q={title}&limit=1"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"[HIBA] API hívás sikertelen: {response.status_code}")
        return {}
    data = response.json()
    if not data.get("data"):
        print("[INFO] Nincs találat a Jikan API-n.")
        return {}
    return data["data"][0]  # Első találat

# --- Fő logika ---
def main():
    if not os.path.exists(TORRENT_JSON_PATH):
        print(f"Nem található: {TORRENT_JSON_PATH}")
        return

    with open(TORRENT_JSON_PATH, encoding="utf-8") as f:
        torrents = json.load(f)

    first_key = next(iter(torrents))
    episode_id = torrents[first_key].get("episode_id", first_key)
    title_guess = extract_series_title(episode_id)

    print(f"[INFO] Keresett cím: {title_guess}")

    anime_data = search_anime_jikan(title_guess)
    if not anime_data:
        return

    output = {
        "input_title": title_guess,
        "matched_title": anime_data.get("title"),
        "title_japanese": anime_data.get("title_japanese"),
        "mal_id": anime_data.get("mal_id"),
        "genres": [g["name"] for g in anime_data.get("genres", [])],
        "synopsis": anime_data.get("synopsis")
    }

    print("\n[OUTPUT] Kontextus előnézet:")
    for k, v in output.items():
        print(f"{k}: {v}")

    os.makedirs(os.path.dirname(CACHE_OUTPUT), exist_ok=True)
    with open(CACHE_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n[SUCCESS] Mentve ide: {CACHE_OUTPUT}")

if __name__ == "__main__":
    main()