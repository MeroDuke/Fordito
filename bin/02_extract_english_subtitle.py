import json
import subprocess
import os

def extract_english_subtitle(mkv_file):
    """
    Kinyeri az angol feliratot egy adott MKV fájlból és .ass formátumban menti el.
    """
    # Fájl neve kiterjesztés nélkül
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
    extract_command = [
        "mkvextract", "tracks", mkv_file, f"{track_id}:{output_subtitle}"
    ]
    extract_result = subprocess.run(extract_command, capture_output=True, text=True)
    
    if extract_result.returncode != 0:
        print("❌ Hiba történt a felirat kinyerése közben!")
        print(extract_result.stderr)
    else:
        print(f"✅ Sikeresen kinyert felirat: {output_subtitle}")

# Példa használat
mkv_file = "Welcome.to.Japan.Ms.Elf.S01E08.Welcome.to.Japan.Mrs.Arcane.Dragon.1080p.BILI.WEB-DL.AAC2.0.H.264-VARYG.mkv"  # Ezt cseréld le dinamikusan
extract_english_subtitle(mkv_file)
