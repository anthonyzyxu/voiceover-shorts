# CLAUDE.md — 口播視頻自動包裝管線

把一支口播 MOV 自動包裝成 **1080×1920 豎版短視頻（≤2:59）**：faster-whisper 轉錄 → Claude 提煉 PPT 文案 → Remotion 動態排版＋畫中畫合成 → 渲染輸出。

## 技術棧

- **Python 3.12**（⚠️ 不是 3.14——PyAV 在 3.14 無 wheel 會編譯失敗）+ faster-whisper `large-v3` + `av==14.2.0`（新版 PyAV ≥15 與 faster-whisper 1.2.1 不相容）
- **Remotion React**（`remotion@4.x`，靜態 JSON import）

## 跑一支新影片（四步）

```bash
# 1. 裁剪＋轉錄（超長自動剪靜音）→ 產出 transcript.json（句級＋詞級時間戳）
cd python && .venv/bin/python run_pipeline.py <input.mov>

# 2. 人機檢查點：Claude 讀 transcript.json → 產出合規 slides.json
#    （3~6 頁；主標題 ≤10 字；每頁 2~4 條、每條 ≤15 字；高亮詞帶時間戳；
#     用 python/.venv/bin/python -c "from schema import parse_slides; ..." 驗證）

# 3. 把（裁剪後）影片拷成 remotion/public/input.mov
cp <trimmed.mov> remotion/public/input.mov

# 4. 自檢＋渲染
cd remotion && python3 scripts/check.py          # 渲關鍵幀自檢
DATE=... THEME=... bash scripts/render.sh        # 輸出 output/日期-主題.mp4
```

## 資料流

`input.mov` → `transcript.json`（轉錄，簡體＋可能有錯字）→ `slides.json`（Claude 提煉的繁體文案＋高亮詞時間戳）→ Remotion 依時間戳驅動文字動畫＋畫中畫。

## 已知重點（勿踩）

- **不入庫**：`transcript.json`、`slides.json`、`output/`、`*.mov/mp4/wav`、`audio/` 皆 gitignored；每次都是新 MOV。
- **VFR 裁剪**：來源若是變動幀率螢幕錄影，`cut_video` 用 `trim/atrim+concat` 保留影格時序；**勿改回 `select+setpts=N/FRAME_RATE/TB`**（會造成影音不同步）。
- **資料載入**：`Root.tsx` 用靜態 JSON import（`../../slides.json`）；**勿改回 `calculateMetadata`+`node:fs`**（webpack 不支援瀏覽器 bundle node:fs）。
- **字體**：繁體中文（台灣），PingFang TC。

## 參考文件

- 環境安裝／用法／資料格式：`README.md`
- 設計決策：`docs/superpowers/specs/2026-11-26-voiceover-ppt-video-design.md`
- 原始規格：`任務.md`

## 測試

```bash
cd python && .venv/bin/python -m pytest ../tests -v   # Python：schema/trim/transcribe
cd remotion && npx vitest run && npx tsc --noEmit     # Remotion：timeline/loadData + 型別
```
