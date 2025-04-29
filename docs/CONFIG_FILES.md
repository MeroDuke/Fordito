# ⚙️ Konfigurációs fájlok – Subtitle Translator

Ez a dokumentáció bemutatja a `config/` mappa tartalmát: milyen konfigurációs fájlok érhetők el, és azokban milyen beállításokat lehet megadni.

---

## 🧹 `cleanup_config.ini`

```ini
[SETTINGS]
keep_recent_days = 14  ; Ennyi napnál régebbi torrent és ideiglenes fájl törlődik
```

Ez szabályozza, hogy a  `userdata\downloaded_torrents.json` fájlban mennyi idő után törlődjenek az eltárolt torrentek.

---

## 🔐 `credentials.ini`

```ini
[OPENAI]
api_key = sk-...

Az OpenAI API kulcsokat tárolja. Legalább az OpenAI kulcs megadása kötelező.

---

## 📣 `discord_config.ini`

```ini
[DISCORD]
webhook_url = https://discord.com/api/webhooks/...
```

A Discord webhook URL-t tartalmazza, ahova a rendszer elküldi a kész feliratot értesítésként.

---

## 🧠 `openai_config.ini`

```ini
[OPENAI]
MODEL_ENG = gpt-4-turbo
MODEL_JPN = gpt-4o
BATCH_SIZE = 3
USE_CONTEXT = false
```

Ez a fájl szabályozza az OpenAI API használatát:

- **MODEL_ENG**: Az angol nyelvű feliratokhoz használt modell neve.
- **MODEL_JPN**: A japán nyelvű feliratokhoz használt modell neve.
- **BATCH_SIZE**: Hány feliratsort fordítunk egyetlen API-hívás során.
- **USE_CONTEXT**: Ha igaz, a rendszer extra anime kontextust (szinopszis, műfajok, karakterlista) ad hozzá a fordítási prompthoz.

---

## 🪄 `postprocess_config.ini`

```ini
[postprocess]
ass_title = 
```
Ez a fájl lehetővé teszi a feliratfájl fejlécében található Title: mező felülírását:
Ha az ass_title mező nem üres, az új szöveg kerül be a .ass fájl fejlécébe.
Ha üresen hagyod (ass_title =), akkor a meglévő Title: sor változatlan marad.

---

## 🔽 `qbittorrent_config.ini`

```ini
[QBITTORRENT]
HOST = localhost
PORT = 8080
USERNAME = pythonteszt
PASSWORD = pythonteszt

[FILTER]
KEYWORDS = 1080p, multisub
PREFERRED_QUALITY = WEB-DL, HEVC, EAC3

[DOWNLOAD]
TRUSTED_TAG = Yes
TARGET_TORRENT_MATCH =
```

Ez a fájl szabályozza a qBittorrent Web API kapcsolatot és az RSS-alapú torrentletöltés szűrését:

HOST / PORT / USERNAME / PASSWORD: a Web UI eléréséhez szükséges adatok.
KEYWORDS: minden itt megadott kulcsszónak szerepelnie kell a torrent címében.
PREFERRED_QUALITY: legalább egy elemnek szerepelnie kell a címben (pl. WEB-DL vagy HEVC).
TRUSTED_TAG = Yes: csak a „Trusted” jelöléssel ellátott torrenteket engedélyezi az RSS feedből.
TARGET_TORRENT_MATCH: ha megadsz értékeket, ezeknek mind szerepelniük kell a torrent címében (case-insensitive). Ha üres, ez a szűrés nem aktív.

---

