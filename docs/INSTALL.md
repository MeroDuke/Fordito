# 🛠️ Telepítési útmutató – Subtitle Translator

Ez a dokumentáció lépésről lépésre bemutatja, hogyan lehet beállítani és elindítani a Subtitle Translator rendszert.

---

## 🗓️ Rendszerkövetelmények

* **Python**: 3.10.5 vagy újabb
* **Operációs rendszer**: Windows 10/11 (más rendszerekre nem tesztelt)
* **Git** (a repository klónozásához)

---

## 📦 Süzkséges Python csomagok

A következő Python csomagokat manuálisan kell telepíteni `pip` segítségével:

```bash
pip install requests tqdm openai tiktoken qbittorrent-api pytest pytest-html
```

---

## 💻 Külső programok (nem Python)

A következő külső eszközök szükségesek a rendszer működéséhez:

| Program               | Funkció                                            | Letöltési link                                      |
| --------------------- | -------------------------------------------------- | --------------------------------------------------- |
| **qBittorrent**       | Torrentek automatikus letöltése RSS-ből            | [qbittorrent.org](https://www.qbittorrent.org/)     |
| **MKVToolNix**        | Feliratok kinyerése MKV fájlokból                  | [mkvtoolnix.download](https://mkvtoolnix.download/) |
| **Subtitle Edit CLI** | SUP bitmap feliratok OCR alapú konvertálása ASS-ba | [nikse.dk](https://www.nikse.dk/SubtitleEdit)       |

> *Megjegyzés: A Subtitle Edit telepítése után győződj meg róla, hogy a `SubtitleEdit.exe` elérhető a PATH-ban.*

---

## 🔐 API kulcsok beállítása

1. Hozd létre a `config/credentials.ini` fájlt (ha még nem létezik).
2. Add meg az API kulcsokat a következő formátumban:

```ini
[OPENAI]
api_key = sk-...
```

*Megjegyzés: csak az OpenAI használata kötelező.*

---

## 🏁 Első futtatás

1. Klónozd le a projektet:

```bash
git clone https://github.com/MeroDuke/Fordito.git
cd Fordito
```

2. Ellenőrizd a config/ mappa helyességét és állítsd be a konfigurációs fájlokat.
   cleanup\_config.ini: megadja, hogy milyen régi torrenteket szeretnél megtartani.
   credentials.ini: az OpenAI API-kulcs helye.
   discord\_config.ini: a Discord-integrációhoz szükséges webhook URL.
   openai\_config.ini: OpenAI beállítások – használt motor, fordítási mennyiség szabályozása, extra kontextus használata.
   postprocess\_config.ini: utómunka az ASS fájlban, például ha más szerzőt szeretnél megadni a kész feliratban.
   qbittorrent\_config.ini: qBittorrent kapcsolat beállításai – torrent filterek, megbízhatósági beállítások, specifikus torrentek szűrése.

3. Válassz futtatási módot:
   3/A. Futtasd a scripteket külön-külön, egymás után, ha manuálisan szeretnéd végrehajtani a lépéseket.
   3/B. Futtasd a fő scriptet (master\_translator.py), ha a teljes folyamatot egyben szeretnéd elindítani:

```bash
python master_translator.py
```

> A rendszer automatikusan felismeri a legfrissebb feliratot, beleértve a bitmap (SUP) feliratok felismerését és OCR alapú feldolgozását is, ha szükséges.

---

## 🖼️ SUP felirat konvertálása (1.2.0 újdonság)

A rendszer 1.2.0-tól kezdődően **automatikusan felismeri a bitmap formátumú SUP feliratokat** a `02_extract_subtitles.py` futtatásakor, és ha talál ilyet, automatikusan OCR-rel átalakítja ASS formátumba.

Nincs szükség külön lefuttatni a `sup_to_ass.py` scriptet, mivel a funkció beépült a normál feliratfeldolgozási folyamatba.

1. Győződj meg róla, hogy a `SubtitleEdit.exe` elérhető a PATH-ban.
2. Helyezz el egy .mkv fájlt a `data/` mappába, amely tartalmaz bitmap feliratot.
3. Futtasd a következő parancsot:

```bash
python 02_extract_subtitles.py
```

> A rendszer automatikusan felismeri a bitmap feliratokat és elvégzi az átalakítást ASS formátumba a `data/` mappában.

---

## ✅ Sikeres futás ellenőrzése

* 3/A: Ha a data/ mappában és a Discord csatornán is megjelenik egy új .hungarian.ass fájl, akkor a rendszer helyesen működik.
* 3/B: Ha a Discord csatornán megjelenik egy új .hungarian.ass fájl, akkor a rendszer helyesen működik.
* SUP feldolgozás esetén: A `data/` mappában létrejön a konvertált `.ass` fájl a normál feldolgozási folyamat részeként.
* Hiba esetén a részletes naplók a logs/ mappában találhatók.

---

## 🧪 Tesztelés

A projekt teljes tesztkészlete lefuttatható a következő paranccsal:

```bash
python master_test_automation.py
```

Ez a parancs a tests/ mappa minden tesztjét lefuttatja, és opcionálisan HTML riportot is készít a logs/ mappába (ha engedélyezve van a logolás).
