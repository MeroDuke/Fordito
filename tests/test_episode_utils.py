import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, PROJECT_DIR)

from scripts.episode_utils import extract_episode_id

def test_extract_episode_id_from_standard_title():
    title = "Lycoris Recoil - 03"
    result = extract_episode_id(title)
    assert result == "Lycoris Recoil - S01E03"

def test_extract_episode_id_from_long_number():
    title = "One Piece - 1125"
    result = extract_episode_id(title)
    assert result == "One Piece - S01E1125"

def test_extract_episode_id_from_movie_title():
    title = "Shingeki no Kyojin - The Final Movie"
    result = extract_episode_id(title)
    assert result == "Shingeki no Kyojin - The Final Movie - S00E01"

def test_extract_episode_id_from_invalid_title():
    title = "Just a random string"
    result = extract_episode_id(title)
    assert result is None
