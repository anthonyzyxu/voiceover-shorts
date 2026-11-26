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


def cut_video(input_path: str, output_path: str, cuts: List[Tuple[float, float]]) -> None:
    """剪掉 cuts 中的區段，寫出 output_path。無 cuts 時直接 copy。"""
    if not cuts:
        subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, "-c", "copy", output_path],
            check=True,
        )
        return

    expr = " or ".join(f"between(t,{s},{e})" for s, e in cuts)
    vf = f"select='not({expr})',setpts=N/FRAME_RATE/TB"
    af = f"aselect='not({expr})',asetpts=N/SR/TB"
    subprocess.run(
        ["ffmpeg", "-y", "-i", input_path,
         "-vf", vf, "-af", af,
         "-c:v", "libx264", "-c:a", "aac", output_path],
        check=True,
    )
