import sys
import openai
import os
import time
import configparser
import json
import re
from tqdm import tqdm

# 📌 Projektmappa logoláshoz
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

# 📌 Log modul
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, PROJECT_DIR)
from scripts.logger import log_user_print, log_tech
from scripts.estimate_translation_cost import (
    extract_lines_from_ass,
    extract_translatables,
    estimate_token_count_precise,
    calculate_cost,
    log_cost_estimate
)

LOG_NAME = "03_translate_subtitles"

# 📌 Konfigurációs fájlok beolvasása
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPENAI_CONFIG_PATH = os.path.join(BASE_DIR, "config", "openai_config.ini")
CREDENTIALS_PATH = os.path.join(BASE_DIR, "config", "credentials.ini")

if not os.path.exists(CREDENTIALS_PATH):
    log_user_print(LOG_NAME, "❌ Nincs meg a 'credentials.ini'! Kérlek, másold le a 'credentials_template.ini'-t, nevezd át, és töltsd ki.")
    log_tech(LOG_NAME, "Hiányzik a config/credentials.ini fájl.")
    sys.exit(1)

config = configparser.ConfigParser()
config.read(OPENAI_CONFIG_PATH)

secrets = configparser.ConfigParser()
secrets.read(CREDENTIALS_PATH)

# 📌 OpenAI API beállítások
OPENAI_API_KEY = secrets.get("OPENAI", "API_KEY", fallback=None)
MODEL_ENG = config.get("OPENAI", "MODEL_ENG", fallback="gpt-4-turbo")
MODEL_JPN = config.get("OPENAI", "MODEL_JPN", fallback="gpt-4o")
BATCH_SIZE = config.getint("OPENAI", "BATCH_SIZE", fallback=3)
USE_CONTEXT = config.getboolean("OPENAI", "USE_CONTEXT", fallback=False)
log_tech(LOG_NAME, f"Kontextus használata engedélyezve: {USE_CONTEXT}")

if not OPENAI_API_KEY:
    log_user_print(LOG_NAME, "❌ Nincs megadva OpenAI API kulcs a credentials.ini konfigurációban!")
    log_tech(LOG_NAME, "OpenAI API kulcs hiányzik a konfigurációból.")
    raise ValueError("❌ Nincs megadva OpenAI API kulcs a credentials.ini konfigurációban!")

# 📌 Projektmappa és 'data' mappa meghatározása
DATA_DIR = os.path.join(PROJECT_DIR, "data")

# 📌 Kontextus betöltése, ha van és engedélyezett
CONTEXT_PATH = os.path.join(PROJECT_DIR, "userdata", "context_preview.json")
CONTEXT_DATA = None
if USE_CONTEXT:
    if os.path.exists(CONTEXT_PATH):
        try:
            with open(CONTEXT_PATH, encoding="utf-8") as f:
                CONTEXT_DATA = json.load(f)
        except Exception as e:
            CONTEXT_DATA = None

def build_contextual_prompt(delimiter: str) -> str:
    context_lines = []
    if CONTEXT_DATA:
        if CONTEXT_DATA.get("synopsis"):
            context_lines.append(f"Anime synopsis: {CONTEXT_DATA['synopsis']}")
        if CONTEXT_DATA.get("genres"):
            context_lines.append(f"Genres: {', '.join(CONTEXT_DATA['genres'])}")
        if CONTEXT_DATA.get("characters"):
            formatted = [
                f"{c.get('name')} ({c.get('name_japanese')})"
                for c in CONTEXT_DATA["characters"]
                if c.get("name") and c.get("name_japanese")
            ]
            if formatted:
                context_lines.append(f"Character list: {', '.join(formatted)}")
    context_text = "\n".join(context_lines)
    return (
        "You are a professional translator.\n"
        + context_text + "\n"
        + "Translate each of the following lines to natural, idiomatic, and conversational Hungarian.\n"
        + f"Output the translations exactly separated by '{delimiter}'.\n"
        + "Do not output anything else."
    )

def find_ass_file(directory):
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
    log_user_print(LOG_NAME, "⚠️ Nincs megfelelő .ass fájl a 'data' mappában.")
    log_tech(LOG_NAME, "Hiányzik .ass fájl a data mappából.")
    exit(1)

# 📌 Modell kiválasztása fájlnév alapján
if "_english" in INPUT_FILE:
    MODEL = MODEL_ENG
elif "_japanese" in INPUT_FILE:
    MODEL = MODEL_JPN
else:
    log_user_print(LOG_NAME, "❌ Ismeretlen nyelvi fájlformátum.")
    log_tech(LOG_NAME, f"Ismeretlen fájlnév: {INPUT_FILE}")
    exit(1)

# 📌 Költségbecslés a fájl alapján (valósághű modell szerint)
ass_lines = extract_lines_from_ass(INPUT_FILE)
translatables = extract_translatables(ass_lines)
input_tokens, output_tokens = estimate_token_count_precise(translatables, MODEL, BATCH_SIZE)
cost = calculate_cost(input_tokens, output_tokens, MODEL)
log_user_print(LOG_NAME, f"💡 Becsült fordítási költség: {cost:.2f} USD ({input_tokens} input token, {output_tokens} output token, modell: {MODEL})")
log_cost_estimate(MODEL, input_tokens, output_tokens, cost, accepted=True)

