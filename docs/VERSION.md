# 🗂️ Verziótörténet – Subtitle Translator

## \[1.4.0] – 2025-05-21

### 🛠️ Stabilitási és kompatibilitási kiadás

Ez a verzió nem tartalmaz új funkciókat, kizárólag a projekt teljes körű, dokumentált és gépfüggetlen futtathatóságát biztosítja.

### ♻️ Módosítások

* Az `INSTALL.md` teljesen újrastrukturálva step-by-step módon
* Verziók rögzítése (`openai==0.28`, Python 3.10.5 ajánlás)
* Subtitle Edit és MKVToolNix PATH kezelése pontosítva
* `credentials_template.ini` és más konfigurációs fájlok szerepe tisztázva
* Új figyelmeztetések az OpenAI költségekre és fiókszükségletre

### 🚗 Bugfixek

* A `06_discord_post_ASS.py` korábban tévesen választott torrentet bizonyos esetekben (pl. több hasonló című epizód esetén).  
  Javítva: mostantól pontozásos rendszer (kulcsszavak + epizód egyezés) alapján történik a párosítás, részletes technikai loggal.

### 📄 Dokumentáció

* `INSTALL.md` újraírása → VM-en is tesztelt változat
* `README.md`, `CONFIG_FILES.md`, `TECHNICAL_OVERVIEW.md` ellenőrizve – nem igényeltek módosítást

---

## \[1.3.0] – 2025-05-20

### ✅ Új funkciók

* `logger_config.ini` fájl bevezetése – a logolás vezérlése konfigurációs fájlból történik
* `logger.py` frissítve: automatikusan beolvassa a konfigurációt, ha elérhető
* Új logika a `06_discord_post_ASS.py` scriptben: torrent párosítás elsődlegesen hash alapján történik
* Verziókövetés dokumentumként (`VERSION.md`) kiegészítve

### 📄 Dokumentáció

* `INSTALL.md`, `README.md`, `TECHNICAL_OVERVIEW.md`, `CONFIG_FILES.md` frissítve az új logolási rendszerre
* `RELEASE_NOTES.md` fájl elkészült

---

## \[1.2.0] – 2025-05-13

### ✅ Új funkciók

* SUP bitmap feliratok automatikus felismerése és OCR alapú átalakítása ASS formátumba (`Subtitle Edit CLI` használatával)
* A `02_extract_subtitles.py` script kibővítve: automatikusan kezeli a bitmap (SUP) feliratokat is, nincs szükség külön lefutásra
* Új modul: `scripts/sup_to_ass.py` – dedikált OCR alapú SUP → ASS konvertáló funkció

### ♻️ Refaktorálások és módosítások

* `02_extract_subtitles.py` mostantól képes felismerni és automatikusan átalakítani a bitmap (SUP) feliratokat a teljes feldolgozási folyamatban
* A SUP konvertáló folyamat integrálva a `master_translator.py` pipeline-ba (nincs külön lépés rá)

### 📂 Új fájlok

* `scripts/sup_to_ass.py` – SUP bitmap feliratok OCR alapú átalakítása ASS-ba

### 📄 Dokumentáció

* `INSTALL.md`, `README.md`, `TECHNICAL_OVERVIEW.md` frissítve a SUP OCR feldolgozással kapcsolatos új funkcionalitásra

---

## \[1.1.0] – 2025-04-30

### ✅ Új funkciók

* Teljes körű automatikus tesztelési keretrendszer bevezetése (`tests/` mappa)
* Tesztek scriptből indíthatók a `master_test_automation.py` segítségével
* HTML riport generálás támogatása (`pytest-html` plugin segítségével)
* Logger-integráció teszteléshez és riportoláshoz (`log_user_print()` használat mindenhol)
* A `logger.py` frissítve: támogatja az UTF-8 karakterkódolást, Unicode kimenetet
* A `logs/` mappa mostantól naplózza a tesztek eredményét (ha engedélyezve van)

### 🥪 Új tesztmodulok

* `test_logger.py`: naplózási funkciók ellenőrzése
* `test_download_parser.py`: RSS parsing és torrent naplózás
* `test_load_downloaded_hashes.py`: letöltési log betöltés és hibatűrés
* `test_update_episode_log_hash.py`: hash frissítése meglévő logbejegyzéshez
* `test_translate_ass_script.py`: (blokkolva – fizetős API-t hívna)
* `test_character_color_map.py`: karakter-színgenerálás ellenőrzése
* `test_add_subtitle.py`: ASS felirat beillesztése MKV fájlba (`mkvmerge`)
* `test_cleanup_data_folder.py`: `/data` mappa fájltisztítása (mockolt klienssel)
* `test_episode_utils.py`: epizódazonosítás különféle címformátumokból
* `test_estimate_translation_cost.py`: költségbecslő token alapú működése

### 📂 Új fájlok

* `scripts/color_utils.py` – színkód generálás karakternevek alapján
* `master_test_automation.py` – minden tesztet egyben elindító futtatóscript
* Új tesztfájlok: `tests/test_*.py` (9 darab)

### ♻️ Refaktorálások

* `05_mkvtool_add_subtitle_to_mkv.py` frissítve: környezeti változós tesztelhetőség
* `logger.py` módosítva, hogy kódolási hibák nélkül támogassa az emojikat és magyar karaktereket
* Tesztek `tmp_path` és `mock` használatával íródtak (valós erőforrások helyett)

---

## \[1.0.1] – 2025-04-30

### 🚗 Bugfixek és pontosítások

* A költségbecslő modul (estimate\_translation\_cost.py) most már valósághű tokenhasználat alapján számol becslést.
* Az input tokenek figyelembe veszik a teljes rendszerprompt + batchen belüli összefűzött `user` szöveget.
* Az output tokenek becslése konzervatív `×1.7` szorzóval történik, hogy a valós költség alatt ne maradjon a jelzett érték.
* Ez a módosítás a `03_OpenAI_API_ONLY_4-Turbo_translate_ass.py` scripten keresztül is érvényesül.

---

## \[1.0.0.] – 2025-04-29

### ✨ Elkészült funkciók

* Automatizált torrent letöltés RSS alapján
* Subtitle kibontás MKV fájlokból
* AI-alapú feliratfordítás angol vagy japán nyelvről magyarra (OpenAI)
* Kontextusalapú prompt-rendszer (anime synopsis, karakterlista, műfaj)
* Token-alapú költségbecslés és API limit figyelem
* Beszélőalapú stíluskezelés és karakterenkénti színezés
* Konfigurációs rendszer `.ini` fájlokkal
* Discord webhook integráció
* Letöltési naplózás (torrent ismétlődés megelőzése)
* Teljes körű dokumentáció: README, INSTALL, TECH DOC, CONFIG FILES

---

### 🧊 A projekt jövője

Az 1.4.0 verzióval a Subtitle Translator projekt karbantartási fázisba lép. További funkciófejlesztés nem várható, kizárólag hibajavítás történik, ha szükséges.

A következő nagyobb kiadás várhatóan **2.0.0** lesz, amely teljesen újratervezett rendszerként, grafikus felhasználói felülettel (GUI) és új funkcionalitással tér vissza – ha és amikor a fejlesztő kedvet érez hozzá.
