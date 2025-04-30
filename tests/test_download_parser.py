import importlib.util
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, PROJECT_DIR)

# Dinamikus import a 01_download_torrent_parser_qbittorrent.py modulhoz
module_path = os.path.join(PROJECT_DIR, "bin", "01_download_torrent_parser_qbittorrent.py")
spec = importlib.util.spec_from_file_location("parser", module_path)
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)

def test_parse_rss_returns_expected():
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