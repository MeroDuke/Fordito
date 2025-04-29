# 🎬 Subtitle Translator – AI-alapú feliratfordító rendszer

Ez a projekt egy **automatizált feliratfordító eszköz**, amely képes anime feliratokat angol vagy japán nyelvről **magyarra** fordítani mesterséges intelligencia segítségével. A rendszer `.ass` formátumú feliratokat dolgoz fel, és jellemzően anime torrentekkel együtt használható.

---

## 🚀 Funkciók

- Automatikus .torrent fájl letöltése RSS alapján
- Feliratfájlok kiválasztása és előfeldolgozása
- Japán vagy angol nyelv automatikus felismerése
- AI-alapú fordítás (OpenAI)
- Beszélőalapú stíluskezelés és színezés
- Költségbecslés és tokenlimit figyelembevétele
- Szükség esetén extra kontextus használata az adott címhez
- Magyar nyelvű .ass fájl mentése
- Discord-integráció webhookon keresztül
- Mentett torrentek ürítése
- Lokális munkafájlok eltávolítása a data/ mappából

---

## 📁 Mappastruktúra

```
Fordito/
├─ bin/           # Futtatható scriptek (pl. torrent letöltő, fordító modulok)
├─ config/        # Konfigurációs JSON fájlok (pl. API kulcsok, színezés)
├─ data/          # Bemeneti és kimeneti .ass fájlok
├─ logs/          # Logfájlok és figyelmeztetések
├─ scripts/       # Segéd- és fejlesztési scriptek
├─ userdata/      # Beszélőnevek, színadatok, egyéb felhasználói adatok
├─ .env           # (Opcionális) környezeti változók
└─ master_translator.py  # Az egész folyamatot végrehajtó vezérlőscript
```

---

## 🔧 Telepítés (Részletes útmutató: `INSTALL.md`)

> ⚠️ A telepítési útmutató jelenleg külön fájlban készül, de a minimum lépések:

```bash

git clone <https://github.com/MeroDuke/Fordito.git>
cd Fordito

```
---

▶️ Használat

Kétféle működési mód érhető el:

1. Minden script önállóan is futtatható. Így akár manuálisan, lépésről lépésre is végigvihető a folyamat.
2. A teljes scriptlánc egyben is lefuttatható a `master_translator.py` futtatásával – ekkor minden modul egymás után automatikusan végrehajtódik.

Bármelyik módszert választod:  
> A rendszer automatikusan felismeri a legfrissebb feliratot, és elvégzi a feldolgozást, fordítást, valamint a stílusozást.
---

## ❗ Tippek / Hibakezelés

- Ha a `logs/` vagy más mappa nem létezne, a rendszernek létre kell hoznia őket automatikusan
- Ügyelj arra, hogy a `config/credentials.ini` fájl tartalmazza az érvényes API kulcsot
- Ha hiba történik, a részleteket a `logs/` mappában találod meg. A logolás alapból ki van kapcsolva; a `scripts/logger.py` fájlban lehet ki- és bekapcsolni.

---

## 📌 Állapot

Ez a `README.md` fájl a felhasználói útmutató alapváltozata. A projekt további dokumentációi a `docs/` mappába kerülnek (telepítés, konfigurációk, verziózás, technikai részletek).
