import os
import json

# 📌 Mappák és fájlnevek
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
USERDATA_DIR = os.path.join(PROJECT_DIR, "userdata")
DATA_DIR = os.path.join(PROJECT_DIR, "data")

SPEAKER_FILE = os.path.join(USERDATA_DIR, "speakers.txt")
GENDER_MAP_FILE = os.path.join(USERDATA_DIR, "character_gender_map.json")
COLOR_MAP_FILE = os.path.join(USERDATA_DIR, "gender_color_map.json")

# 📌 character_gender_map betöltése
gender_map = {}
if os.path.exists(GENDER_MAP_FILE):
    with open(GENDER_MAP_FILE, "r", encoding="utf-8") as f:
        gender_map = json.load(f)

# 📌 Új nevek hozzáadása speakers.txt alapján
if os.path.exists(SPEAKER_FILE):
    with open(SPEAKER_FILE, "r", encoding="utf-8") as f:
        for line in f:
            name = line.strip()
            if name and name not in gender_map:
                gender_map[name] = "unknown"

# 📌 character_gender_map mentése
with open(GENDER_MAP_FILE, "w", encoding="utf-8") as f:
    json.dump(gender_map, f, ensure_ascii=False, indent=2)

print(f"✅ Névlista frissítve: {GENDER_MAP_FILE}")

# 📌 gender_color_map betöltése
with open(COLOR_MAP_FILE, "r", encoding="utf-8") as f:
    color_map = json.load(f)

# 📌 Hungarian .ass fájl keresése
input_ass = None
for file in os.listdir(DATA_DIR):
    if file.endswith("_hungarian.ass"):
        input_ass = os.path.join(DATA_DIR, file)
        break

if not input_ass:
    print("❌ Nem található _hungarian.ass fájl a data mappában.")
    exit(1)

# 📌 Fájl beolvasása
with open(input_ass, "r", encoding="utf-8") as f:
    lines = f.readlines()

output_ass = input_ass.replace(".ass", "_styled.ass")

# 📌 Styles szekció beazonosítása
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

# 📌 Style: Default sor beolvasása
style_default = None
for line in lines[styles_start:styles_end]:
    if line.lower().startswith("style: default"):
        style_default = line.strip()
        break

# 📌 Új Style sorok generálása
new_styles = []
if style_default and format_line:
    parts = style_default.split(",")
    format_fields = [f.strip().lower() for f in format_line.split(":", 1)[1].split(",")]
    color_idx = format_fields.index("primarycolour")
    name_idx = 0
    for gender, color in color_map.items():
        new_parts = parts.copy()
        new_parts[name_idx] = f"Char_{gender.capitalize()}"
        new_parts[color_idx] = color
        new_styles.append("Style: " + ",".join(new_parts) + "\n")

# 📌 Beszúrjuk az új Style-okat, ha még nem léteznek
existing_styles = set(line.split(":",1)[1].split(",")[0].strip() for line in lines[styles_start:styles_end] if line.lower().startswith("style:"))
style_insert_idx = styles_end if styles_end else len(lines)
for new_style in new_styles:
    style_name = new_style.split(":",1)[1].split(",")[0].strip()
    if style_name not in existing_styles:
        lines.insert(style_insert_idx, new_style)
        style_insert_idx += 1

# 📌 Dialogue sorok frissítése
updated_lines = []
for line in lines:
    if line.strip().lower().startswith("dialogue:"):
        parts = line.split(",", 10)
        if len(parts) >= 4:
            name = parts[4].strip()
            gender = gender_map.get(name, "unknown")
            style_name = f"Char_{gender.capitalize()}"
            parts[3] = style_name
            updated_line = ",".join(parts)
            updated_lines.append(updated_line)
        else:
            updated_lines.append(line)
    else:
        updated_lines.append(line)

# 📌 Fájl mentése
with open(output_ass, "w", encoding="utf-8") as f:
    f.writelines(updated_lines)

print(f"✅ ASS fájl frissítve: {output_ass}")