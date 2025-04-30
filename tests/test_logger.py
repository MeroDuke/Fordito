import os
import sys
from unittest.mock import patch
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, PROJECT_DIR)

from scripts.logger import log_user_print, log_tech

def test_log_user_print(capsys):
    log_user_print("TEST_LOG", "Ez egy felhasználói üzenet.")
    captured = capsys.readouterr()
    assert "Ez egy felhasználói üzenet." in captured.out

def test_log_tech_writes_file():
    with patch("scripts.logger.LOG_ENABLED", True):
        log_tech("TESZT", "Ez technikai log.")

        log_filename = datetime.now().strftime("%Y-%m-%d_TESZT_tech.log")
        log_path = os.path.join("logs", log_filename)

        assert os.path.isfile(log_path)
        with open(log_path, encoding="utf-8") as f:
            content = f.read()
        assert "Ez technikai log." in content
