import os
import datetime
import configparser
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Config olvasás
def is_logging_enabled(config_file='config/logger_config.ini'):
    config = configparser.ConfigParser()
    try:
        if not os.path.exists(config_file):
            print("⚠ Logger config fájl hiányzik, logolás tiltva.")
            return False
        config.read(config_file, encoding='utf-8')
        value = config.get('logger', 'log_enabled', fallback='false').strip().lower()
        if value == 'true':
            return True
        elif value == 'false':
            return False
        else:
            print(f"⚠ Ismeretlen log_enabled érték a configban: '{value}' → logolás tiltva.")
            return False
    except Exception as e:
        print(f"⚠ Logger config olvasási hiba: {e} → logolás tiltva.")
        return False

from pathlib import Path

def find_project_root():
    current = Path(__file__).resolve()
    for _ in range(5):  # ne menjünk túl mélyre
        # Git-alapú keresés (fejlesztőknek)
        if (current / ".git").is_dir():
            return current
        # Fallback: ha .git nincs, keressük a tipikus mappákat
        required_dirs = ["bin", "scripts", "data", "config", "userdata"]
        if all((current / d).is_dir() for d in required_dirs):
            return current
        current = current.parent
    raise RuntimeError("❌ Nem található projektgyökér: se .git, se jellemző mappastruktúra.")

PROJECT_ROOT = find_project_root()
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "logger_config.ini")
LOG_ENABLED = is_logging_enabled(CONFIG_PATH)
os.makedirs(LOG_DIR, exist_ok=True)

def _get_log_path(script_name: str, suffix: str) -> str:
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = f"{date_str}_{script_name}_{suffix}.log"
    return os.path.join(LOG_DIR, filename)

def _separator():
    return "\n" + "-" * 80 + "\n"

def log_user(script_name: str, message: str):
    if LOG_ENABLED:
        _write_log(script_name, message, suffix="user")

def log_user_print(script_name: str, message: str):
    print(message)
    log_user(script_name, message)

def log_tech(script_name: str, message: str):
    if LOG_ENABLED:
        _write_log(script_name, message, suffix="tech")

def _write_log(script_name: str, message: str, suffix: str):
    timestamp = datetime.datetime.now().strftime('%H:%M:%S')
    path = _get_log_path(script_name, suffix)
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
        f.write("-" * 80 + "\n")
