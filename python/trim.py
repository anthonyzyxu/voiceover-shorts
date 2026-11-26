"""靜音偵測與裁剪（ffmpeg 包裝）＋ compute_cuts 純邏輯。"""

import re
import subprocess
from typing import List, Tuple


def compute_cuts(
    silences: List[Tuple[float, float]],
    total_duration: float,
    max_duration: float = 179.0,
) -> List[Tuple[float, float]]:
    """回傳要剪掉的（start,end）區段。

    規則：開頭靜音（start==0）與結尾靜音（end==total_duration）恆剪；
    中間靜音僅當總時長仍 >max_duration 時由最長依序剪。
    """
    leading: List[Tuple[float, float]] = []
    trailing: List[Tuple[float, float]] = []
    mids: List[Tuple[float, float]] = []
    for s, e in silences:
        if s == 0:
            leading.append((s, e))
        elif e == total_duration:
            trailing.append((s, e))
        else:
            mids.append((s, e))

    cuts = leading + trailing
    remaining = total_duration - sum(e - s for s, e in cuts)

    if remaining <= max_duration:
        return cuts

    for s, e in sorted(mids, key=lambda r: r[1] - r[0], reverse=True):
        cuts.append((s, e))
        remaining -= e - s
        if remaining <= max_duration:
            break

    return cuts


def result_after_cuts(total_duration: float, cuts: List[Tuple[float, float]]) -> float:
    """剪去 cuts 後的最終時長。"""
    return total_duration - sum(e - s for s, e in cuts)


def _duration(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def detect_silence(
    input_path: str,
    min_silence: float = 0.5,
    noise_threshold: str = "-30dB",
) -> List[Tuple[float, float]]:
    """跑 ffmpeg silencedetect，回傳靜音區段清單（結尾靜音延伸到總長）。"""
    cmd = [
        "ffmpeg", "-i", input_path,
        "-af", f"silencedetect=noise={noise_threshold}:d={min_silence}",
        "-f", "null", "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    stderr = proc.stderr
    starts = [float(m) for m in re.findall(r"silence_start:\s*(-?[\d.]+)", stderr)]
    ends = [float(m) for m in re.findall(r"silence_end:\s*(-?[\d.]+)", stderr)]
    silences = list(zip(starts, ends))
    if len(starts) > len(ends):
        # 結尾仍在靜音（無 silence_end）→ 延伸到總長
        silences.append((starts[-1], _duration(input_path)))
    return silences


def _keep_intervals(
    cuts: List[Tuple[float, float]], total_duration: float
) -> List[Tuple[float, float]]:
    """由要剪掉的區段推導「保留區間」（互補）。"""
    keep: List[Tuple[float, float]] = []
    cursor = 0.0
    for s, e in sorted(cuts):
        if s > cursor:
            keep.append((cursor, s))
        cursor = max(cursor, e)
    if cursor < total_duration:
        keep.append((cursor, total_duration))
    return keep


def cut_video(input_path: str, output_path: str, cuts: List[Tuple[float, float]]) -> None:
    """剪掉 cuts 中的區段，寫出 output_path。無 cuts 時直接 copy。"""
    if not cuts:
        subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, "-c", "copy", output_path],
            check=True,
        )
        return

    keep = _keep_intervals(cuts, _duration(input_path))
    if not keep:
        raise RuntimeError("裁剪後無任何保留片段")

    # 用 trim/atrim + concat 逐段裁剪再拼接，保留各段原始 PTS 間距。
    # 來源為 VFR 時，select+setpts=N/FRAME_RATE/TB 會把影格重新等距，
    # 造成影音不同步；trim 保留原始時序，才不會讓影片播放變快。
    n = len(keep)
    parts = []
    for i, (s, e) in enumerate(keep):
        parts.append(f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}]")
        parts.append(f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS[a{i}]")
    v_in = "".join(f"[v{i}]" for i in range(n))
    a_in = "".join(f"[a{i}]" for i in range(n))
    parts.append(f"{v_in}concat=n={n}:v=1:a=0[outv]")
    parts.append(f"{a_in}concat=n={n}:v=0:a=1[outa]")
    filter_complex = ";".join(parts)

    subprocess.run(
        ["ffmpeg", "-y", "-i", input_path,
         "-filter_complex", filter_complex,
         "-map", "[outv]", "-map", "[outa]",
         "-c:v", "libx264", "-c:a", "aac", output_path],
        check=True,
    )
