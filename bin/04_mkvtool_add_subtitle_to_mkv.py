import os
import subprocess

# 📌 Keressük meg az MKV fájlt az aktuális mappában
mkv_files = [f for f in os.listdir() if f.endswith(".mkv")]
if not mkv_files:
    print("❌ Nincs MKV fájl a mappában!")
    exit(1)
mkv_file = mkv_files[0]  # Az első talált MKV fájl

# 📌 Keressük meg az "HU" azonosítót tartalmazó ASS feliratfájlt
ass_files = [f for f in os.listdir() if f.endswith(".ass") and "HU" in f]
if not ass_files:
    print("❌ Nincs HU feliratfájl a mappában!")
    exit(1)
ass_file = ass_files[0]

# 📌 Kimeneti fájl neve (HU megjelöléssel)
output_file = mkv_file.replace(".mkv", "_HU.mkv")

# 📌 MKVToolNix parancs összeállítása
command = [
    "mkvmerge", "-o", output_file,
    mkv_file,
    "--language", "0:hun",
    "--track-name", "0:Magyar",
    ass_file
]

# 📌 Parancs végrehajtása
print(f"🚀 MKVToolNix futtatása: {' '.join(command)}")
try:
    subprocess.run(command, check=True)
    print(f"✅ Sikeresen hozzáadtuk a feliratot! Kimeneti fájl: {output_file}")
except subprocess.CalledProcessError as e:
    print(f"❌ Hiba történt: {e}")
