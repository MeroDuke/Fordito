import subprocess
import sys
import os
from datetime import datetime
from scripts.logger import log_user_print, LOG_ENABLED

SCRIPT_NAME = "master_test_automation"

def main():
    log_user_print(SCRIPT_NAME, "🧪 Tesztek futtatása pytest-tel...")

    report_args = []
    if LOG_ENABLED:
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_path = os.path.join("logs", f"{date_str}_pytest_report.html")
        report_args = ["--html", report_path, "--self-contained-html"]

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests"] + report_args,
            text=True,
            capture_output=True
        )

        log_user_print(SCRIPT_NAME, result.stdout)
        if result.stderr:
            log_user_print(SCRIPT_NAME, result.stderr)

        if result.returncode == 0:
            log_user_print(SCRIPT_NAME, "✅ Minden teszt sikeresen lefutott!")
        else:
            log_user_print(SCRIPT_NAME, "❌ Hiba történt a tesztek futtatása során.")
            sys.exit(result.returncode)

    except Exception as e:
        log_user_print(SCRIPT_NAME, f"❌ Kritikus hiba: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
