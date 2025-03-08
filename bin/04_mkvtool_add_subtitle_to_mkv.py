import os
import subprocess

# 📌 Projektmappa és 'data' mappa meghatározása
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")

# 📌 Megkeressük az összes MKV és HU.ass fájlt a 'data' mappában
mkv_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".mkv")]
ass_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".ass") and ".HU." in f]

if not mkv_files:
    print("❌ Nincs MKV fájl a 'data' mappában!")
    exit(1)

if not ass_files:
    print("❌ Nincs HU feliratfájl a 'data' mappában!")
    exit(1)

# 📌 Párosítjuk az MKV fájlokat a megfelelő HU.ass fájlokkal
for mkv_file in mkv_files:
    base_name = os.path.splitext(mkv_file)[0]  # Alapnév kiterjesztés nélkül
    matching_ass_file = next((ass for ass in ass_files if base_name in ass), None)

    if not matching_ass_file:
        print(f"⚠️ Nem található megfelelő HU felirat ehhez: {mkv_file}")
        continue  # Ha nincs párosítható felirat, ugrunk a következő MKV-ra

    # 📌 Teljes elérési utak
    mkv_path = os.path.join(DATA_DIR, mkv_file)
    ass_path = os.path.join(DATA_DIR, matching_ass_file)
    output_file = os.path.join(DATA_DIR, f"{base_name}_HU.mkv")

    # 📌 MKVToolNix parancs összeállítása
    command = [
        "mkvmerge", "-o", output_file,
        mkv_path,
        "--language", "0:hun",
        "--track-name", "0:Magyar",
        ass_path
    ]

    # 📌 Parancs végrehajtása
    print(f"🚀 MKVToolNix futtatása: {' '.join(command)}")
    try:
        subprocess.run(command, check=True)
        print(f"✅ Sikeresen hozzáadtuk a feliratot! Kimeneti fájl: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Hiba történt: {e}")
