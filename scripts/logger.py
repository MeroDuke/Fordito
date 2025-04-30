import os
import datetime
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Master kapcsoló
LOG_ENABLED = False

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
    import datetime
    import os
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.datetime.now().strftime('%H:%M:%S')
    PROJECT_ROOT = find_project_root()  # vagy hasonló, amit már használtál
    LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
    os.makedirs(LOG_DIR, exist_ok=True)
    path = os.path.join(LOG_DIR, f"{date_str}_{script_name}_{suffix}.log")
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
        f.write("-" * 80 + "\n")
