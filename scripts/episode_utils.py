import re

def extract_episode_id(title: str) -> str | None:
    """
    Visszaad egy egységesített episode_id-t a torrent cím alapján,
    pl. 'Kusuriya no Hitorigoto - S02E14'

    Ha nem található, None-t ad vissza.
    """
    # Feltöltőnév eltávolítása, pl. [Erai-raws]
    clean_title = re.sub(r'^\[[^\]]+\]\s*', '', title).strip()

    # Szezon + epizód vagy csak epizód kinyerése
    match = re.search(r'(.*?)(?: -)?\s*(?:S?(\d{1,2})[xE](\d{1,2})|\b(\d{1,3})\b)', clean_title)
    if not match:
        return None

    anime_name = match.group(1).strip()
    if match.group(2) and match.group(3):
        season = int(match.group(2))
        episode = int(match.group(3))
    elif match.group(4):
        season = 1
        episode = int(match.group(4))
    else:
        return None

    return f"{anime_name} - S{season:02}E{episode:02}"
