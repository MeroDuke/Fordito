#!/usr/bin/env python3
import os
import re
from pathlib import Path

# 📌 A data könyvtár, ahol az .ass fájlok vannak
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"

# ———————————————— 
# Fájlok megtalálása
english_file = None
hungarian_file = None
for fn in os.listdir(DATA_DIR):
    if fn.endswith("_english.ass"):
        english_file = DATA_DIR / fn
    elif fn.endswith("_hungarian_styled.ass") and not fn.endswith("_fixed.ass"):
        hungarian_file = DATA_DIR / fn

if not english_file or not hungarian_file:
    print("❌ Nem található mindkét fájl (…_english.ass és …_hungarian_styled.ass)")
    exit(1)

output_file = hungarian_file.with_name(hungarian_file.stem + "_fixed.ass")

# ———————————————— 
# Beolvasás
with open(english_file, encoding="utf-8") as f:
    en_lines = f.readlines()
with open(hungarian_file, encoding="utf-8") as f:
    hu_lines = f.readlines()

# ———————————————— 
# Map építése: kulcs = (start, end), érték = listák az override blokkokból és style-okból
override_map = {}  # (start,end) -> [ "{…}{…}", … ]
style_map    = {}  # (start,end) -> [ "Text", "sign_generic", … ]

for line in en_lines:
    if not line.lower().startswith("dialogue:"):
        continue
    parts = line.rstrip("\n").split(",", 9)
    if len(parts) < 10:
        continue

    start, end = parts[1].strip(), parts[2].strip()
    style      = parts[3].strip()
    text_field = parts[9]

    # Az első egymás után következő {…}{…} blokk kinyerése
    override = ""
    m = re.match(r"(\{[^}]*\})+", text_field)
    if m:
        override = m.group(0)

    if override:
        key = (start, end)
        override_map.setdefault(key, []).append(override)
        style_map   .setdefault(key,    []).append(style)

# ———————————————— 
# Magyar sorok feldolgozása: újraírás override-dal + style-al
output = []
counters = {}  # számláló minden key-hez, hogy idempotens legyen

for hline in hu_lines:
    if not hline.lower().startswith("dialogue:"):
        output.append(hline)
        continue

    parts = hline.rstrip("\n").split(",", 9)
    if len(parts) < 10:
        output.append(hline)
        continue

    start, end = parts[1].strip(), parts[2].strip()
    key = (start, end)

    if key in override_map:
        idx = counters.get(key, 0)
        if idx < len(override_map[key]):
            override = override_map[key][idx]
            style    = style_map[key][idx]
            counters[key] = idx + 1

            # Ha még nincs benne, illesszük be
            if not parts[9].startswith(override):
                # visszaírjuk az override blokkot
                parts[9] = override + parts[9].strip()
            # ha van beszélőnév (parts[4]), akkor style-t is állítjuk
            if parts[4].strip():
                parts[3] = style

            output.append(",".join(parts) + "\n")
            continue

    # semmi sem illeszkedik → eredeti sort írjuk
    output.append(hline)

# ———————————————— 
# Mentés
with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(output)

print(f"✅ Felülírt override-ok visszaillesztve: {output_file}")
