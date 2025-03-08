import openai
import os
import re
import time
from tqdm import tqdm

# 📌 OpenAI API beállítások
OPENAI_API_KEY = "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"  # 🔹 A saját API kulcsod
MODEL = "gpt-4-turbo"  # 🔹 OpenAI modell
BATCH_SIZE = 3  # 🔹 Egyszerre ennyi sort küldünk fordításra

# 📌 Fájl elérési utak
INPUT_FILE = r"E:\\felirat_teszt\\2_translate\\subtitle.ass"
OUTPUT_FILE = os.path.splitext(INPUT_FILE)[0] + "_translated.ass"

# 📌 OpenAI API kliens inicializálása
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def translate_with_openai(text_list):
    """ OpenAI GPT-4 Turbo segítségével fordít szövegeket """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a professional translator. Translate the following English subtitles to Hungarian while preserving formatting."},
                {"role": "user", "content": "\n".join(text_list)}
            ]
        )
        return response.choices[0].message.content.split("\n")  # 🔹 Sorokra bontás
    except Exception as e:
        print(f"⚠️ OpenAI API hiba: {e}")
        return text_list  # 🔹 Ha hiba van, visszaadjuk az eredeti szöveget

# 📌 ASS fájl beolvasása és fordítása
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

translated_lines = []
batch = []
original_prefixes = []

with tqdm(total=len(lines), desc="🔄 Fordítás folyamatban", unit="sor") as pbar:
    for line in lines:
        if line.startswith("Dialogue:"):
            last_comma_idx = line.rfind(",,")
            if last_comma_idx != -1:
                text_to_translate = line[last_comma_idx + 2:].strip()
                prefix = line[:last_comma_idx + 2]

                batch.append(text_to_translate)
                original_prefixes.append(prefix)

                if len(batch) >= BATCH_SIZE:
                    translated_batch = translate_with_openai(batch)

                    for j, translated_text in enumerate(translated_batch):
                        translated_lines.append(f"{original_prefixes[j]}{translated_text}\n")
                        pbar.update(1)

                    batch = []
                    original_prefixes = []

                time.sleep(1)  # 🔹 OpenAI API túlterhelés elkerülése
        else:
            translated_lines.append(line)

# 📌 Fordított fájl mentése
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(translated_lines)

print(f"✅ Fordítás kész! Mentve: {OUTPUT_FILE}")
