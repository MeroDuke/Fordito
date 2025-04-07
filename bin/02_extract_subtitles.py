import json
import subprocess
import os
import shutil

# 📌 Projektmappa és 'data' mappa meghatározása
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")


def check_dependency(command):
    """Ellenőrzi, hogy a megadott parancs elérhető-e a rendszer PATH-jában."""
    if shutil.which(command) is None:
        raise EnvironmentError(f"'{command}' parancs nem található. Telepítsd a szükséges csomagot.")


def run_command(command, error_message):
    """Futtat egy parancsot és hibák esetén kivételt dob."""
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"{error_message}\n{result.stderr.strip()}")
    return result.stdout


def find_mkv_file(directory):
    """
    Megkeresi az első elérhető MKV fájlt a megadott mappában.
    """
    try:
        for file in os.listdir(directory):
            if file.lower().endswith(".mkv"):
                return os.path.join(directory, file)
    except FileNotFoundError:
        print(f"⚠️ A mappa nem található: {directory}")
    return None


def extract_subtitle(mkv_file, language_codes, output_suffix):
    """
    Kinyeri a megadott nyelvű feliratot egy adott MKV fájlból és .ass formátumban menti el.
    """
    base_name = os.path.splitext(mkv_file)[0]
    output_subtitle = f"{base_name}_{output_suffix}.ass"

    # Ellenőrizzük, hogy a kimeneti fájl már létezik-e
    if os.path.exists(output_subtitle):
        print(f"ℹ️ A {output_subtitle} fájl már létezik. Átugrás.")
        return

    # MKV fájl információ lekérése JSON formátumban
    command = ["mkvmerge", "-J", mkv_file]
    try:
        stdout = run_command(command, "❌ Hiba történt az MKV fájl feldolgozása közben!")
        mkv_info = json.loads(stdout)
    except (RuntimeError, json.JSONDecodeError) as e:
        print(e)
        return

    # Megkeressük a felirat track-et a megadott nyelvkódokkal
    subtitle_track = next(
        (
            track for track in mkv_info.get("tracks", [])
            if track.get("type") == "subtitles" and track.get("properties", {}).get("language", "").lower() in language_codes
        ),
        None
    )

    if not subtitle_track:
        print(f"❌ Nem található {output_suffix} felirat a fájlban.")
        return

    track_id = subtitle_track["id"]
    print(f"✅ {output_suffix.capitalize()} felirat megtalálva: Track ID {track_id}")

    # Felirat kinyerése .ass formátumban
    extract_command = ["mkvextract", "tracks", mkv_file, f"{track_id}:{output_subtitle}"]
    try:
        run_command(extract_command, f"❌ Hiba történt a {output_suffix} felirat kinyerése közben!")
        print(f"✅ Sikeresen kinyert {output_suffix} felirat: {output_subtitle}")
    except RuntimeError as e:
        print(e)


# 📌 Főprogram
if __name__ == "__main__":
    # Ellenőrizzük a szükséges parancsokat
    try:
        check_dependency("mkvmerge")
        check_dependency("mkvextract")
    except EnvironmentError as e:
        print(e)
        exit(1)

    print(f"🔍 MKV fájl keresése a mappában: {DATA_DIR}")
    mkv_file = find_mkv_file(DATA_DIR)

    if mkv_file:
        print(f"🎯 Talált MKV fájl: {mkv_file}")
        # Angol felirat kinyerése
        extract_subtitle(mkv_file, ["eng", "en"], "english")
        # Japán felirat kinyerése
        extract_subtitle(mkv_file, ["jpn", "ja"], "japanese")
    else:
        print("⚠️ Nincs MKV fájl a 'data' mappában.")
