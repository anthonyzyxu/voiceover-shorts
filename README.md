# voiceover-shorts

**口播影片自動包裝管線** · _Voiceover Video Packaging Pipeline_

> 🤖 **給 AI Agent 用家**：對你的 agent 說這一句，它就會自己讀文件開始幹活：
> 「讀 `README.md` 和 `CLAUDE.md`，然後幫我處理這支口播影片：`/path/to/input.mov`」
>
> _For AI-agent users: paste this one line and the agent reads the docs and gets to work — "Read `README.md` and `CLAUDE.md`, then process this talking-head video: `/path/to/input.mov`."_

把一支口播 MOV 自動包裝成 **1080×1920 豎版短視頻（≤2:59）**：動態 PPT 知識卡片風格的文案背景＋人物畫中畫，文字動畫全程對齊人聲時間軸。

_Turn a talking-head MOV into a **1080×1920 vertical short video (≤2:59)** — animated "PPT knowledge-card" text background plus a picture-in-picture of the speaker, with text animations synced to the voice timeline._

---

## 這是什麼 · What This Is

輸入一支「人在講話」的影片（MOV，字幕燒在畫面、無獨立文字稿），自動產出一支豎版短視頻：

- **轉錄**：faster-whisper（`large-v3`）抽音頻轉錄，含句子級＋詞級時間戳。
- **提煉**：由 AI 把逐字稿提煉成 PPT 式金句（主標題＋重點列表＋高亮詞）。
- **合成**：Remotion 依時間戳驅動文字淡入／上滑／高亮，人物以畫中畫呈現在右上角。
- **出片**：自檢後渲染成 `日期-主題.mp4`。

_Input a talking-head video; output a vertical short: transcribe (faster-whisper), distill into PPT-style copy (AI), composite with Remotion (text animation + PiP), then render._

## 運作流程 · How It Works

```
input.mov（口播影片）
    │
    ├─ (1) 裁剪 trim ── 超長時剪靜音 ──→ input.trimmed.mov
    │
    ├─ (2) 轉錄 transcribe ── faster-whisper large-v3 ──→ transcript.json（句級＋詞級時間戳）
    │
    ├─ (3) 文案提煉（人機檢查點）── AI 讀 transcript.json ──→ slides.json（PPT 金句＋高亮詞）
    │
    └─ (4) Remotion 渲染 ── 依時間戳驅動文字動畫＋畫中畫 ──→ output/日期-主題.mp4
```

## 架構 · Architecture

兩個子專案，以 JSON 檔在步驟間傳遞資料：

| 端 | 目錄 | 職責 | 技術 |
|----|------|------|------|
| Python 端 | `python/` | 裁剪、轉錄、schema 驗證 | faster-whisper、pydantic、ffmpeg |
| Remotion 端 | `remotion/` | 動態排版、畫中畫、渲染 | Remotion（React）、TypeScript |

_Two sub-projects passing JSON between steps: Python (trim/transcribe/validate) and Remotion (animate/composite/render)._

**資料契約**：`transcript.json`（轉錄結果）→ `slides.json`（文案＋時間戳），兩者格式由 `python/schema.py` 定義與驗證。

## 目錄結構 · Project Structure

```
voiceover-shorts/
├── README.md                  # 入口 · Entry
├── LICENSE                    # MIT
├── CONTRIBUTING.md            # 貢獻指南 · Contributing
├── CHANGELOG.md               # 版本記錄 · Changelog
├── CLAUDE.md                  # AI 助手索引 · AI agent index
├── docs/
│   ├── design.md              # 設計文件 · Design
│   └── implementation-plan.md # 實作計畫 · Implementation plan
├── python/                    # 轉錄＋裁剪 · Transcription & trimming
│   ├── requirements.txt
│   ├── schema.py              # 資料契約驗證 · Schema validation
│   ├── trim.py                # 靜音裁剪 · Silence trimming
│   ├── transcribe.py          # faster-whisper 轉錄 · Transcription
│   └── run_pipeline.py        # 管線串接 · Orchestrator
├── remotion/                  # 渲染 · Rendering (Remotion React)
│   ├── remotion.config.ts
│   ├── scripts/
│   │   ├── check.py           # 關鍵幀自檢 · Keyframe self-check
│   │   └── render.sh          # 最終渲染 · Render
│   └── src/
│       ├── Root.tsx           # Composition 註冊
│       ├── Video.tsx          # 主合成 · Main composition
│       ├── components/        # 視覺元件 · Visual components
│       │   ├── Background.tsx
│       │   ├── ProgressBar.tsx
│       │   ├── Slide.tsx
│       │   └── PiP.tsx
│       └── lib/               # 純邏輯 · Pure logic
│           ├── types.ts
│           ├── timeline.ts    # 時間軸 · Timeline
│           └── loadData.ts
└── tests/                     # Python 測試 · Tests
    ├── test_schema.py
    ├── test_trim.py
    └── test_transcribe.py
```

## 需求 · Requirements

