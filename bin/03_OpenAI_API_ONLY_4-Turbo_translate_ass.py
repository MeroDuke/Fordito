import openai
import os
import re
import time
import configparser
from tqdm import tqdm

# 📌 Konfiguráció beolvasása a config.ini fájlból
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "openai_config.ini")
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

# 📌 OpenAI API beállítások
OPENAI_API_KEY = config.get("OPENAI", "API_KEY", fallback=None)
MODEL_ENG = config.get("OPENAI", "MODEL_ENG", fallback="gpt-4-turbo")
MODEL_JPN = config.get("OPENAI", "MODEL_JPN", fallback="gpt-4o")
BATCH_SIZE = config.getint("OPENAI", "BATCH_SIZE", fallback=3)

if not OPENAI_API_KEY:
    raise ValueError("❌ Nincs megadva OpenAI API kulcs a konfigurációban!")

# 📌 Projektmappa és 'data' mappa meghatározása
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")


def find_ass_file(directory):
    """
    Megkeresi az első .ass fájlt, amely tartalmazza a '_english' vagy '_japanese' kifejezést a fájlnévben.
    """
    for file in os.listdir(directory):
        if file.endswith(".ass") and ("_english" in file or "_japanese" in file):
            return os.path.join(directory, file)
    return None


# 📌 Keresünk fordítandó fájlt
INPUT_FILE = find_ass_file(DATA_DIR)

if not INPUT_FILE:
    print("⚠️ Nincs megfelelő .ass fájl a 'data' mappában.")
    exit(1)

# 📌 Modell kiválasztása fájlnév alapján
if "_english" in INPUT_FILE:
    MODEL = MODEL_ENG
elif "_japanese" in INPUT_FILE:
    MODEL = MODEL_JPN
else:
    print("❌ Ismeretlen nyelvi fájlformátum.")
    exit(1)

# 📌 Kimeneti fájl neve
OUTPUT_FILE = INPUT_FILE.replace("_english", "_hungarian").replace("_japanese", "_hungarian")

print(f"✅ Talált feliratfájl: {INPUT_FILE}")
print(f"✅ Használt modell: {MODEL}")
print(f"✅ A fordított fájl neve: {OUTPUT_FILE}")


# 📌 OpenAI API kliens inicializálása
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def translate_with_openai(text_list):
    """ OpenAI segítségével fordít szövegeket """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a professional translator. Translate the following text to Hungarian while preserving formatting."},
                {"role": "user", "content": "\n".join(text_list)}
            ]
        )
        return response.choices[0].message.content.split("\n")
    except Exception as e:
        print(f"⚠️ OpenAI API hiba: {e}")
        return text_list


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

                time.sleep(1)
        else:
            translated_lines.append(line)


# 📌 Fordított fájl mentése
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(translated_lines)

print(f"✅ Fordítás kész! Mentve: {OUTPUT_FILE}")
