import json
import subprocess
import os

# 📌 Projektmappa és 'data' mappa meghatározása
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")

def find_mkv_file(directory):
    """
    Megkeresi az első elérhető MKV fájlt a megadott mappában.
    """
    for file in os.listdir(directory):
        if file.endswith(".mkv"):
            return os.path.join(directory, file)
    return None

def extract_english_subtitle(mkv_file):
    """
    Kinyeri az angol feliratot egy adott MKV fájlból és .ass formátumban menti el.
    """
    base_name = os.path.splitext(mkv_file)[0]
    output_subtitle = f"{base_name}.ass"
    
    # MKV fájl információ lekérése JSON formátumban
    command = ["mkvmerge", "-J", mkv_file]
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Hiba történt az MKV fájl feldolgozása közben!")
        print(result.stderr)
        return
    
    try:
        mkv_info = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("❌ Hiba: Az MKV fájl adatai nem olvashatók JSON formátumban.")
        return
    
    # Keresünk egy angol nyelvű feliratot
    subtitle_track = None
    for track in mkv_info.get("tracks", []):
        if track.get("type") == "subtitles" and track["properties"].get("language", "") in ["eng", "en"]:
            subtitle_track = track
            break
    
    if not subtitle_track:
        print("❌ Nem található angol felirat a fájlban.")
        return
    
    track_id = subtitle_track["id"]
    print(f"✅ Angol felirat megtalálva: Track ID {track_id}")
    
    # Felirat kinyerése .ass formátumban
    extract_command = ["mkvextract", "tracks", mkv_file, f"{track_id}:{output_subtitle}"]
    extract_result = subprocess.run(extract_command, capture_output=True, text=True)
    
    if extract_result.returncode != 0:
        print("❌ Hiba történt a felirat kinyerése közben!")
        print(extract_result.stderr)
    else:
        print(f"✅ Sikeresen kinyert felirat: {output_subtitle}")

# 📌 Főprogram
if __name__ == "__main__":
    print(f"🔍 MKV fájl keresése a mappában: {DATA_DIR}")
    mkv_file = find_mkv_file(DATA_DIR)

    if mkv_file:
        print(f"🎯 Talált MKV fájl: {mkv_file}")
        extract_english_subtitle(mkv_file)
    else:
        print("⚠️ Nincs MKV fájl a 'data' mappában.")
