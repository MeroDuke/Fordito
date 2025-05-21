# 🛠️ Telepítési útmutató – Subtitle Translator

Ez a dokumentáció lépésről lépésre bemutatja, hogyan lehet beállítani és elindítani a Subtitle Translator rendszert.

---

## 🗓️ Rendszerkövetelmények

* **Python**: 3.10.5 vagy újabb
* **Operációs rendszer**: Windows 10/11 (más rendszerekre nem tesztelt)
* **Git** (a repository klónozásához) – *vagy* töltsd le a projekt ZIP fájlját a GitHub webes felületéről: [Letöltés ZIP-ben](https://github.com/MeroDuke/Fordito/archive/refs/heads/main.zip)

---

## 💻 Külső programok (nem Python)

A következő külső eszközök szükségesek a rendszer működéséhez:

| Program               | Funkció                                            | Letöltési link                                      |
| --------------------- | -------------------------------------------------- | --------------------------------------------------- |
| **qBittorrent**       | Torrentek automatikus letöltése RSS-ből            | [qbittorrent.org](https://www.qbittorrent.org/)     |
| **MKVToolNix**        | Feliratok kinyerése MKV fájlokból                  | [mkvtoolnix.download](https://mkvtoolnix.download/) |
| **Subtitle Edit CLI** | SUP bitmap feliratok OCR alapú konvertálása ASS-ba | [nikse.dk](https://www.nikse.dk/SubtitleEdit)       |

---

## 🐍 Python telepítése (ha még nincs)

A Python letölthető innen: [python.org/downloads](https://www.python.org/downloads/windows/)

> Telepítésnél figyelj a következőkre:
>
> * Válaszd az **Install Now** lehetőséget.
> * Jelöld be az **Add Python to PATH** opciót.
> * Futtasd a telepítőt **rendszergazdaként**.
> * A telepítés végén kattints a **„Disable path length limit”** gombra, ha megjelenik.

---

## 📦 Szükséges Python csomagok

A következő Python csomagokat manuálisan kell telepíteni `pip` segítségével:

```bash
pip install requests tqdm openai tiktoken qbittorrent-api pytest pytest-html
```

---

## ⚙️ qBittorrent beállítása lépésről lépésre

1. Indítsd el a qBittorrent klienst.
2. Menj a „Beállítások” → „Webes felhasználói felület (Web UI)” részhez.
3. Kapcsold be a webes felületet.
4. Adj meg egy felhasználónevet és jelszót.
5. Kattints az „Alkalmaz” majd „OK” gombra.
6. A `Fordito/config/qbittorrent_config.ini` fájlban ugyanezt a nevet és jelszót add meg.
7. Ajánlott: A telepítés során kapcsold be a „Windows-zal együtt indul” opciót is, különben a letöltés nem fog működni.

---

## 🔧 Programok hozzáadása a PATH-hoz (ha nem automatikus)

Ha az MKVToolNix vagy a Subtitle Edit nem érhető el a parancssorból (`mkvmerge`, `SubtitleEdit.exe`), akkor a telepítési mappa elérési útját **kézzel kell hozzáadni** a rendszer PATH változójához:

1. Keresd meg, hova telepítetted a programot:

   * Például: `C:\Users\<felhasználónév>\AppData\Local\Programs\MKVToolNix`
   * vagy: `D:\PortableApps\Subtitle Edit`
2. Nyisd meg a **Vezérlőpult → Rendszer → Speciális rendszerbeállítások → Környezeti változók** menüpontot.
3. A „Rendszerváltozók” részben keresd meg a `Path` változót, majd kattints a **„Szerkesztés…”** gombra.
4. Kattints **„Új”**, majd illeszd be a megtalált elérési utat.
5. Kattints **OK** minden ablakban, majd **indíts új terminált**, hogy az új beállítás érvénybe lépjen.

> Ha az alapértelmezett helyre telepítetted volna a programokat, ezek lennének a tipikus útvonalak:
>
> * `C:\Program Files\MKVToolNix`
> * `C:\Program Files\Subtitle Edit`

---

## 🔐 API kulcsok beállítása

> ⚠️ **Fontos:** A rendszer működéséhez OpenAI fiók szükséges. Ez egy fizetős szolgáltatás!
>
> * Fiók létrehozása: [https://platform.openai.com/signup](https://platform.openai.com/signup)
> * API kulcs létrehozása: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
> * Egyenleg feltöltése: [https://platform.openai.com/account/billing](https://platform.openai.com/account/billing)

1. Hozd létre a `config/credentials.ini` fájlt (ha még nem létezik).
2. Add meg az API kulcsokat a következő formátumban:

```ini
[OPENAI]
api_key = sk-...
```

*Megjegyzés: csak az OpenAI használata kötelező.*

---

## 🏁 Első futtatás

1. Klónozd le a projektet Git segítségével:

```bash
git clone https://github.com/MeroDuke/Fordito.git
cd Fordito
```

*vagy* töltsd le a projekt ZIP változatát innen: [Letöltés ZIP-ben](https://github.com/MeroDuke/Fordito/archive/refs/heads/main.zip), majd csomagold ki egy tetszőleges mappába.

2. Ellenőrizd a `config/` mappa helyességét és állítsd be a konfigurációs fájlokat:

   * `cleanup_config.ini`: megadja, hogy milyen régi torrenteket szeretnél megtartani.
   * `credentials.ini`: az OpenAI API-kulcs helye.
   * `discord_config.ini`: a Discord-integrációhoz szükséges webhook URL.
   * `openai_config.ini`: OpenAI beállítások – használt motor, fordítási mennyiség szabályozása, extra kontextus használata. Figyelem: az „extra kontextus használata” opció bekapcsolása megnöveli az OpenAI API-költséget, mivel több szöveget küld a rendszer a modellnek fordítás előtt. Ez magasabb tokenhasználattal és így magasabb számlázással járhat. Érdemes csak akkor engedélyezni, ha valóban szükséges a pontosabb fordításhoz.
   * `postprocess_config.ini`: utómunka az ASS fájlban, például ha más szerzőt szeretnél megadni a kész feliratban.
   * `qbittorrent_config.ini`: qBittorrent kapcsolat beállításai – torrent filterek, megbízhatósági beállítások, specifikus torrentek szűrése.
   * `logger_config.ini`: vezérli, hogy a rendszer ír-e naplót a `logs/` mappába.

3. Válassz futtatási módot:

   * **3/A.** Futtasd a scripteket külön-külön, egymás után, ha manuálisan szeretnéd végrehajtani a lépéseket.
   * **3/B.** Futtasd a fő scriptet (master\_translator.py), ha a teljes folyamatot egyben szeretnéd elindítani:

```bash
python master_translator.py
```

> A rendszer automatikusan felismeri a legfrissebb feliratot, beleértve a bitmap (SUP) feliratok felismerését és OCR alapú feldolgozását is, ha szükséges.

---

## 🖼️ SUP bitmap felirat automatikus feldolgozása (1.2.0-tól)

A rendszer 1.2.0-tól kezdődően **automatikusan felismeri a bitmap formátumú SUP feliratokat** a `02_extract_subtitles.py` futtatásakor, és ha talál ilyet, automatikusan OCR-rel átalakítja ASS formátumba.

Nincs szükség külön lefuttatni a `sup_to_ass.py` scriptet, mivel a funkció beépült a normál feliratfeldolgozási folyamatba.

1. Győződj meg róla, hogy a `SubtitleEdit.exe` elérhető a PATH-ban.
2. Helyezz el egy `.mkv` fájlt a `data/` mappába, amely tartalmaz bitmap feliratot.
3. Futtasd a következő parancsot:

```bash
python 02_extract_subtitles.py
```

> A rendszer automatikusan felismeri a bitmap feliratokat és elvégzi az átalakítást ASS formátumba a `data/` mappában.

---

## ✅ Sikeres futás ellenőrzése

* **3/A:** Ha a `data/` mappában és a Discord csatornán is megjelenik egy új `.hungarian.ass` fájl, akkor a rendszer helyesen működik.
* **3/B:** Ha a Discord csatornán megjelenik egy új `.hungarian.ass` fájl, akkor a rendszer helyesen működik.
* **SUP feldolgozás esetén:** A `data/` mappában létrejön a konvertált `.ass` fájl a normál feldolgozási folyamat részeként.
* Hiba esetén a részletes naplók a `logs/` mappában találhatók.

---

## 🥪 Tesztelés

A projekt teljes tesztkészlete lefuttatható a következő paranccsal:

```bash
python master_test_automation.py
```

Ez a parancs a `tests/` mappa minden tesztjét lefuttatja, és opcionálisan HTML riportot is készít a `logs/` mappába (ha engedélyezve van a logolás).
