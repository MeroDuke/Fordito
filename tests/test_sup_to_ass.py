import os
import sys
import importlib.util
import pytest
from unittest.mock import MagicMock

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, PROJECT_DIR)

# Dinamikus import a sup_to_ass.py modulhoz
module_path = os.path.join(PROJECT_DIR, "scripts", "sup_to_ass.py")
spec = importlib.util.spec_from_file_location("sup_to_ass", module_path)
sup_to_ass = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sup_to_ass)


def test_convert_sup_to_ass_missing_sup(monkeypatch):
    monkeypatch.setattr(sup_to_ass.shutil, "which", lambda x: "SubtitleEdit.exe")
    monkeypatch.setattr(sup_to_ass.os.path, "exists", lambda x: False)

    with pytest.raises(RuntimeError, match="Bemeneti SUP fájl nem található"):
        sup_to_ass.convert_sup_to_ass("dummy_input.sup", "dummy_output.ass")

def test_convert_sup_to_ass_missing_exe(monkeypatch):
    monkeypatch.setattr(sup_to_ass.shutil, "which", lambda x: None)

    with pytest.raises(RuntimeError, match="CLI nem található"):
        sup_to_ass.convert_sup_to_ass("dummy_input.sup", "dummy_output.ass")

def test_convert_sup_to_ass_fail_process(monkeypatch):
    mock_process = MagicMock()
    mock_process.stdout.readline.side_effect = ["OCR... : 0%\n", ""]
    mock_process.wait.return_value = 1

    monkeypatch.setattr(sup_to_ass.subprocess, "Popen", lambda *args, **kwargs: mock_process)
    monkeypatch.setattr(sup_to_ass.shutil, "which", lambda x: "SubtitleEdit.exe")
    monkeypatch.setattr(sup_to_ass.os.path, "exists", lambda x: True)

    with pytest.raises(RuntimeError, match="Subtitle Edit hibázott"):
        sup_to_ass.convert_sup_to_ass("dummy_input.sup", "dummy_output.ass")
