import os
import json
from unittest.mock import patch, MagicMock
import importlib.util
from pathlib import Path

import pytest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
SCRIPT_PATH = os.path.join(PROJECT_DIR, "bin", "06_discord_post_ASS.py")

# Dinamikus import
spec = importlib.util.spec_from_file_location("discord_post_script", SCRIPT_PATH)
discord_post_script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(discord_post_script)

def test_match_torrent_hash_priority(tmp_path):
    data_dir = tmp_path / "data"
    userdata_dir = tmp_path / "userdata"
    data_dir.mkdir()
    userdata_dir.mkdir()

    subtitle_filename = "[Erai-raws] Aru Majo ga Shinu Made - 07 [1080p CR WEB-DL AVC AAC][MultiSub][90E0C48B]_hungarian_styled.ass"
    subtitle_file = data_dir / subtitle_filename
    subtitle_file.write_text("dummy ass", encoding="utf-8")

    db = {
        "1": {
            "episode_id": "Aru Majo ga Shinu Made - S01E07",
            "title": "[Erai-raws] Aru Majo ga Shinu Made - 07 [1080p CR WEB-DL AVC AAC][MultiSub][90E0C48B]",
            "hash": "7a9c2bea020587fcad937eb525668b6d7564db23",
            "source": "https://nyaa.si/download/1971034.torrent"
        }
    }
    db_path = userdata_dir / "downloaded_torrents.json"
    db_path.write_text(json.dumps(db, indent=2), encoding="utf-8")

    result = discord_post_script.match_torrent(tmp_path, subtitle_filename)
    assert result == "https://nyaa.si/download/1971034.torrent"

def test_main_does_not_send_real_request(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "discord_config.ini"
    config_file.write_text("[discord]\nwebhook_url = https://fake.url/webhook\nstartup_message = Test message\n", encoding="utf-8")

    userdata_dir = tmp_path / "userdata"
    userdata_dir.mkdir()
    db = {
        "1": {
            "episode_id": "Dummy Episode",
            "title": "[Dummy] Test - 01 [DummyHash]",
            "hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "source": "https://dummy.torrent"
        }
    }
    (userdata_dir / "downloaded_torrents.json").write_text(json.dumps(db), encoding="utf-8")

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    subtitle_file = data_dir / "[Dummy] Test - 01 [DummyHash]_hungarian_styled.ass"
    subtitle_file.write_text("dummy ass", encoding="utf-8")

    os.environ["PYTHONPATH"] = str(PROJECT_DIR)

    with patch("bin.06_discord_post_ASS.requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        discord_post_script.PROJECT_DIR = str(tmp_path)
        discord_post_script.CONFIG_FILENAME = config_file.name
        discord_post_script.DATA_DIRNAME = data_dir.name
        discord_post_script.USERDATA_DIRNAME = userdata_dir.name

        discord_post_script.main()

        assert mock_post.call_count >= 2

        # Dinamikus payload ellenőrzés, függetlenül a sorrendtől
        found_text_message = any("json" in call.kwargs for call in mock_post.call_args_list)
        found_file_upload = any("files" in call.kwargs for call in mock_post.call_args_list)

        assert found_text_message, "Nem található szöveges üzenet (json payload)"
        assert found_file_upload, "Nem található fájl feltöltés (files payload)"

        # Audit helper: payloadok kilistázása
        for i, call in enumerate(mock_post.call_args_list):
            print(f"\n🔎 Call {i+1} payload:")
            if "json" in call.kwargs:
                print("  JSON:", call.kwargs["json"])
            if "data" in call.kwargs:
                print("  DATA:", call.kwargs["data"])
            if "files" in call.kwargs:
                print("  FILES:", call.kwargs["files"])
