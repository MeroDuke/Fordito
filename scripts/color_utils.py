import hashlib

BRIGHTNESS_THRESHOLD = 180

def perceived_brightness(r, g, b):
    return (r * 299 + g * 587 + b * 114) / 1000

def generate_color_for_name(name: str) -> str:
    """Egy karakter neve alapján generál egy sötét színt ASS formátumban (&HRRGGBB&)."""
    h = hashlib.md5(name.encode()).hexdigest()
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    if perceived_brightness(r, g, b) > BRIGHTNESS_THRESHOLD:
        r = int(r * 0.5)
        g = int(g * 0.5)
        b = int(b * 0.5)
    return f"&H{b:02X}{g:02X}{r:02X}&"

def is_valid_ass_color_format(color: str) -> bool:
    """Ellenőrzi, hogy a szín formátuma megfelel-e az ASS specifikációnak (&HRRGGBB&)."""
    if not isinstance(color, str):
        return False
    return color.startswith("&H") and color.endswith("&") and len(color) == 9