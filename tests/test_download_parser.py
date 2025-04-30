import importlib.util
import os
import sys
from datetime import datetime
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, PROJECT_DIR)

# Dinamikus import a 01_download_torrent_parser_qbittorrent.py modulhoz
module_path = os.path.join(PROJECT_DIR, "bin", "01_download_torrent_parser_qbittorrent.py")
spec = importlib.util.spec_from_file_location("parser", module_path)
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)

def test_parse_rss_returns_expected(tmp_path):
    test_log_path = tmp_path / "downloaded_torrents.json"
    parser.TORRENT_LOG_PATH = str(test_log_path)

    rss = '''<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0" xmlns:nyaa="https://nyaa.si/xmlns/nyaa">
      <channel>
        <title>Nyaa.si Feed</title>
        <item>
          <title>Bleach - 03</title>
          <link>magnet:?xt=urn:btih:ABC123DEF456</link>
          <nyaa:trusted>Yes</nyaa:trusted>
        </item>
      </channel>
    </rss>
    '''

    # Szűrési feltételek biztos sikere
    parser.KEYWORDS[:] = ["bleach"]
    parser.PREFERRED_QUALITY[:] = [""]  # ne legyen üres
    parser.TARGET_TORRENT_MATCH[:] = []
    parser.TRUSTED_TAG = "Yes"

    parser.extract_episode_id = lambda title: "S01E03"
    parser.is_title_already_downloaded = lambda episode_id: False

    result = parser.parse_rss(rss)
    print("DEBUG result:", result)
    assert result is not None
    assert result["title"] == "Bleach - 03"
    assert result["link"].startswith("magnet:")

def test_add_episode_id_to_log_stub_creates_file(tmp_path):
    test_log_path = tmp_path / "downloaded_torrents.json"
    parser.TORRENT_LOG_PATH = str(test_log_path)

    result_id = parser.add_episode_id_to_log_stub("S01E03", "Bleach - 03", "https://nyaa.si/view/123")

    assert result_id == "1"
    assert test_log_path.exists()

    data = json.loads(test_log_path.read_text(encoding="utf-8"))
    assert "1" in data
    assert data["1"]["episode_id"] == "S01E03"
    assert data["1"]["title"] == "Bleach - 03"
    assert data["1"]["source"] == "https://nyaa.si/view/123"
    assert "added_at" in data["1"]

def test_add_episode_id_to_log_stub_appends_entry(tmp_path):
    test_log_path = tmp_path / "downloaded_torrents.json"
    parser.TORRENT_LOG_PATH = str(test_log_path)

    # első bejegyzés
    parser.add_episode_id_to_log_stub("S01E03", "Bleach - 03", "url1")
    # második bejegyzés
    second_id = parser.add_episode_id_to_log_stub("S01E04", "Bleach - 04", "url2")

    assert second_id == "2"

    data = json.loads(test_log_path.read_text(encoding="utf-8"))
    assert len(data) == 2
    assert data["2"]["episode_id"] == "S01E04"
    assert data["2"]["title"] == "Bleach - 04"
    assert data["2"]["source"] == "url2"
    assert "added_at" in data["2"]
