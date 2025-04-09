import openai
import os
import time
import configparser
from tqdm import tqdm

# 📌 Konfigurációs fájlok beolvasása
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPENAI_CONFIG_PATH = os.path.join(BASE_DIR, "config", "openai_config.ini")
CREDENTIALS_PATH = os.path.join(BASE_DIR, "config", "credentials.ini")

config = configparser.ConfigParser()
config.read(OPENAI_CONFIG_PATH)

secrets = configparser.ConfigParser()
secrets.read(CREDENTIALS_PATH)

# 📌 OpenAI API beállítások
OPENAI_API_KEY = secrets.get("OPENAI", "API_KEY", fallback=None)
MODEL_ENG = config.get("OPENAI", "MODEL_ENG", fallback="gpt-4-turbo")
MODEL_JPN = config.get("OPENAI", "MODEL_JPN", fallback="gpt-4o")
BATCH_SIZE = config.getint("OPENAI", "BATCH_SIZE", fallback=3)

if not OPENAI_API_KEY:
    raise ValueError("❌ Nincs megadva OpenAI API kulcs a credentials.ini konfigurációban!")

# 📌 Projektmappa és 'data' mappa meghatározása
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")


def find_ass_file(directory):
    """
    Megkeresi az elsődleges .ass fájlt a következő prioritási sorrendben:
    1. Japán felirat ('_japanese' a fájlnévben)
    2. Angol felirat ('_english' a fájlnévben)
    """
    japanese_file = None
    english_file = None

    for file in os.listdir(directory):
        if file.endswith(".ass"):
            if "_japanese" in file:
                japanese_file = os.path.join(directory, file)
            elif "_english" in file:
                english_file = os.path.join(directory, file)
    return japanese_file or english_file


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

# 📌 OpenAI API kulcs beállítása
openai.api_key = OPENAI_API_KEY


def translate_with_openai(text_list):
    """OpenAI segítségével fordítja le a megadott szövegeket egy egyedi elválasztó használatával."""
    delimiter = "|||"
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": (
                    "You are a professional translator. "
                    "Translate each of the following lines to natural, idiomatic, and conversational Hungarian. "
                    "Avoid literal translations. Instead, preserve the intended tone, mood, and context of each line. "
                    f"Output the translations exactly separated by '{delimiter}'. "
                    "Do not output anything else."
                )},
                {"role": "user", "content": delimiter.join(text_list)}
            ]
        )
        output = response.choices[0].message.content.strip()
        translations = output.split(delimiter)
        translations = [t.strip() for t in translations if t.strip()]
        if len(translations) != len(text_list):
            print(f"⚠️ Warning: Expected {len(text_list)} translations, but got {len(translations)}.")
        return translations
    except Exception as e:
        print(f"⚠️ OpenAI API hiba: {e}")
        return text_list


# 📌 ASS fájl beolvasása
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 🌟 Beszélőnevek kigyűjtése a fordítás előtt
unique_names = set()
for line in lines:
    if line.strip().lower().startswith("dialogue:"):
        parts = line.split(",", 10)
        if len(parts) >= 2:
            name = parts[4].strip()
            if name:
                unique_names.add(name)

translated_lines = []
batch = []
original_prefixes = []

# Számoljuk meg a fordítandó "Dialogue:" sorokat a progress bar pontos működéséhez
dialogue_count = sum(1 for line in lines if line.strip().lower().startswith("dialogue:"))

with tqdm(total=dialogue_count, desc="🔄 Fordítás folyamatban", unit="sor") as pbar:
    for line in lines:
        if line.strip().lower().startswith("dialogue:"):
            parts = line.split(",", 10)
            if len(parts) >= 2:
                name = parts[4].strip()
                # név már korábban kigyűjtve

            last_comma_idx = line.rfind(",,")
            if last_comma_idx != -1:
                text_to_translate = line[last_comma_idx + 2:].strip()
                prefix = line[:last_comma_idx + 2]

                batch.append(text_to_translate)
                original_prefixes.append(prefix)

                if len(batch) >= BATCH_SIZE:
                    translated_batch = translate_with_openai(batch)
                    for j in range(min(len(original_prefixes), len(translated_batch))):
                        translated_lines.append(f"{original_prefixes[j]}{translated_batch[j]}\n")
                        pbar.update(1)
                    batch = []
                    original_prefixes = []
                    time.sleep(1)
            else:
                translated_lines.append(line)
                pbar.update(1)
        else:
            translated_lines.append(line)
    if batch:
        translated_batch = translate_with_openai(batch)
        for j in range(min(len(original_prefixes), len(translated_batch))):
            translated_lines.append(f"{original_prefixes[j]}{translated_batch[j]}\n")
            pbar.update(1)
        time.sleep(1)

# 📌 Fordított fájl mentése
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(translated_lines)

# 📌 Nevek mentése a 'userdata' mappába
USERDATA_DIR = os.path.join(PROJECT_DIR, "userdata")
os.makedirs(USERDATA_DIR, exist_ok=True)
speaker_output_path = os.path.join(USERDATA_DIR, "speakers.txt")

with open(speaker_output_path, "w", encoding="utf-8") as f:
    for name in sorted(unique_names):
        f.write(name + "\n")

print(f"✅ Fordítás kész! Mentve: {OUTPUT_FILE}")
print(f"📂 Beszélőnevek mentve: {speaker_output_path}")
