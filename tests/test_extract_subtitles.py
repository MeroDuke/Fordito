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

def test_extract_bitmap_subtitle_triggers_sup_to_ass(tmp_path):
    dummy_mkv = tmp_path / "dummy.mkv"
    dummy_sup = tmp_path / "dummy_english.sup"
    dummy_mkv.write_text("dummy")
    dummy_sup.write_text("supdata")

    mock_info = {
        "tracks": [
            {
                "id": 3,
                "type": "subtitles",
                "codec_id": "S_HDMV/PGS",
                "properties": {
                    "language": "eng"
                }
            }
        ]
    }

    with patch.object(subtitle_extractor, "log_user_print") as mock_log:
        with patch("scripts.logger.log_tech"):
            with patch("subprocess.run") as mock_subprocess:
                mock_subprocess.return_value.returncode = 0
                mock_subprocess.return_value.stdout = ""
                with patch("scripts.sup_to_ass.convert_sup_to_ass") as mock_convert:
                    result = subtitle_extractor.extract_bitmap_subtitle(mock_info, str(dummy_mkv), ["eng"], "english")
                    assert result is True
                    mock_convert.assert_called_once()

def test_main_runs_with_no_mkv(monkeypatch):
    monkeypatch.setattr(subtitle_extractor, "find_mkv_file", lambda x: None)
    with patch.object(subtitle_extractor, "log_user_print") as mock_log:
        subtitle_extractor.main()
        mock_log.assert_called_with("02_extract_subtitles", "⚠️ Nincs MKV fájl a 'data' mappában.")
