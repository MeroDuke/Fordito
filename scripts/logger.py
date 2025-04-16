import os
import datetime

# Master kapcsoló
LOG_ENABLED = True

# Log mappa
def find_project_root(marker=".git"):
    current = os.path.abspath(os.path.dirname(__file__))
    while current != os.path.dirname(current):
        if os.path.isdir(os.path.join(current, marker)):
            return current
        current = os.path.dirname(current)
    raise RuntimeError("❌ Nem található projektgyökér (nincs .git mappa)")

PROJECT_ROOT = find_project_root()
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Segédfüggvény a fájlnévhez
def _get_log_path(script_name: str, suffix: str) -> str:
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = f"{date_str}_{script_name}_{suffix}.log"
    return os.path.join(LOG_DIR, filename)

# Vízszintes vonal a szétválasztáshoz
def _separator():
    return "\n" + "-" * 80 + "\n"

# User logolás
def log_user(script_name: str, message: str):
    if not LOG_ENABLED:
        return
    path = _get_log_path(script_name, "user")
    timestamp = datetime.datetime.now().strftime('%H:%M:%S')
    with open(path, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}")
        f.write(_separator())

# Technikai logolás
def log_tech(script_name: str, message: str):
    if not LOG_ENABLED:
        return
    path = _get_log_path(script_name, "tech")
    timestamp = datetime.datetime.now().strftime('%H:%M:%S')
    with open(path, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}")
        f.write(_separator())
