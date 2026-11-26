#!/usr/bin/env python3
"""對關鍵時間點渲靜幀，供視覺自檢（文字溢出／畫中畫遮擋）。

用法：
    python scripts/check.py [keyframes_dir]

預設 keyframes 輸出到 <repo>/output/keyframes/。
"""

import json
import subprocess
import sys
from pathlib import Path

FPS = 30


def main() -> None:
    remotion_root = Path(__file__).resolve().parent.parent
    repo_root = remotion_root.parent

    keyframes_dir = (
        Path(sys.argv[1]) if len(sys.argv) > 1 else repo_root / "output" / "keyframes"
    )
    keyframes_dir.mkdir(parents=True, exist_ok=True)

    slides_path = repo_root / "slides.json"
    slides = json.loads(slides_path.read_text(encoding="utf-8"))

    times = [3.0, 15.0] + [s["start"] + 0.1 for s in slides["slides"]]
    times = sorted({round(t, 2) for t in times})

    for t in times:
        frame = round(t * FPS)
        out = keyframes_dir / f"frame_{t}.png"
        subprocess.run(
            [
                "npx",
                "remotion",
                "still",
                "src/index.ts",
                "Main",
                str(out),
                f"--frame={frame}",
            ],
            cwd=remotion_root,
            check=True,
        )
        print(f"rendered {out} (t={t}s)")

    print("\n自檢：請人工檢查上述 PNG 是否有文字溢出／畫中畫遮擋文字。")


if __name__ == "__main__":
    main()
