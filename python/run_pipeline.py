"""管線串接：裁剪 → 轉錄 → （第二步人機檢查點）→ 渲染。

用法：
    python run_pipeline.py <input.mov> [--max-duration 179] [--model large-v3]
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from transcribe import transcribe  # noqa: E402
from trim import _duration, compute_cuts, cut_video, detect_silence, result_after_cuts  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description="口播視頻自動包裝管線（裁剪＋轉錄）")
    p.add_argument("input", help="輸入 MOV/音檔路徑")
    p.add_argument("--max-duration", type=float, default=179.0, help="成品時長上限（秒）")
    p.add_argument("--model", default="large-v3", help="faster-whisper 模型")
    p.add_argument(
        "-o",
        "--output-json",
        default=str(Path(__file__).resolve().parent.parent / "transcript.json"),
    )
    args = p.parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        sys.exit(f"輸入檔不存在：{input_path}")

    total = _duration(str(input_path))
    print(f"[1/3] 偵測靜音與裁剪（總長 {total:.1f}s，上限 {args.max_duration}s）...")

    silences = detect_silence(str(input_path))
    cuts = compute_cuts(silences, total, max_duration=args.max_duration)

    work_path = input_path
    if cuts:
        trimmed = input_path.with_name(input_path.stem + ".trimmed.mov")
        print(f"      剪去 {len(cuts)} 段靜音 → {trimmed.name}")
        cut_video(str(input_path), str(trimmed), cuts)
        work_path = trimmed
    else:
        print("      無需裁剪")

    final_duration = result_after_cuts(total, cuts)
    if final_duration > args.max_duration:
        print(
            f"⚠️  警告：剪去所有靜音後仍為 {final_duration:.1f}s，"
            f"超過上限 {args.max_duration}s；需另行剪內容才能達標。"
        )

    print(f"[2/3] 轉錄（faster-whisper {args.model}）...")
    transcript = transcribe(
        str(work_path), args.output_json, model_size=args.model
    )
    print(f"      產出 {args.output_json}（{len(transcript.segments)} 段）")

    print()
    print("[3/3] 第二步（人機檢查點）：")
    print("  由 Claude 讀 transcript.json → 產出合規 slides.json（經 schema.py 驗證）。")
    print("  之後：")
    print("    1. 將 slides.json 放回專案根目錄。")
    print("    2. 將（裁剪後）影片拷貝為 remotion/public/input.mov。")
    print("    3. cd remotion && python3 scripts/check.py   # 視覺自檢")
    print('    4. DATE=... THEME=... bash remotion/scripts/render.sh   # 渲染')


if __name__ == "__main__":
    main()
