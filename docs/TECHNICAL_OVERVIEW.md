# 🧠 Technikai dokumentáció – Subtitle Translator

Ez a dokumentáció a fejlesztők számára készült, hogy gyorsan átlássák a projekt szerkezetét, működését és moduljait.

---

## 📁 Fő mappák

- **bin/** – Fő futtatható scriptek
- **scripts/** – Újrafelhasználható Python modulok
- **config/** – Konfigurációs fájlok (INI/JSON)
- **data/** – Bemeneti és kimeneti .ass fájlok
- **tests/** – Teszt Automata fájlok
- **userdata/** – Beszélőnevek, színek és egyéb adatok
- **logs/** – Naplózott hibák, figyelmeztetések

---

## 🧩 Futtatható scriptek (bin/)

| Fájl | Funkció |
|------|---------|
| `01_download_torrent_parser_qbittorrent.py` | Letölti a legfrissebb torrentet az RSS alapján |
| `02_extract_subtitles.py` | Kibontja az .ass fájlt a letöltött MKV-ből |
| `03_OpenAI_API_ONLY_4-Turbo_translate_ass.py` | Lefordítja az angol vagy japán feliratot magyarra (OpenAI) |
| `04_update_character_gender_map.py` | Beszélőnevek és nemek leképezése a felirat alapján |
| `05_mkvtool_add_subtitle_to_mkv.py` | Visszailleszti a lefordított feliratot az MKV fájlba |
| `06_discord_post_ASS.py` | A lefordított feliratot Discord webhookon keresztül elküldi |
| `07_cleanup_data_and_torrents.py` | Régi torrentek és felesleges fájlok törlése a data/ mappából |

---

## 🔄 Workflow (master_translator.py)

```text
1. Torrent letöltés (01)
2. Felirat kibontása (02)
3. Fordítás OpenAI segítségével (03)
4. Beszélők és nemek frissítése (04)
5. Felirat visszarakása az MKV-be (05)
6. Discord értesítés küldése (06)
7. Takarítás (07)
```

---

## 🧱 Modulok (scripts/)

| Modul | Leírás |
|-------|--------|
| `color_utils.py`  | Karakter szinezés segédlet
| `context_lookup.py` | Extra kontextus keresése egy adott címhez |
| `download_log.py` | Letöltési események naplózása |
| `episode_utils.py` | Epizód-specifikus segédfüggvények |
| `estimate_translation_cost.py` | Fordítás várható költségének becslése token alapon |
| `logger.py` | Naplózás vezérlése (ki/bekapcsolás) |
| `qbittorrent_client.py` | qBittorrent Web API kapcsolat és letöltésvezérlés |
| `__init__.py` | (üres) – a `scripts` mappa modulként importálhatóvá tétele |

---

## ⚙️ Konfigurációs fájlok kapcsolatai

| Fájl | Kapcsolódó script(ek) |
|------|------------------------|
| `credentials.ini` | 03 (OpenAI), 06 (Discord) |
| `openai_config.ini` | 03 (motor, kontextus, batch limit) |
| `discord_config.ini` | 06 |
| `qbittorrent_config.ini` | 01 |
| `cleanup_config.ini` | 07 |
| `postprocess_config.ini` | 03, 05 |

---

## 🔧 Egyéb megjegyzések

- A legtöbb bin/script modulos formában készült, így külön-külön is futtatható.
- A `master_translator.py` lineárisan végrehajtja az összes lépést.
- A `master_test_automation.py`lineárisan lefuttatja az összes automata tesztet.
- A `logs/` mappa tartalma alapértelmezetten nem jön létre, de hiba esetén automatikusan generálódik.

---

```markdown
## 🧪 Tesztfuttatás

A teljes projekt tesztelése a gyökérmappában található `master_test_automation.py` script segítségével történik:

```bash
python master_test_automation.py

```
Ez minden tests/ alatti modult lefuttat, és opcionálisan HTML riportot generál a logs/ mappába.

---

## 📝 Záró megjegyzés

Ez a technikai dokumentáció a Subtitle Translator projekt **1.1.0 verziójához** készült.  
A dokumentáció célja, hogy egy fejlesztő rövid idő alatt átlássa a rendszer felépítését, működését és a főbb összefüggéseket.

További fejlesztések (pl. API integráció, bővített moduláris struktúra, automatizált tesztelés) esetén ajánlott a dokumentációt kiegészíteni, illetve részletesebb ábrákkal vagy folyamatleírásokkal bővíteni.

---