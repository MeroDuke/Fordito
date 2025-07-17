# 🎬 Subtitle Translator – AI-alapú feliratfordító rendszer

> Verzió: 1.4.1 · Frissítve: 2025-07-17

Ez a projekt egy **automatizált feliratfordító eszköz**, amely képes anime feliratokat angol vagy japán nyelvről **magyarra** fordítani mesterséges intelligencia segítségével. A rendszer `.ass` formátumú feliratokat dolgoz fel, és jellemzően anime torrentekkel együtt használható.

---

## 🚀 Funkciók

* Automatikus .torrent fájl letöltése RSS alapján
* Feliratfájlok kiválasztása és előfeldolgozása
* Japán vagy angol nyelv automatikus felismerése
* SUP bitmap feliratok automatikus felismerése és OCR alapú átalakítása ASS formátumba (Subtitle Edit CLI segítségével, ideiglenes fájlkezeléssel)
* AI-alapú fordítás (OpenAI)
* Beszélőalapú stíluskezelés és színezés
* Nem dialógus overlay (`sign_`) sorok pozíció- és formázáshelyreállítása
* Költségbecslés és tokenlimit figyelembevétele
* Sükség esetén extra kontextus használata az adott címhez
* Magyar nyelvű .ass fájl mentése
* Discord-integráció webhookon keresztül (felirathoz automatikusan társított torrent linkkel)
* Mentett torrentek ürítése
* Lokális munkafájlok eltávolítása a data/ mappából
* Konfigurálható logolás `logger_config.ini` fájlból (alapértelemezetten kikapcsolva)

---

## 📁 Mappastruktúra

```
Fordito/
├─ bin/           # Futtatható scriptek (pl. torrent letöltő, fordító modulok)
├─ config/        # Konfigurációs JSON fájlok (pl. API kulcsok, színezés)
├─ data/          # Bemeneti és kimeneti .ass fájlok
├─ logs/          # Logfájlok és figyelmeztetések
├─ scripts/       # Segéd- és fejlesztési scriptek
├─ tests/          # Automata Tesztek
├─ userdata/      # Beszélőnevek, színadatok, egyéb felhasználói adatok
├─ .env           # (Opcionális) környezeti változók
└─ master_translator.py  # Az egész folyamatot végrehajtó vezérlőscript
```

---

## 🔧 Telepítés (Részletes útmutató: `INSTALL.md`)

> ⚠️ A telepítési útmutató jelenleg külön fájlban készül, de a minimum lépések:

```bash
git clone https://github.com/MeroDuke/Fordito.git
cd Fordito
```

---

▶️ Használat

Kétféle működési mód érhető el:

1. Minden script önállóan is futtatható. Így akár manuálisan, lépésről lépésre is végigvihető a folyamat.
2. A teljes scriptlánc egyben is lefuttatható a `master_translator.py` futtatásával – ekkor minden modul egymás után automatikusan végrehajtódik.

Bármelyik módszert választod:

> A rendszer automatikusan felismeri a legfrissebb feliratot, elvégzi a feldolgozást, beleértve a bitmap (SUP) feliratok OCR alapú átalakítását, fordítást, valamint a stílusozást.

---

## ❗ Tippek / Hibakezelés

* Ha a `logs/` vagy más mappa nem létezne, a rendszernek létre kell hoznia őket automatikusan
* Ügyelj arra, hogy a `config/credentials.ini` fájl tartalmazza az érvényes API kulcsot
* Ha hiba történik, a részleteket a `logs/` mappában találod meg. A logolás alapértelezetten ki van kapcsolva; ezt mostantól a `config/logger_config.ini` fájlban lehet vezérelni (`log_enabled = true`).

---

## 🥪 Automatikus tesztelés

A projekt teljes körű unit tesztlefedettséggel rendelkezik. A tesztek a `tests/` mappában találhatók, és a következőképpen futtathatók:

### Tesztek indítása

```bash
python master_test_automation.py
```

Ez a script:

lefuttatja az összes pytest tesztet

ha a logolás engedélyezve van (`logger_config.ini > log_enabled = true`), akkor:

részletes HTML riportot generál a logs/ mappába

a riport neve: `YYYY-MM-DD_HH-MM-SS_pytest_report.html`

## 📌 Állapot

Ez a `README.md` fájl a felhasználói útmutató alapváltozata. A projekt további dokumentációi a `docs/` mappába kerülnek (telepítés, konfigurációk, verziózás, technikai részletek).

---

## 📄 Licenc

Ez a projekt a [Creative Commons Nevezd meg! – Ne add el! – Ne változtasd! 4.0 Nemzetközi](https://creativecommons.org/licenses/by-nc-nd/4.0/deed.hu) licenc alatt áll.

© 2025 AK Fordító

A kód és dokumentáció szabadon megtekinthető és megosztható **nem kereskedelmi célokra**, **változtatás nélkül**, a szerző nevének feltüntetése mellett.

A projekt által használt külső szoftverek részletes listája megtalálható a NOTICE fájlban.
