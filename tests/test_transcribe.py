import subprocess

import pytest

from transcribe import run_transcribe


@pytest.fixture
def noaudio(tmp_path):
    """產生一支「純畫面、無音軌」的 mp4，作為無音軌輸入。"""
    p = tmp_path / "noaudio.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", "testsrc=duration=1:size=320x240:rate=30",
            "-c:v", "libx264", str(p),
        ],
        check=True,
        capture_output=True,
    )
    return str(p)


def test_transcribe_no_audio_stream_raises(noaudio):
    with pytest.raises(RuntimeError):
        run_transcribe(noaudio, "/tmp/out.json", model_size="tiny")
