from trim import compute_cuts


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
