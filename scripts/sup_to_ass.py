import sys
import os
import subprocess
import shutil
from pathlib import Path

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PROJECT_DIR)

from scripts.logger import log_tech, log_user_print

LOG_NAME = "sup_to_ass"

def find_english_sup_file(data_dir: str = "data") -> str:
    """
    Megkeresi az első .sup fájlt, ami '_english' mintát tartalmaz.
    """
    for file in Path(data_dir).glob("*.sup"):
        if "_english" in file.stem:
            return str(file.resolve())
    raise RuntimeError(f"❌ Nem található '_english' mintát tartalmazó SUP fájl a {data_dir} mappában.")

from tqdm import tqdm

def run_subtitle_edit_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    pbar = tqdm(total=100, desc="🔄 OCR progress", unit="%", ncols=80)
    current_progress = 0
    for line in iter(process.stdout.readline, ''):
        clean_line = line.strip()
        if not clean_line:
            continue
        if "OCR... :" in clean_line:
            try:
                progress = int(clean_line.split(":")[-1].strip().replace("%", ""))
                if progress > current_progress:
                    pbar.update(progress - current_progress)
                    current_progress = progress
            except ValueError:
                continue
        else:
            log_tech(LOG_NAME, clean_line)
    pbar.close()
    process.wait()
    return process.returncode

def convert_sup_to_ass(sup_path: str, ass_output_path: str, lang: str = "en"):
    """
    SUP → ASS feldolgozás Subtitle Edit CLI segítségével (OCR alapon).
    A SubtitleEdit.exe-nek a PATH-ban kell lennie.
    """
    log_user_print(LOG_NAME, f"📥 Feldolgozás elindítva: {sup_path}")

    if not shutil.which("SubtitleEdit.exe"):
        raise RuntimeError("❌ Subtitle Edit CLI nem található a PATH-ban!")

    if not os.path.exists(sup_path):
        raise RuntimeError(f"❌ Bemeneti SUP fájl nem található: {sup_path}")

    sup_abs = os.path.abspath(sup_path)
    ass_abs = os.path.abspath(ass_output_path)

    command = [
        "SubtitleEdit.exe",
        "/convert",
        sup_abs,
        "ass",
        f"/outputfilename:{ass_abs}"
    ]

    log_tech(LOG_NAME, f"⚙️ Subtitle Edit parancs: {' '.join(command)}")
    log_user_print(LOG_NAME, "▶️ OCR elindítva...")

    return_code = run_subtitle_edit_command(command)

    if return_code != 0 or not os.path.exists(ass_abs):
        raise RuntimeError(f"❌ Subtitle Edit hibázott vagy nem jött létre az ASS fájl: {ass_output_path}")

    log_user_print(LOG_NAME, f"✅ Sikeres feldolgozás, létrejött: {ass_output_path}")

if __name__ == "__main__":
    try:
        sup_path = find_english_sup_file("data")
        ass_output_path = str(Path(sup_path).with_suffix(".ass"))
        convert_sup_to_ass(sup_path, ass_output_path, lang="english")
    except Exception as e:
        print(str(e))
