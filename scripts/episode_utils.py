import re

def extract_episode_id(title: str) -> str | None:
    """
    Egységesített episode_id-t ad vissza a cím alapján, pl.
    'One Piece - S01E1125'
    """
    clean_title = re.sub(r'^\[[^\]]+\]\s*', '', title).strip()

    # Keressük a formátumot: "Cím - 1125" vagy hasonlók
    match = re.match(r'^(.*?)[\s\-]+(\d{2,4})\b', clean_title)
    if match:
        anime_name = match.group(1).strip()
        episode = int(match.group(2))
        return f"{anime_name} - S01E{episode:02}"

    return None