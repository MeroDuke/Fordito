import sys
import os
import json
import subprocess
import shutil
import time

# 📌 Projektmappa és 'data' mappa meghatározása
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")

# 📌 Log modul betöltése
sys.path.insert(0, PROJECT_DIR)
from scripts.logger import log_user_print, log_tech

LOG_NAME = "02_extract_subtitles"


def check_dependency(command):
    if shutil.which(command) is None:
        log_tech(LOG_NAME, f"'{command}' parancs nem található a PATH-ban.")
        raise EnvironmentError(f"'{command}' parancs nem található. Telepítsd a szükséges csomagot.")


def run_command(command, error_message, shell=False):
    result = subprocess.run(command, capture_output=True, text=True, shell=shell)
    if result.returncode != 0:
        log_tech(LOG_NAME, f"{error_message}\n{result.stderr.strip()}")
        raise RuntimeError(f"{error_message}\n{result.stderr.strip()}")
    return result.stdout


def find_mkv_file(directory):
    for file in os.listdir(directory):
        if file.lower().endswith(".mkv"):
            return os.path.join(directory, file)
    return None


def wait_until_file_unlocked(file_path, timeout=10):
    start_time = time.time()
    while True:
        try:
            with open(file_path, "rb"):
                return True
        except PermissionError:
            if time.time() - start_time > timeout:
                return False
            time.sleep(0.5)


def extract_subtitle(mkv_info, mkv_file, language_codes, output_suffix, fallback_track_name=None):
    base_name = os.path.splitext(mkv_file)[0]
    subtitle_track = None

    for track in mkv_info.get("tracks", []):
        if track.get("type") == "subtitles" and track.get("properties", {}).get("language", "").lower() in language_codes:
            codec_id = track.get("properties", {}).get("codec_id")
            if codec_id == "S_HDMV/PGS":
                return  # PGS van, nem dolgozunk vele itt
            subtitle_track = track
            break

    if not subtitle_track and fallback_track_name:
        for track in mkv_info.get("tracks", []):
            if (
                track.get("type") == "subtitles"
                and fallback_track_name.lower() in track.get("properties", {}).get("track_name", "").lower()
            ):
                codec_id = track.get("properties", {}).get("codec_id")
                if codec_id == "S_HDMV/PGS":
                    return
                subtitle_track = track
                log_user_print(LOG_NAME, f"ℹ️ Fallback: {output_suffix} felirat a track_name alapján ('{fallback_track_name}')")
                break

    if not subtitle_track:
        log_user_print(LOG_NAME, f"❌ Nincs {output_suffix} szöveges felirat.")
        return

    track_id = subtitle_track["id"]
    codec_id = subtitle_track.get("properties", {}).get("codec_id")
    log_user_print(LOG_NAME, f"✅ {output_suffix.capitalize()} felirat megtalálva: Track ID {track_id}")
    log_tech(LOG_NAME, f"✅ {output_suffix.capitalize()} felirat megtalálva: Track ID {track_id} (codec: {codec_id})")

    base_name = os.path.splitext(mkv_file)[0]
    output_path = f"{base_name}_{output_suffix}.ass"

    if os.path.exists(output_path):
        log_user_print(LOG_NAME, f"ℹ️ A {output_path} fájl már létezik. Átugrás.")
        return

    extract_command = ["mkvextract", "tracks", mkv_file, f"{track_id}:{output_path}"]
    try:
        run_command(extract_command, f"❌ Hiba a {output_suffix} felirat kinyerésénél!")
        if not wait_until_file_unlocked(output_path):
            log_tech(LOG_NAME, f"Nem olvasható: {output_path}")
            return

        if codec_id != "S_TEXT/ASS":
            log_user_print(LOG_NAME, f"⚠️ A {output_suffix} felirat nem valódi .ass (codec: {codec_id}). Elmentve ugyan, de figyelem!")
            log_tech(LOG_NAME, f"Nem valódi .ass: codec_id={codec_id} fájl={output_path}")
        else:
            log_user_print(LOG_NAME, f"✅ Sikeresen kinyert {output_suffix} felirat: {output_path}")

    except RuntimeError as e:
        log_tech(LOG_NAME, str(e))


def extract_bitmap_subtitle(mkv_info, mkv_file, language_codes, output_suffix):
    base_name = os.path.splitext(mkv_file)[0]
    output_sup = f"{base_name}_{output_suffix}.sup"
    output_ass = f"{base_name}_{output_suffix}.ass"

    for track in mkv_info.get("tracks", []):
        if (
            track.get("type") == "subtitles"
            and track.get("codec_id") == "S_HDMV/PGS"
            and track.get("properties", {}).get("language", "").lower() in language_codes
        ):
            track_id = track["id"]
            log_user_print(LOG_NAME, f"✅ {output_suffix.capitalize()} bitmap felirat megtalálva: Track ID {track_id}")
            extract_command = ["mkvextract", "tracks", mkv_file, f"{track_id}:{output_sup}"]
            try:
                run_command(extract_command, f"❌ Hiba a {output_suffix} .sup kinyerésekor!")
                log_user_print(LOG_NAME, f"✅ {output_suffix} .sup fájl kinyerve: {output_sup}")
                from scripts.sup_to_ass import convert_sup_to_ass
                convert_sup_to_ass(output_sup, output_ass, lang=output_suffix)
                return True
            except RuntimeError as e:
                log_tech(LOG_NAME, str(e))
    return False


def main():
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
        command = ["mkvmerge", "-J", mkv_file]
        try:
            stdout = run_command(command, "Nem sikerült olvasni az MKV metainfót!")
            mkv_info = json.loads(stdout)

            # English
            if not extract_bitmap_subtitle(mkv_info, mkv_file, ["eng", "en"], "english"):
                extract_subtitle(mkv_info, mkv_file, ["eng", "en"], "english")

            # Japanese
            if not extract_bitmap_subtitle(mkv_info, mkv_file, ["jpn", "ja"], "japanese"):
                extract_subtitle(mkv_info, mkv_file, ["jpn", "ja"], "japanese", fallback_track_name="ass")

        except Exception as e:
            log_tech(LOG_NAME, f"MKV info feldolgozási hiba: {e}")
    else:
        log_user_print(LOG_NAME, "⚠️ Nincs MKV fájl a 'data' mappában.")


if __name__ == "__main__":
    main()