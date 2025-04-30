# 🛠️ Telepítési útmutató – Subtitle Translator

Ez a dokumentáció lépésről lépésre bemutatja, hogyan lehet beállítani és elindítani a Subtitle Translator rendszert.

---

## 📋 Rendszerkövetelmények

- **Python**: 3.10.5 vagy újabb
- **Operációs rendszer**: Windows 10/11 (más rendszerekre nem tesztelt)
- **Git** (a repository klónozásához)

---

## 📦 Szükséges Python csomagok

A következő Python csomagokat manuálisan kell telepíteni `pip` segítségével:

```bash

pip install requests tqdm openai tiktoken qbittorrent-api pytest pytest-html

```

---

## 💻 Külső programok (nem Python)

A következő külső eszközök szükségesek a rendszer működéséhez:

| Program          | Funkció                               | Letöltési link |
|------------------|----------------------------------------|----------------|
| **qBittorrent**   | Torrentek automatikus letöltése RSS-ből | [qbittorrent.org](https://www.qbittorrent.org/) |
| **MKVToolNix**    | Feliratok kinyerése MKV fájlokból       | [mkvtoolnix.download](https://mkvtoolnix.download/) |

Telepítés után bizonyosodj meg róla, hogy az alkalmazások elérhetők a PATH-ban vagy helyesen konfiguráltad őket a config fájlokban.

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
    cleanup_config.ini: megadja, hogy milyen régi torrenteket szeretnél megtartani.
    credentials.ini: az OpenAI API-kulcs helye.
    discord_config.ini: a Discord-integrációhoz szükséges webhook URL.
    openai_config.ini: OpenAI beállítások – használt motor, fordítási mennyiség szabályozása, extra kontextus használata.
    postprocess_config.ini: utómunka az ASS fájlban, például ha más szerzőt szeretnél megadni a kész feliratban.
    qbittorrent_config.ini: qBittorrent kapcsolat beállításai – torrent filterek, megbízhatósági beállítások, specifikus torrentek szűrése.

3. Válassz futtatási módot:
    3/A. Futtasd a scripteket külön-külön, egymás után, ha manuálisan szeretnéd végrehajtani a lépéseket.
    3/B. Futtasd a fő scriptet (master_translator.py), ha a teljes folyamatot egyben szeretnéd elindítani:

```bash

python master_translator.py

```

> A rendszer automatikusan felismeri a legfrissebb feliratot és elvégzi a fordítást.

---

## ✅ Sikeres futás ellenőrzése

- 3/A: Ha a data/ mappában és a Discord csatornán is megjelenik egy új .hungarian.ass fájl, akkor a rendszer helyesen működik.
- 3/B: Ha a Discord csatornán megjelenik egy új .hungarian.ass fájl, akkor a rendszer helyesen működik.
- Hiba esetén a részletes naplók a logs/ mappában találhatók.

---

## 🧪 Tesztelés

A projekt teljes tesztkészlete lefuttatható a következő paranccsal:

```bash

python master_test_automation.py

```
Ez a parancs a tests/ mappa minden tesztjét lefuttatja, és opcionálisan HTML riportot is készít a logs/ mappába (ha engedélyezve van a logolás).

---