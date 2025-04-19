import json
import requests
import os
import re
from datetime import datetime

# --- Projekt gyökér elérése ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TORRENT_JSON_PATH = os.path.join(ROOT_DIR, "userdata", "downloaded_torrents.json")
CACHE_OUTPUT = os.path.join(ROOT_DIR, "userdata", "context_preview.json")

# --- Egyszerű címkinyerés az episode_id mezőből ---
def extract_series_title(episode_id: str) -> str:
    return episode_id.split(" - ")[0].strip()

# --- Anilist API (GraphQL) ---
def search_anime_anilist(title: str) -> dict:
    query = '''
    query ($search: String) {
      Media(search: $search, type: ANIME) {
        id
        title {
          romaji
          native
        }
        description(asHtml: false)
        genres
        characters(sort: [ROLE, RELEVANCE], perPage: 25) {
          edges {
            role
            node {
              name {
                full
                native
              }
            }
          }
        }
      }
    }
    '''

    variables = {"search": title}
    url = "https://graphql.anilist.co"
    response = requests.post(url, json={"query": query, "variables": variables})

    if response.status_code != 200:
        print(f"[HIBA] Anilist API hívás sikertelen: {response.status_code}")
        return {}

    data = response.json()
    media = data.get("data", {}).get("Media", {})
    return media

# --- Fő logika ---
def main():
    if not os.path.exists(TORRENT_JSON_PATH):
        print(f"Nem található: {TORRENT_JSON_PATH}")
        return

    with open(TORRENT_JSON_PATH, encoding="utf-8") as f:
        torrents = json.load(f)

    # Legfrissebb entry kiválasztása az added_at mező alapján
    latest_entry = max(torrents.items(), key=lambda x: x[1].get("added_at", ""))
    episode_id = latest_entry[1].get("episode_id", latest_entry[0])
    title_guess = extract_series_title(episode_id)

    print(f"[INFO] Keresett cím: {title_guess}")

    anime = search_anime_anilist(title_guess)
    if not anime:
        return

    characters = []
    for edge in anime.get("characters", {}).get("edges", []):
        node = edge.get("node", {})
        name_data = node.get("name", {})
        characters.append({
            "name": name_data.get("full"),
            "name_japanese": name_data.get("native"),
            "role": edge.get("role", "Unknown")
        })

    output = {
        "input_title": title_guess,
        "matched_title": anime.get("title", {}).get("romaji"),
        "title_japanese": anime.get("title", {}).get("native"),
        "anilist_id": anime.get("id"),
        "genres": anime.get("genres", []),
        "synopsis": anime.get("description"),
        "source_language": "ja" if anime.get("title", {}).get("native") else "en",
        "characters": characters
    }

    print("\n[OUTPUT] Kontextus előnézet:")
    for k, v in output.items():
        if k != "characters":
            print(f"{k}: {v}")
    print(f"characters: {len(characters)} db lekérve")

    os.makedirs(os.path.dirname(CACHE_OUTPUT), exist_ok=True)
    with open(CACHE_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n[SUCCESS] Mentve ide: {CACHE_OUTPUT}")

if __name__ == "__main__":
    main()
