import os
import sys
from unittest.mock import patch
from datetime import datetime
import configparser
import pytest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, PROJECT_DIR)

from scripts.logger import log_user_print, log_tech, is_logging_enabled

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

def test_logging_enabled_true(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "logger_config.ini"
    config_file.write_text("[logger]\nlog_enabled = true\n", encoding="utf-8")

    assert is_logging_enabled(config_file=str(config_file)) is True

def test_logging_enabled_false(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "logger_config.ini"
    config_file.write_text("[logger]\nlog_enabled = false\n", encoding="utf-8")

    assert is_logging_enabled(config_file=str(config_file)) is False

def test_logging_enabled_unknown_value(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "logger_config.ini"
    config_file.write_text("[logger]\nlog_enabled = alma\n", encoding="utf-8")

    assert is_logging_enabled(config_file=str(config_file)) is False

def test_logging_enabled_missing_file(tmp_path):
    fake_file = tmp_path / "config" / "logger_config.ini"
    assert is_logging_enabled(config_file=str(fake_file)) is False

def test_logging_enabled_invalid_ini(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "logger_config.ini"
    config_file.write_text("EZ NEM INI FORMATUM", encoding="utf-8")

    assert is_logging_enabled(config_file=str(config_file)) is False
