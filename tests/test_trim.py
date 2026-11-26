from trim import _duration, _keep_intervals, compute_cuts, cut_video, result_after_cuts


def test_no_trim_when_under_max():
    # 無靜音、總長 120s < 179 → 回傳 []
    assert compute_cuts([], 120.0) == []


def test_trim_leading_and_trailing_silence():
    # 開頭 0~2s 靜音、結尾 170~180s 靜音 → 剪 [0,2]、[170,180]
    cuts = compute_cuts([(0.0, 2.0), (170.0, 180.0)], 180.0)
    assert cuts == [(0.0, 2.0), (170.0, 180.0)]


def test_cut_mid_silence_only_when_over_max():
    # 總長 200s、中間有 10s 靜音(100~110) → 仍超 179 → 剪該靜音
    cuts = compute_cuts([(100.0, 110.0)], 200.0)
    assert (100.0, 110.0) in cuts


def test_cut_longest_mid_silence_first():
    # 中間兩個靜音 5s 與 30s，需剪到 ≤179 → 先剪 30s 的（剪完 170 已 ≤179）
    cuts = compute_cuts([(50.0, 55.0), (100.0, 130.0)], 200.0)
    assert cuts == [(100.0, 130.0)]


def test_result_after_cuts():
    assert result_after_cuts(200.0, [(100.0, 110.0)]) == 190.0
    assert result_after_cuts(120.0, []) == 120.0


def test_keep_intervals():
    assert _keep_intervals([(1.0, 2.0)], 3.0) == [(0.0, 1.0), (2.0, 3.0)]
    assert _keep_intervals([(0.0, 2.0)], 3.0) == [(2.0, 3.0)]
    assert _keep_intervals([(1.0, 3.0)], 3.0) == [(0.0, 1.0)]
    assert _keep_intervals([], 3.0) == [(0.0, 3.0)]


def test_cut_video_multi_cut(tmp_path):
    import subprocess

    src = tmp_path / "clip.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", "testsrc=duration=3:size=320x240:rate=30",
            "-f", "lavfi", "-i", "sine=frequency=1000:duration=3",
            "-c:v", "libx264", "-c:a", "aac", "-shortest", str(src),
        ],
        check=True, capture_output=True,
    )
    out = tmp_path / "cut.mp4"
    cut_video(str(src), str(out), [(0.5, 1.0), (2.0, 2.5)])
    assert out.exists() and out.stat().st_size > 0
    d = _duration(str(out))
    assert 1.8 < d < 2.3, d

    # 影音時長須一致（防 VFR 影格被重新等距造成不同步）
    def stream_dur(sel: str) -> float:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", sel,
             "-show_entries", "stream=duration", "-of", "csv=p=0", str(out)],
            capture_output=True, text=True,
        )
        return float(r.stdout.strip())

    assert abs(stream_dur("v:0") - stream_dur("a:0")) < 0.1
