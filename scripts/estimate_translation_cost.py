import argparse
import json
import time
import re
from pathlib import Path
import tiktoken
import configparser
import sys
import os

# Logger beállítás
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, PROJECT_DIR)

from scripts.logger import log_user_print, log_tech, LOG_ENABLED
LOG_NAME = "translation_cost_estimate"

# Konfiguráció betöltése
config = configparser.ConfigParser()
config.read("config/config.ini")

MODEL_ENG = config.get("OPENAI", "MODEL_ENG", fallback="gpt-4-turbo")
MODEL_JPN = config.get("OPENAI", "MODEL_JPN", fallback="gpt-4o")

model_price_map = {
    "gpt-4": {"input": 0.01, "output": 0.03},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
    "gpt-4o": {"input": 0.005, "output": 0.015},
}

def clean_text_to_translate(text):
    text = re.sub(r"{.*?}", "", text)
    text = re.sub(r"\\N", " ", text)
    text = re.sub(r"\(.*?\)", "", text)
    return text.strip()

def find_ass_file():
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data"
    if not data_dir.exists():
        log_user_print(LOG_NAME, "❌ A 'data/' mappa nem található.")
        log_tech(LOG_NAME, "Data directory missing.")
        raise FileNotFoundError("A 'data/' mappa nem található a projektgyökérben.")
    for file in data_dir.glob("*.ass"):
        name = file.name.lower()
        if ("_english" in name or "_japanese" in name) and "_hungarian" not in name:
            log_user_print(LOG_NAME, f"✅ Fájl kiválasztva: {file.name}")
            log_tech(LOG_NAME, f"Fordítandó fájl: {file}")
            return file
    log_user_print(LOG_NAME, "❌ Nem található fordítható .ass fájl a 'data/' mappában.")
    log_tech(LOG_NAME, "No translatable .ass file found.")
    raise FileNotFoundError("Nem található fordítható .ass fájl a 'data/' mappában.")

def extract_lines_from_ass(ass_path):
    raw_lines = Path(ass_path).read_text(encoding="utf-8", errors="ignore").splitlines()
    dialogue_lines = [line for line in raw_lines if line.startswith("Dialogue:")]
    lines = []
    for raw in dialogue_lines:
        parts = raw.split(",", 9)
        if len(parts) < 10:
            continue
        start, end, style, text = parts[1], parts[2], parts[3], parts[9]
        lines.append({
            "type": "Dialogue",
            "start": start,
            "end": end,
            "style": style,
            "text": text,
            "text_to_translate": clean_text_to_translate(text)
        })
    log_tech(LOG_NAME, f"Összesen {len(lines)} fordítandó sor beolvasva.")
    return lines

def extract_translatables(lines):
    trans = [line["text_to_translate"] for line in lines if line.get("type") == "Dialogue"]
    log_tech(LOG_NAME, f"Fordítandó sorok száma: {len(trans)}")
    return trans

def estimate_token_count(all_translatables, model):
    enc = tiktoken.encoding_for_model(model)
    input_tokens = sum(len(enc.encode(f"Translate this to Hungarian: {line}")) for line in all_translatables)
    output_tokens = sum(len(enc.encode(line)) for line in all_translatables)
    log_tech(LOG_NAME, f"Token becslés | input: {input_tokens}, output: {output_tokens}")
    return input_tokens, output_tokens

def calculate_cost(input_tokens, output_tokens, model):
    prices = model_price_map.get(model)
    if not prices:
        log_tech(LOG_NAME, f"Ismeretlen modell: {model}")
        raise ValueError(f"Ismeretlen modell: {model}")
    cost = (input_tokens * prices["input"] + output_tokens * prices["output"]) / 1000
    log_tech(LOG_NAME, f"Becsült költség ({model}): {cost:.4f} USD")
    return round(cost, 4)

def log_cost_estimate(model, input_tokens, output_tokens, cost, accepted, log_path=os.path.join(PROJECT_DIR, "logs", "cost_estimate_log.json")):
    log_data = {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost": cost,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "user_accepted": accepted
    }
    if not LOG_ENABLED:
        return

    try:
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            json.dump(log_data, f)
            f.write("\n")
        log_tech(LOG_NAME, f"Költség log mentve: {log_data}")
    except Exception as e:
        log_user_print(LOG_NAME, f"⚠ Nem sikerült menteni a logot: {e}")
        log_tech(LOG_NAME, f"Log mentési hiba: {e}")

def detect_model_from_filename(filename):
    fname = filename.lower()
    if "_english" in fname:
        return MODEL_ENG
    elif "_japanese" in fname:
        return MODEL_JPN
    else:
        return "gpt-4"  # fallback

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--yes", action="store_true", help="Automatikus elfogadás költség esetén")
    args = parser.parse_args()

    try:
        ass_path = find_ass_file()
    except FileNotFoundError:
        sys.exit(1)

    model = detect_model_from_filename(ass_path.name)
    log_tech(LOG_NAME, f"Detektált modell: {model}")

    lines = extract_lines_from_ass(ass_path)
    all_translatables = extract_translatables(lines)
    input_tokens, output_tokens = estimate_token_count(all_translatables, model)
    cost = calculate_cost(input_tokens, output_tokens, model)

    log_user_print(LOG_NAME, f"💡 Becsült költség: {cost:.2f} USD ({input_tokens} input token, {output_tokens} output token, modell: {model})")
    accepted = True

    log_cost_estimate(model, input_tokens, output_tokens, cost, accepted)
    log_user_print(LOG_NAME, "✅ Költség naplózva és elfogadva. Folytatás lehetséges.")

if __name__ == "__main__":
    main()
