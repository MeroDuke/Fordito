import re

def extract_episode_id(title: str) -> str | None:
    """
    Egységesített episode_id-t ad vissza a cím alapján.
    Példa:
      'One Piece - S01E1125'
      'Shingeki no Kyojin - Kanketsu-hen - The Last Attack - Movie' → 'Shingeki no Kyojin - Kanketsu-hen - The Last Attack - Movie - S00E01'
    """
    clean_title = re.sub(r'^\[[^\]]+\]\s*', '', title).strip()

    # 🎥 Movie detektálás
    if re.search(r'\bmovie\b', clean_title, re.IGNORECASE):
        return f"{clean_title} - S00E01"

    # 🎞️ Epizód alapú azonosítás (pl. " - 03")
    match = re.match(r'^(.*?)[\s\-]+(\d{2,4})\b', clean_title)
    if match:
        anime_name = match.group(1).strip()
        episode = int(match.group(2))
        return f"{anime_name} - S01E{episode:02}"

    return None