# 📌 Kimeneti fájl neve
OUTPUT_FILE = INPUT_FILE.replace("_english", "_hungarian").replace("_japanese", "_hungarian")

log_user_print(LOG_NAME, f"✅ Talált feliratfájl: {INPUT_FILE}")
log_user_print(LOG_NAME, f"✅ Használt modell: {MODEL}")
log_user_print(LOG_NAME, f"✅ A fordított fájl neve: {OUTPUT_FILE}")
log_tech(LOG_NAME, f"Input fájl: {INPUT_FILE} | Modell: {MODEL} | Output: {OUTPUT_FILE}")

openai.api_key = OPENAI_API_KEY

def translate_with_openai(text_list):
    from scripts.logger import log_tech
    delimiter = "|||"
    system_prompt = build_contextual_prompt(delimiter)
    log_tech(LOG_NAME, "[DEBUG] Átadott system prompt:")
    log_tech(LOG_NAME, system_prompt)
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": delimiter.join(text_list)}
            ]
        )
        # 🔢 Valós tokenhasználat logolása
        if hasattr(response, "usage"):
            log_tech(LOG_NAME, f"[USAGE] prompt: {response.usage['prompt_tokens']}, completion: {response.usage['completion_tokens']}, total: {response.usage['total_tokens']}")

        output = response.choices[0].message.content.strip()
        translations = output.split(delimiter)
        translations = [t.strip() for t in translations if t.strip()]
        if len(translations) != len(text_list):
            log_tech(LOG_NAME, f"⚠️ Warning: Expected {len(text_list)} translations, but got {len(translations)}.")
        return translations
    except Exception as e:
        log_user_print(LOG_NAME, f"⚠️ OpenAI API hiba: {e}")
        log_tech(LOG_NAME, f"OpenAI kivétel: {e}")
        return text_list

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

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
original_prefixes = []  # ezt kellett hozzáadni!
dialogue_count = sum(1 for line in lines if line.strip().lower().startswith("dialogue:"))

with tqdm(total=dialogue_count, desc="🔄 Fordítás folyamatban", unit="sor") as pbar:
    for line in lines:
        if not line.strip().lower().startswith("dialogue:"):
            translated_lines.append(line)
            continue

        # 1) Vedd ki az első {…} override blokkot, ha van
        parts0 = line.rstrip("\n").split(",", 9)
        text_field = parts0[9]
        m = re.match(r"^(\{[^}]*\})", text_field)
        override = m.group(1) if m else ""
        remainder = text_field[len(override):]

        # 2) Ha ez valódi shape‐rajzoló tag (\p<szám>), ugord át
        if re.search(r"\\p\\d", override):
            translated_lines.append(line)
            pbar.update(1)
            continue

        # 3) Készítsd el a prefixet, amiben benne van már az override is
        prefix = ",".join(parts0[:9]) + "," + override

        # 4) A maradék szöveget küldd a fordítóhoz
        if "\\N" in remainder:
            chunks = [c.strip() for c in remainder.split("\\N")]
            # fordítjuk az egymás utánival
            translations = translate_with_openai(chunks)
            # újrasortörjük \N-nel
            new_text = "\\N".join(translations)
            # visszarakjuk a prefix + override blokk elé
            translated_lines.append(f"{prefix}{new_text}\n")
            pbar.update(1)
            continue

        # nincs sortörés, batch-be küldjük
        text_to_translate = remainder.strip()
        batch.append(text_to_translate)
        original_prefixes.append(prefix)

        # 5) Ha elértük a BATCH_SIZE-t, flush-oljuk
        if len(batch) >= BATCH_SIZE:
            translated_batch = translate_with_openai(batch)
            for j in range(min(len(original_prefixes), len(translated_batch))):
                translated_lines.append(f"{original_prefixes[j]}{translated_batch[j]}\n")
                pbar.update(1)
            batch = []
            original_prefixes = []
            time.sleep(1)

    # Fájl végén a maradék batch-t is flush-oljuk
    if batch:
        translated_batch = translate_with_openai(batch)
        for j in range(min(len(original_prefixes), len(translated_batch))):
            translated_lines.append(f"{original_prefixes[j]}{translated_batch[j]}\n")
            pbar.update(1)
        time.sleep(1)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(translated_lines)
log_user_print(LOG_NAME, f"✅ Fordítás kész! Mentve: {OUTPUT_FILE}")
log_tech(LOG_NAME, f"Fordított állomány mentve: {OUTPUT_FILE}")

USERDATA_DIR = os.path.join(PROJECT_DIR, "userdata")
os.makedirs(USERDATA_DIR, exist_ok=True)
speaker_output_path = os.path.join(USERDATA_DIR, "speakers.txt")

with open(speaker_output_path, "w", encoding="utf-8") as f:
    for name in sorted(unique_names):
        f.write(name + "\n")
log_user_print(LOG_NAME, f"📂 Beszélőnevek mentve: {speaker_output_path}")
log_tech(LOG_NAME, f"Beszélőnevek exportálva: {speaker_output_path}")
