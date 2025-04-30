import os
import sys
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path
import importlib.util

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
SCRIPT_PATH = os.path.join(PROJECT_DIR, "bin", "07_cleanup_data_and_torrents.py")

# Dinamikus import
spec = importlib.util.spec_from_file_location("cleanup_script", SCRIPT_PATH)
cleanup_script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cleanup_script)

def test_cleanup_data_folder_removes_files(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Dummy fájlok létrehozása
    mkv_file = data_dir / "testvideo.mkv"
    ass_file = data_dir / "testsubtitle.ass"
    mkv_file.write_text("dummy mkv")
    ass_file.write_text("dummy ass")

    assert mkv_file.exists()
    assert ass_file.exists()

    # DATA_DIR átállítása
    original_data_dir = cleanup_script.DATA_DIR
    cleanup_script.DATA_DIR = str(data_dir)

    # Mockoljuk a qBittorrent klienst
    dummy_client = MagicMock()

    with patch("bin.07_cleanup_data_and_torrents.create_client_from_config", return_value=dummy_client):
        cleanup_script.cleanup_qbittorrent_and_data_folder()

    # Fájlok törlésének ellenőrzése
    assert not mkv_file.exists()
    assert not ass_file.exists()

    # Visszaállítás
    cleanup_script.DATA_DIR = original_data_dir