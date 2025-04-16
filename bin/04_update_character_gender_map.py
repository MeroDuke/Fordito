import sys
import os
import json
import hashlib

# 📌 Mappák és fájlnevek

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, PROJECT_DIR)
from scripts.logger import log_user_print, log_tech

USERDATA_DIR = os.path.join(PROJECT_DIR, "userdata")
DATA_DIR = os.path.join(PROJECT_DIR, "data")

SPEAKER_FILE = os.path.join(USERDATA_DIR, "speakers.txt")
COLOR_MAP_FILE = os.path.join(USERDATA_DIR, "character_color_map.json")

LOG_NAME = "04_update_styles"

# 📌 Szín világosságának becslése
def perceived_brightness(r, g, b):
    return (r * 299 + g * 587 + b * 114) / 1000

BRIGHTNESS_THRESHOLD = 180

if os.path.exists(COLOR_MAP_FILE):
    with open(COLOR_MAP_FILE, "r", encoding="utf-8") as f:
        color_map = json.load(f)
else:
    color_map = {}

if os.path.exists(SPEAKER_FILE):
    with open(SPEAKER_FILE, "r", encoding="utf-8") as f:
        for line in f:
            name = line.strip()
            if name and name not in color_map:
                h = hashlib.md5(name.encode()).hexdigest()
                r = int(h[0:2], 16)
                g = int(h[2:4], 16)
                b = int(h[4:6], 16)
                if perceived_brightness(r, g, b) > BRIGHTNESS_THRESHOLD:
                    r = int(r * 0.5)
                    g = int(g * 0.5)
                    b = int(b * 0.5)
                color_map[name] = f"&H{b:02X}{g:02X}{r:02X}&"
                log_tech(LOG_NAME, f"Szín generálva: {name} -> {color_map[name]}")

with open(COLOR_MAP_FILE, "w", encoding="utf-8") as f:
    json.dump(color_map, f, ensure_ascii=False, indent=2)
log_user_print(LOG_NAME, f"✅ Szítérkép frissítve: {COLOR_MAP_FILE}")
log_tech(LOG_NAME, f"Szítérkép mentve: {COLOR_MAP_FILE}")

input_ass = None
for file in os.listdir(DATA_DIR):
    if file.endswith("_hungarian.ass"):
        input_ass = os.path.join(DATA_DIR, file)
        break

if not input_ass:
    log_user_print(LOG_NAME, "❌ Nem található _hungarian.ass fájl a data mappában.")
    log_tech(LOG_NAME, "Nem találtunk fordított .ass fájlt a data/ alatt.")
    exit(1)

with open(input_ass, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.strip().lower().startswith("title:"):
        lines[i] = "Title: Akihabarai Könyvespolc - AI fordítás\n"
        log_tech(LOG_NAME, "Title mező frissítve.")
        break

output_ass = input_ass.replace(".ass", "_styled.ass")

format_line = None
styles_start = None
styles_end = None
for i, line in enumerate(lines):
    if line.strip().lower() == "[v4+ styles]":
        styles_start = i
    elif styles_start and line.strip().startswith("["):
        styles_end = i
        break
    elif styles_start and line.lower().startswith("format:"):
        format_line = line.strip()

style_default = None
for line in lines[styles_start:styles_end]:
    if line.lower().startswith("style: default"):
        style_default = line.strip()
        break

new_styles = []
if style_default and format_line:
    parts = style_default.split(",")
    format_fields = [f.strip().lower() for f in format_line.split(":", 1)[1].split(",")]
    color_idx = format_fields.index("outlinecolour")
    name_idx = 0
    fontname_idx = format_fields.index("fontname")
    for character, color in color_map.items():
        new_parts = parts.copy()
        new_parts[name_idx] = f"Char_{character}"
        new_parts[color_idx] = color
        new_parts[fontname_idx] = "Trebuchet MS"
        style_line = "Style: " + ",".join(new_parts) + "\n"
        new_styles.append(style_line)
        log_tech(LOG_NAME, f"Style generálva: {style_line.strip()}")

existing_styles = set(line.split(":",1)[1].split(",")[0].strip() for line in lines[styles_start:styles_end] if line.lower().startswith("style:"))
style_insert_idx = styles_end if styles_end else len(lines)
for new_style in new_styles:
    style_name = new_style.split(":",1)[1].split(",")[0].strip()
    if style_name not in existing_styles:
        lines.insert(style_insert_idx, new_style)
        style_insert_idx += 1
        log_tech(LOG_NAME, f"Style beszúrva: {style_name}")

updated_lines = []
for line in lines:
    if line.strip().lower().startswith("dialogue:"):
        parts = line.split(",", 10)
        if len(parts) >= 4:
            name = parts[4].strip()
            style_name = f"Char_{name}"
            parts[3] = style_name
            updated_line = ",".join(parts)
            updated_lines.append(updated_line)
            log_tech(LOG_NAME, f"Stílus frissítve: {name} -> {style_name}")
        else:
            updated_lines.append(line)
    else:
        updated_lines.append(line)

with open(output_ass, "w", encoding="utf-8") as f:
    f.writelines(updated_lines)
log_user_print(LOG_NAME, f"✅ ASS fájl frissítve: {output_ass}")
log_tech(LOG_NAME, f"ASS fájl mentve: {output_ass}")
