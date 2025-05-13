import os
import sys
import json
import tempfile
import importlib.util
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
SCRIPT_PATH = os.path.join(PROJECT_DIR, "bin", "02_extract_subtitles.py")

# Dinamikus import
spec = importlib.util.spec_from_file_location("subtitle_extractor", SCRIPT_PATH)
subtitle_extractor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subtitle_extractor)

def test_find_mkv_file(tmp_path):
    test_file = tmp_path / "video.mkv"
    test_file.write_text("fake mkv content")

    found_file = subtitle_extractor.find_mkv_file(tmp_path)
    assert found_file == str(test_file)

def test_run_command_success():
    output = subtitle_extractor.run_command("echo Hello", "Error", shell=True)
    assert "Hello" in output

def test_check_dependency_found():
    assert subtitle_extractor.check_dependency("python") is None

def test_main_runs_with_no_mkv(monkeypatch):
    monkeypatch.setattr(subtitle_extractor, "find_mkv_file", lambda x: None)
    with patch.object(subtitle_extractor, "log_user_print") as mock_log:
        subtitle_extractor.main()
        mock_log.assert_called_with("02_extract_subtitles", "⚠️ Nincs MKV fájl a 'data' mappában.")
