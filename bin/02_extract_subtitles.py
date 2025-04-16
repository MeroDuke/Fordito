import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, PROJECT_DIR)

import json
import subprocess
import os
import shutil

# 📌 Projektmappa és 'data' mappa meghatározása
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")

# 📌 Log modul
from scripts.logger import log_user_print, log_tech
LOG_NAME = "02_extract_subtitles"

def check_dependency(command):
    if shutil.which(command) is None:
        log_tech(LOG_NAME, f"'{command}' parancs nem található a PATH-ban.")
        raise EnvironmentError(f"'{command}' parancs nem található. Telepítsd a szükséges csomagot.")

def run_command(command, error_message):
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        log_tech(LOG_NAME, f"{error_message}\n{result.stderr.strip()}")
        raise RuntimeError(f"{error_message}\n{result.stderr.strip()}")
    return result.stdout

def find_mkv_file(directory):
    try:
        for file in os.listdir(directory):
            if file.lower().endswith(".mkv"):
                return os.path.join(directory, file)
    except FileNotFoundError:
        log_tech(LOG_NAME, f"A mappa nem található: {directory}")
        log_user_print(LOG_NAME, f"⚠️ A mappa nem található: {directory}")
    return None

def extract_subtitle(mkv_file, language_codes, output_suffix, fallback_track_name=None):
    base_name = os.path.splitext(mkv_file)[0]
    output_subtitle = f"{base_name}_{output_suffix}.ass"

    if os.path.exists(output_subtitle):
        log_user_print(LOG_NAME, f"ℹ️ A {output_subtitle} fájl már létezik. Átugrás.")
        return

    command = ["mkvmerge", "-J", mkv_file]
    try:
        stdout = run_command(command, "❌ Hiba történt az MKV fájl feldolgozása közben!")
        mkv_info = json.loads(stdout)
    except (RuntimeError, json.JSONDecodeError) as e:
        log_tech(LOG_NAME, f"MKV feldolgozási hiba: {e}")
        return

    subtitle_track = next(
        (
            track for track in mkv_info.get("tracks", [])
            if track.get("type") == "subtitles" and track.get("properties", {}).get("language", "").lower() in language_codes
        ),
        None
    )

    if not subtitle_track and fallback_track_name:
        subtitle_track = next(
            (
                track for track in mkv_info.get("tracks", [])
                if track.get("type") == "subtitles" and fallback_track_name.lower() in track.get("properties", {}).get("track_name", "").lower()
            ),
            None
        )
        if subtitle_track:
            log_user_print(LOG_NAME, f"ℹ️ Fallback: {output_suffix} felirat kinyerése a track_name alapján ('{fallback_track_name}')")
            log_tech(LOG_NAME, f"Fallback track alapján talált felirat: {output_suffix}")

    if not subtitle_track:
        log_user_print(LOG_NAME, f"❌ Nem található {output_suffix} felirat a fájlban.")
        return

    track_id = subtitle_track["id"]
    log_user_print(LOG_NAME, f"✅ {output_suffix.capitalize()} felirat megtalálva: Track ID {track_id}")
    log_tech(LOG_NAME, f"{output_suffix} track megtalálva, ID: {track_id}")

    extract_command = ["mkvextract", "tracks", mkv_file, f"{track_id}:{output_subtitle}"]
    try:
        run_command(extract_command, f"❌ Hiba történt a {output_suffix} felirat kinyerése közben!")
        log_user_print(LOG_NAME, f"✅ Sikeresen kinyert {output_suffix} felirat: {output_subtitle}")
        log_tech(LOG_NAME, f"{output_suffix} felirat kinyerve: {output_subtitle}")
    except RuntimeError as e:
        log_tech(LOG_NAME, f"{e}")

if __name__ == "__main__":
    try:
        check_dependency("mkvmerge")
        check_dependency("mkvextract")
    except EnvironmentError as e:
        log_user_print(LOG_NAME, str(e))
        exit(1)

    log_user_print(LOG_NAME, f"🔍 MKV fájl keresése a mappában: {DATA_DIR}")
    mkv_file = find_mkv_file(DATA_DIR)

    if mkv_file:
        log_user_print(LOG_NAME, f"🎯 Talált MKV fájl: {mkv_file}")
        log_tech(LOG_NAME, f"MKV fájl betöltve feldolgozásra: {mkv_file}")
        extract_subtitle(mkv_file, ["eng", "en"], "english")
        extract_subtitle(mkv_file, ["jpn", "ja"], "japanese", fallback_track_name="ass")
    else:
        log_user_print(LOG_NAME, "⚠️ Nincs MKV fájl a 'data' mappában.")
