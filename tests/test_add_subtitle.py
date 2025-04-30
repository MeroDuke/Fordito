import os
import subprocess
import sys
import tempfile
import shutil
import pytest


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
SCRIPT_PATH = os.path.join(PROJECT_DIR, "bin", "05_mkvtool_add_subtitle_to_mkv.py")

def test_embed_subtitle_creates_output(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Valódi minimális MKV generálása ffmpeg-gel
    dummy_mkv = data_dir / "testvideo.mkv"
    try:
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=640x360:d=1",
            "-c:v", "libx264", str(dummy_mkv)
        ], check=True, capture_output=True)
    except FileNotFoundError:
        pytest.skip("ffmpeg nem található a rendszerben – teszt átugorva")

    # Dummy ASS
    dummy_ass = data_dir / "testvideo_hungarian_styled.ass"
    dummy_ass.write_text("""[Script Info]\nTitle: Dummy\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\nDialogue: 0,0:00:00.00,0:00:02.00,Default,,0,0,0,,Teszt felirat\n""", encoding="utf-8")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_DIR)
    env["FORDITO_DATA_DIR"] = str(data_dir)

    result = subprocess.run([sys.executable, SCRIPT_PATH], cwd=PROJECT_DIR, env=env, capture_output=True, text=True)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    assert result.returncode == 0

    output_file = data_dir / "testvideo_hungarian.mkv"
    assert output_file.exists()
    assert output_file.stat().st_size > 0
