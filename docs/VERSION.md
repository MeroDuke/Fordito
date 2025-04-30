# 🗂️ Verziótörténet – Subtitle Translator

## [1.0.1] – 2025-04-30

### 🐛 Bugfixek és pontosítások

- A költségbecslő modul (estimate_translation_cost.py) most már valósághű tokenhasználat alapján számol becslést.
- Az input tokenek figyelembe veszik a teljes rendszerprompt + batchen belüli összefűzött `user` szöveget.
- Az output tokenek becslése konzervatív `×1.7` szorzóval történik, hogy a valós költség alatt ne maradjon a jelzett érték.
- Ez a módosítás a `03_OpenAI_API_ONLY_4-Turbo_translate_ass.py` scripten keresztül is érvényesül.

---

## [1.0.0.] – 2025-04-29

### ✨ Elkészült funkciók

- Automatizált torrent letöltés RSS alapján
- Subtitle kibontás MKV fájlokból
- AI-alapú feliratfordítás angol vagy japán nyelvről magyarra (OpenAI)
- Kontextusalapú prompt-rendszer (anime synopsis, karakterlista, műfaj)
- Token-alapú költségbecslés és API limit figyelem
- Beszélőalapú stíluskezelés és karakterenkénti színezés
- Konfigurációs rendszer `.ini` fájlokkal
- Discord webhook integráció
- Letöltési naplózás (torrent ismétlődés megelőzése)
- Teljes körű dokumentáció: README, INSTALL, TECH DOC, CONFIG FILES

---

### 🔭 Következő irány (1.1+)

- Videófájlokból automatikus feliratszöveg kinyerés (OCR)
- Képkockánkénti szövegfelismerés + fordítás (OpenAI)
- SRT/ASS generálás időbélyegekkel és opcionális pozícióadatokkal
- A meglévő ASS pipeline újrafelhasználása a generált feliratra
- Formázási adatok (szín, pozíció) megtartása későbbi bővítésként

---
