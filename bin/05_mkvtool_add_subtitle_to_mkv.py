import os
import subprocess
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, PROJECT_DIR)

from scripts.logger import log_user_print, log_tech
LOG_NAME = "05_add_subs"

DATA_DIR = os.environ.get("FORDITO_DATA_DIR", os.path.join(PROJECT_DIR, "data"))

mkv_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".mkv")]
ass_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".ass") and "_hungarian_styled." in f]

if not mkv_files:
    log_user_print(LOG_NAME, "❌ Nincs MKV fájl a 'data' mappában!")
    log_tech(LOG_NAME, "Hiányzik MKV fájl a data mappában.")
    exit(1)

if not ass_files:
    log_user_print(LOG_NAME, "❌ Nincs hungarian feliratfájl a 'data' mappában!")
    log_tech(LOG_NAME, "Hiányzik magyar feliratfájl a data mappában.")
    exit(1)

for mkv_file in mkv_files:
    base_name = os.path.splitext(mkv_file)[0]
    matching_ass_file = next((ass for ass in ass_files if base_name in ass), None)

    if not matching_ass_file:
        log_user_print(LOG_NAME, f"⚠️ Nem található megfelelő hungarian felirat ehhez: {mkv_file}")
        log_tech(LOG_NAME, f"Nincs ass párosítás: {mkv_file}")
        continue

    mkv_path = os.path.join(DATA_DIR, mkv_file)
    ass_path = os.path.join(DATA_DIR, matching_ass_file)
    output_file = os.path.join(DATA_DIR, f"{base_name}_hungarian.mkv")

    command = [
        "mkvmerge", "-o", output_file,
        mkv_path,
        "--language", "0:hun",
        "--track-name", "0:Magyar",
        ass_path
    ]

    command_str = " ".join(command)
    log_tech(LOG_NAME, f"Futtatandó parancs: {command_str}")
    log_user_print(LOG_NAME, "MKVToolNix futtatása")

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        log_tech(LOG_NAME, f"mkvmerge stdout:\n{result.stdout}")
        log_tech(LOG_NAME, f"mkvmerge stderr:\n{result.stderr}")
        log_user_print(LOG_NAME, f"✅ Sikeresen hozzáadtuk a feliratot! Kimeneti fájl: {output_file}")
        log_tech(LOG_NAME, f"Felirat hozzáadva: {output_file}")
    except subprocess.CalledProcessError as e:
        log_user_print(LOG_NAME, f"❌ Hiba történt: {e}")
        log_tech(LOG_NAME, f"Hiba mkvmerge futtatása közben: {e}")
        log_tech(LOG_NAME, f"stdout:\n{e.stdout}")
        log_tech(LOG_NAME, f"stderr:\n{e.stderr}")