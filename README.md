# 口播＋動態 PPT 文案背景 視頻自動包裝管線

把一支口播 MOV 自動包裝成 **1080×1920 豎版短視頻（≤2:59）**：背景是「動態 PPT 知識卡片」風格的提煉文案，人物以畫中畫（PiP）呈現在右上角，文字動畫全程對齊人聲時間軸。

> **新手上路**：第一次進專案先看根目錄的 `CLAUDE.md`（Claude Code 會自動載入），是「怎麼跑、有哪些坑」的精簡索引；本文件是完整手冊。

## 技術棧

- **Python**：faster-whisper（`large-v3`）轉錄、pydantic schema 驗證、ffmpeg 裁剪。
- **Node / Remotion（React）**：動態排版＋畫中畫合成、靜幀自檢、渲染輸出。

## 環境安裝

### Python（需 Python 3.12）

> ⚠️ 系統 `python3` 若為 3.14，PyAV（`av`）會編譯失敗。務必用 **python3.12** 建 venv。

```bash
cd python
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt      # faster-whisper、pydantic、av==14.2.0
pip install pytest                    # 跑測試用
```

> `av==14.2.0` 是刻意固定的版本：faster-whisper 1.2.1 與 PyAV ≥15 不相容（`metadata_errors` 參數被移除）。

### Remotion

```bash
cd remotion
npm install
```

## 管線流程

| 步驟 | 動作 | 產物 |
|------|------|------|
| 前置 | 素材超長時，剪開頭暫停／結尾與中間無聲間隔 | `input.trimmed.mov` |
| 1 | 抽音頻 → faster-whisper 轉錄（詞級時間戳） | `transcript.json` |
| 2 | **人機檢查點**：Claude 提煉 PPT 文案 | `slides.json` |
| 3 | Remotion 動態排版＋畫中畫合成 | — |
| 4 | 靜幀自檢 → 渲染 | `日期-主題.mp4` |

### 快速開始

```bash
# 第 0~2 步（裁剪＋轉錄，含第二步前的一切自動化）
cd python
.venv/bin/python run_pipeline.py /path/to/input.mov --max-duration 179

# 第二步：把 transcript.json 交給 Claude 產出 slides.json（見下）
# 之後把 slides.json 放回專案根目錄，並把影片拷貝為 remotion/public/input.mov

# 第 3~4 步：靜幀自檢＋渲染
cd remotion
python3 scripts/check.py                          # 渲關鍵幀供人工自檢
DATE=2026-11-26 THEME=主題 bash scripts/render.sh  # 最終渲染
```

## 第二步（人機檢查點）

此步由 Claude 離線完成，**不接 API**：

1. 讀 `transcript.json`，理解口播核心邏輯。
2. 劃分 **3~6 個邏輯段落**，每段起止時間戳**嚴格對齊語音**。
3. 每頁產出：
   - **主標題** ≤10 字
   - **重點列表 2~4 條**，每條 ≤15 字
   - **高亮詞**：標註需動態高亮的核心詞彙
4. 用 `python/.venv/bin/python -c "from schema import parse_slides; ..."` 驗證合規後輸出 `slides.json`。

## 資料格式

### `transcript.json`

```json
{
  "audio_file": "audio/input.wav",
  "language": "zh",
  "model": "large-v3",
  "segments": [
    {
      "id": 0, "start": 0.0, "end": 3.2, "text": "今天跟大家聊。",
      "words": [{ "word": "今天", "start": 0.0, "end": 0.5 }]
    }
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

## 規則與約定

- **字體**：繁體中文（台灣），PingFang TC（備選 Noto Sans TC）。
- **裁剪**：僅在素材 >2:59 時剪「開頭暫停／結尾與中間無聲間隔」；最終 ≤2:59。
- **輸出**：1080×1920、30fps、`output/日期-主題.mp4`。
- **git**：只存設計／工具／程式碼；`*.mov`、`*.mp4`、`*.wav`、`audio/`、`output/`、`transcript.json`、`slides.json` 不入庫（每次執行都是新 MOV）。

## 測試

```bash
cd python && .venv/bin/python -m pytest ../tests -v          # Python：schema / trim / transcribe
cd remotion && npx vitest run                                # Remotion：timeline / loadData
cd remotion && npx tsc --noEmit                              # 型別檢查
```

## 目錄結構

```
├── python/            # 轉錄＋裁剪（schema / trim / transcribe / run_pipeline）
├── remotion/          # Remotion 專案（components / lib / scripts / Root / Video）
│   ├── public/        # input.mov（渲染時放入，gitignored）
│   └── scripts/       # check.py（自檢）、render.sh（渲染）
├── tests/             # Python 測試
├── slides.json        # 第二步產出（gitignored）
├── transcript.json    # 第一步產出（gitignored）
└── output/            # 成片與關鍵幀（gitignored）
```
