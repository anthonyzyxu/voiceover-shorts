"""faster-whisper 轉錄 → transcript.json。"""

import json
import os
import subprocess
from typing import List

from faster_whisper import WhisperModel
from schema import Transcript


def _has_audio_stream(path: str) -> bool:
    out = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "a",
            "-show_entries", "stream=codec_type", "-of", "csv=p=0", path,
        ],
        capture_output=True, text=True,
    )
    return out.stdout.strip() != ""


def _extract_audio(input_path: str, wav_path: str) -> None:
    os.makedirs(os.path.dirname(wav_path) or ".", exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", input_path,
            "-vn", "-ac", "1", "-ar", "16000", wav_path,
        ],
        check=True, capture_output=True, text=True,
    )


def _build_transcript(raw_segments, wav_path: str, language: str, model_size: str) -> Transcript:
    """把 faster-whisper 的 segments 轉成 Transcript；空結果拋 RuntimeError。"""
    segments: List[dict] = []
    for seg in raw_segments:
        words = [
            {"word": w.word, "start": round(w.start, 3), "end": round(w.end, 3)}
            for w in (getattr(seg, "words", None) or [])
        ]
        segments.append({
            "id": seg.id,
            "start": round(seg.start, 3),
            "end": round(seg.end, 3),
            "text": seg.text.strip(),
            "words": words,
        })
    if not segments:
        raise RuntimeError("轉錄結果為空：音軌可能全靜音或無有效語音")
    return Transcript.model_validate({
        "audio_file": wav_path,
        "language": language,
        "model": model_size,
        "segments": segments,
    })


def transcribe(
    input_path: str,
    output_json: str,
    model_size: str = "large-v3",
    language: str = "zh",
    wav_path: str = "audio/input.wav",
) -> Transcript:
    """抽音頻 → faster-whisper（word_timestamps=True）→ 寫 transcript.json 並回傳。"""
    if not _has_audio_stream(input_path):
        raise RuntimeError(f"輸入檔無音軌：{input_path}")

    _extract_audio(input_path, wav_path)

    model = WhisperModel(model_size, compute_type="int8")
    segments_iter, _info = model.transcribe(
        wav_path, language=language, word_timestamps=True
    )
    transcript = _build_transcript(segments_iter, wav_path, language, model_size)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(transcript.model_dump(), f, ensure_ascii=False, indent=2)

    return transcript


# 測試用封裝名稱（與計畫介面一致）
run_transcribe = transcribe


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="faster-whisper 轉錄 → transcript.json")
    p.add_argument("input", help="輸入影片/音檔路徑")
    p.add_argument("-o", "--output", default="transcript.json")
    p.add_argument("-m", "--model", default="large-v3")
    p.add_argument("-l", "--language", default="zh")
    args = p.parse_args()

    t = transcribe(args.input, args.output, model_size=args.model, language=args.language)
    print(f"transcribed {len(t.segments)} segments -> {args.output}")