- **macOS / Linux**，需 **FFmpeg**（含 `ffprobe`）
- **Python 3.12**（⚠️ 勿用 3.14，PyAV 會編譯失敗）
- **Node.js**（Remotion）
- 首次轉錄會自動下載 `large-v3` 模型（~3GB）

_FFmpeg, Python 3.12 (not 3.14 — PyAV build fails), Node.js. `large-v3` (~3GB) downloads on first transcription._

## 快速開始 · Quick Start

### 1. 安裝環境 · Install

```bash
# Python
cd python
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt      # faster-whisper、pydantic、av==14.2.0
pip install pytest                    # 跑測試用

# Remotion
cd ../remotion && npm install
```

> `av==14.2.0` 是刻意固定的版本：faster-whisper 1.2.1 與 PyAV ≥15 不相容。
> _`av==14.2.0` is pinned: faster-whisper 1.2.1 is incompatible with PyAV ≥15._

### 2. 跑一支影片 · Run a Video

```bash
# (1)+(2) 裁剪＋轉錄 → transcript.json
cd python && .venv/bin/python run_pipeline.py /path/to/input.mov --model large-v3

# (3) 第二步（人機檢查點）：由 AI 讀 transcript.json → 產出 slides.json
#     也可自行撰寫，格式見下方「資料格式」。

# (4) 渲染
cp <裁剪後影片> remotion/public/input.mov          # 或把影片放進 public/
cd remotion && python3 scripts/check.py             # 渲關鍵幀自檢
DATE=2026-11-26 THEME=主題 bash scripts/render.sh   # 輸出 output/日期-主題.mp4
```

## 第二步：AI 文案提煉 · Step 2 (AI Copywriting)

此步由 **AI（Claude）離線完成**，不接 API，也可改用任何 LLM 或手動撰寫 `slides.json`：

1. 讀 `transcript.json`，理解口播邏輯。
2. 劃分 **3~6 個邏輯段落**，每段起止時間戳嚴格對齊語音。
3. 每頁產出：**主標題 ≤10 字**、**重點列表 2~4 條（每條 ≤15 字）**、**高亮詞**（帶時間戳）。

_Step 2 is an offline AI pass (Claude): read the transcript, split into 3–6 segments aligned to speech, and write titles (≤10 chars), bullets (2–4, ≤15 chars each), and highlight words with timestamps._

## 資料格式 · Data Formats

### `transcript.json`

```json
{
  "audio_file": "audio/input.wav",
  "language": "zh",
  "model": "large-v3",
  "segments": [
    { "id": 0, "start": 0.0, "end": 3.2, "text": "今天跟大家聊。",
      "words": [{ "word": "今天", "start": 0.0, "end": 0.5 }] }
  ]
}
```

### `slides.json`

```json
{
  "title": "影片主題",
  "duration": 179.0,
  "slides": [
    {
      "index": 0, "start": 0.0, "end": 28.0, "chapterLabel": "開場",
      "title": "主標題",
      "bullets": [
        { "text": "重點列表條目", "start": 0.0, "end": 12.0,
          "highlight": [{ "word": "高亮詞", "start": 5.0, "end": 5.6 }] }
      ]
    }
  ]
}
```

## 規則與約定 · Rules & Conventions

- **字體**：繁體中文（台灣），PingFang TC（備選 Noto Sans TC）。
- **裁剪**：僅在素材 >2:59 時剪「開頭暫停／結尾與中間無聲間隔」；最終 ≤2:59。
- **輸出**：1080×1920、30fps、`output/日期-主題.mp4`。
- **git**：只存設計／工具／程式碼；`*.mov`、`*.mp4`、`*.wav`、`audio/`、`output/`、`transcript.json`、`slides.json` 不入庫（每次執行都是新 MOV）。

_Font: Traditional Chinese (Taiwan), PingFang TC. Trim silence only when >2:59. Output 1080×1920 @30fps. Generated media/data are git-ignored — every run starts from a fresh MOV._

## 測試 · Tests

```bash
cd python && .venv/bin/python -m pytest ../tests -v   # Python：schema / trim / transcribe
cd remotion && npx vitest run                         # Remotion：timeline / loadData
cd remotion && npx tsc --noEmit                       # 型別檢查
```

## 已知重點 · Gotchas

- **VFR 素材**：來源若是變動幀率螢幕錄影，裁剪務必用 `trim/atrim+concat`（`python/trim.py` 已實作）；`select+setpts=N/FRAME_RATE/TB` 會造成影音不同步。
- **資料載入**：`remotion/src/Root.tsx` 用靜態 JSON import；勿改回 `calculateMetadata`+`node:fs`（webpack 無法把 node:fs 打包進瀏覽器）。

_For VFR screen recordings, cutting must preserve frame timing (trim/atrim+concat) — the alternative causes A/V desync. Root.tsx loads data via static JSON import, not node:fs._

## 相關文件 · Docs

- [設計文件](docs/design.md) — 完整規格與設計決策 · _Design & decisions_
- [實作計畫](docs/implementation-plan.md) — 任務分解記錄 · _Implementation plan_
- [貢獻指南](CONTRIBUTING.md) · [版本記錄](CHANGELOG.md)

## 授權 · License

[MIT](LICENSE)
