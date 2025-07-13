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
    elif file.endswith("_hungarian.ass") and not file.endswith("_styled.ass") and not file.endswith("_fixed.ass"):
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

# 📌 Finomított megoldás: csak a sign_generic sorokra alkalmazzuk a cserét, minden mást érintetlenül hagyunk
output_lines = []
for en_line, hu_line in zip(english_lines, hungarian_lines):
    if en_line.lower().startswith("dialogue:") and "sign_generic" in en_line.lower():
        match = re.match(r"^(.*,,\s*)(\{.*?\})(.*)$", en_line)
        if match:
            prefix = match.group(1)
            override = match.group(2)
            en_text = match.group(3)
            hu_text = hu_line.split(',,', 1)[1] if ",," in hu_line else ""

            # 📌 Új logika: Pozícióhűen visszaállítjuk a \N-ket, ha lehet
            if "\\N" in en_text:
                en_chunks = en_text.split("\\N")
                num_chunks = len(en_chunks)
                hu_chunks = hu_text.strip().split("\\N")

                if len(hu_chunks) == num_chunks:
                    hu_text_with_breaks = "\\N".join(hu_chunks)
                else:
                    hu_words = hu_text.strip().split()
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

            output_lines.append(f"{prefix}{override}{hu_text_with_breaks}\n")
        else:
            output_lines.append(hu_line)
    else:
        output_lines.append(hu_line)

# 📌 Hozzáfűzzük a maradék magyar sorokat, ha volt extra
if len(hungarian_lines) > len(english_lines):
    output_lines.extend(hungarian_lines[len(english_lines):])

# 📌 Mentés
with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(output_lines)

print(f"✅ Fix kész: {output_file.name}")
