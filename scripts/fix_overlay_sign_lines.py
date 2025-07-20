# scripts/fix_overlay_sign_lines.py

import os
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

# 📌 Az angol és magyar fájlok detektálása
english_file = None
hungarian_file = None
for file in os.listdir(DATA_DIR):
    if file.endswith("_english.ass"):
        english_file = DATA_DIR / file
    elif file.endswith("_hungarian_styled.ass") and not file.endswith("_fixed.ass"):
        hungarian_file = DATA_DIR / file

if not english_file or not hungarian_file:
    print("❌ Nem található mindkét fájl (english és hungarian). Kilépés.")
    exit(1)

output_file = hungarian_file.with_name(hungarian_file.stem + "_fixed.ass")

# 📌 Betöltjük a fájlokat
with open(english_file, encoding="utf-8") as f:
    english_lines = f.readlines()

with open(hungarian_file, encoding="utf-8") as f:
    hungarian_lines = f.readlines()

# 📌 Kinyerjük az angol sign_generic sorokat időbélyeg alapján, listába rendezve
sign_map = {}
for line in english_lines:
    if line.lower().startswith("dialogue:"):
        parts = line.strip().split(",", 9)
        if len(parts) >= 10 and parts[3].strip() == "sign_generic":
            start = parts[1].strip()
            end = parts[2].strip()
            style = parts[3].strip()
            name = parts[4].strip()
            override_match = re.match(r"^(\{.*?\})", parts[9].strip())
            override = override_match.group(1) if override_match else ""
            en_text = parts[9].strip()[len(override):]
            sign_map.setdefault((start, end), []).append((style, override, en_text))

# 📌 Magyar sorok feldolgozása
output_lines = []
match_counters = {}
for hu_line in hungarian_lines:
    if hu_line.lower().startswith("dialogue:"):
        parts = hu_line.strip().split(",", 9)
        if len(parts) >= 10:
            start = parts[1].strip()
            end = parts[2].strip()
            key = (start, end)
            if key in sign_map:
                match_counters.setdefault(key, 0)
                index = match_counters[key]
                if index < len(sign_map[key]):
                    style, override, en_text = sign_map[key][index]
                    match_counters[key] += 1

                    if parts[4].strip():
                        parts[3] = style

                    hu_text = parts[9].strip()

                    if "\\N" in en_text:
                        en_chunks = en_text.split("\\N")
                        num_chunks = len(en_chunks)
                        hu_chunks = hu_text.split("\\N")

                        if len(hu_chunks) == num_chunks:
                            hu_text_with_breaks = "\\N".join(hu_chunks)
                        else:
                            hu_words = hu_text.split()
                            if len(hu_words) >= num_chunks:
                                base = len(hu_words) // num_chunks
                                extras = len(hu_words) % num_chunks
                                sizes = [base + (1 if i < extras else 0) for i in range(num_chunks)]
                                chunks = []
                                idx = 0
                                for size in sizes:
                                    chunk = " ".join(hu_words[idx:idx + size])
                                    chunks.append(chunk)
                                    idx += size
                                hu_text_with_breaks = "\\N".join(chunks)
                            else:
                                hu_text_with_breaks = hu_text.strip()
                    else:
                        hu_text_with_breaks = hu_text.strip()

                    parts[9] = f"{override}{hu_text_with_breaks}"
                    output_lines.append(",".join(parts) + "\n")
                    continue
        output_lines.append(hu_line)
    else:
        output_lines.append(hu_line)

# 📌 Mentés
with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(output_lines)