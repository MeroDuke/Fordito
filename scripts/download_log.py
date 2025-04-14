import json
from pathlib import Path
from datetime import datetime

# Naplófájl elérési útja (projekt/userdata/downloaded_torrents.json)
LOG_PATH = Path(__file__).resolve().parents[1] / "userdata" / "downloaded_torrents.json"

def load_download_log() -> dict:
    if LOG_PATH.exists():
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_download_log(log: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

def is_episode_already_downloaded(episode_id: str) -> bool:
    log = load_download_log()
    return episode_id in log

def add_episode_to_log(episode_id: str, title: str, hash_: str, source_url: str) -> None:
    log = load_download_log()
    log[episode_id] = {
        "title": title,
        "hash": hash_,
        "added_at": datetime.now().isoformat(),
        "source": source_url
    }
    save_download_log(log)
