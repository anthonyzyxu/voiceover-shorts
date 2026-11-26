# 口播＋動態 PPT 文案背景 視頻自動包裝管線 實作計畫

> 本計畫已於 2026-11-26 全部實作完成；保留原始任務分解，供理解設計決策。

**Goal:** 把一支口播 MOV 自動包裝成 1080×1920 豎版短視頻（≤2:59）：faster-whisper 轉錄 → Claude 提煉 PPT 文案 → Remotion 動態排版＋畫中畫合成 → 自檢渲染。

**Architecture:** 兩支子專案＋共享資料契約。Python 端（`python/`）負責裁剪與轉錄，產出 `transcript.json`；第二步由 Claude 離線產出 `slides.json`；Remotion 端（`remotion/`）讀取兩份 JSON，依時間戳渲染。資料以 JSON 檔在步驟間傳遞，人機檢查點在第二步。

**Tech Stack:** Python（faster-whisper、pydantic、ffmpeg）、Node/Remotion（React、TypeScript、vitest）。

**Spec:** `docs/design.md`

## Global Constraints

- 輸出：**1080×1920、30fps、≤2:59（≤179.0 秒）**，檔名 `日期-主題.mp4`。
- 字體：**繁體中文（台灣）**，默認 `PingFang TC`，備選 `Noto Sans TC`。
- Whisper：`faster-whisper`、`large-v3`、`language="zh"`、`word_timestamps=True`、CPU `int8`。
- 文案字數：主標題 **≤10 字**；列表每條 **≤15 字**；每頁 **2~4 條**；全片 **3~6 頁**。
- 第二步由 Claude 離線完成（方案 A），**不接 Claude API**。
- 版面：PiP 右上角（圓角＋微陰影＋呼吸邊框）；文字在左／上；淺色商務漸變背景＋網格紋理＋頂部進度／章節標籤。
- 音頻：保留 `input.mov` 原聲；目錄下有 BGM 檔則加極低音量墊樂，否則僅原聲。
- 裁剪：僅在素材 >2:59 時剪「開頭暫停／結尾與中間無聲間隔」；最終 ≤2:59。
- git：只保存**設計／工具／過程更新**（docs、程式碼、README、schema）。`*.mov`、`*.mp4`、`*.wav`、`audio/`、`output/` 與每次執行的資料產物（`transcript.json`、`slides.json`）**不入庫**。每次執行都是全新的 MOV。

## Review Focus

- [ ] **輸入檔無音軌或全靜音** → 裁剪/轉錄應明確報錯，而非產出空 `transcript.json` 或空白成片。→ Task 4 加測試。
- [ ] **輸入檔本身 ≤2:59** → 裁剪應為 no-op，不重編碼、不損壞素材。→ Task 3 加測試。
- [ ] **slides.json 段落未完全覆蓋影片時長（有缺口／重疊）** → 時間軸邏輯不崩潰；缺口時間不顯示任何 slide。→ Task 5 加測試。
- [ ] **bullet 為空或 >15 字／標題 >10 字** → schema 驗證拒絕並給明確訊息。→ Task 2 加測試。
- [ ] **highlight 時間戳落在其 bullet 範圍外** → 時間軸邏輯安全處理（忽略或 clamp），不拋異常。→ Task 5 加測試。

---

## File Structure

```
project_video_aienhanced/
├── 任務.md
├── docs/design.md
├── docs/implementation-plan.md
├── .gitignore
├── python/
│   ├── requirements.txt        # faster-whisper, pydantic
│   ├── schema.py               # transcript.json / slides.json 驗證（pydantic）
│   ├── trim.py                 # 靜音偵測 + compute_cuts + ffmpeg 裁剪
│   ├── transcribe.py           # faster-whisper → transcript.json（CLI）
│   └── run_pipeline.py         # 串接：trim → transcribe（orchestrator）
├── tests/
│   ├── test_schema.py
│   └── test_trim.py
├── remotion/
│   ├── package.json
│   ├── tsconfig.json
│   ├── remotion.config.ts
│   ├── vitest.config.ts
│   ├── src/
│   │   ├── index.ts            # registerRoot
│   │   ├── Root.tsx            # <Composition>
│   │   ├── Video.tsx           # 主合成：Background + Slides + PiP
│   │   ├── components/
│   │   │   ├── Background.tsx
│   │   │   ├── ProgressBar.tsx
│   │   │   ├── Slide.tsx
│   │   │   └── PiP.tsx
│   │   └── lib/
│   │       ├── types.ts        # Slide/Bullet/Highlight/Transcript 型別
│   │       ├── timeline.ts     # 純邏輯：currentSlide / visibleBullets / activeHighlights
│   │       └── loadData.ts     # 讀 slides.json + transcript.json
│   └── src/lib/__tests__/timeline.test.ts
├── audio/                      # 抽取的音頻（gitignored）
└── output/                     # 成片與關鍵幀（gitignored）
```

---

## Task 1: 專案初始化（git + Python env + Remotion 專案）

**Files:**
- Create: `.gitignore`
- Create: `python/requirements.txt`
- Create: `remotion/package.json`, `remotion/tsconfig.json`, `remotion/remotion.config.ts`, `remotion/vitest.config.ts`
- Create: `remotion/src/index.ts`（暫時 `registerRoot` 空殼）

**Interfaces:**
- Produces: 兩個可運行的環境（`python -c "import faster_whisper, pydantic"` 成功；`cd remotion && npx remotion --version` 成功）。

- [ ] **Step 1: 初始化 git 與忽略規則**

```bash
cd /Users/anthony/Development/project_video_aienhanced
git init
```

`.gitignore` 內容（排除大型/生成檔）：
```
# 輸入與成品（每次皆新，不入庫）
*.mov
*.mp4
*.wav
audio/
output/
# 每次執行的資料產物
transcript.json
slides.json
# 環境
python/.venv/
__pycache__/
remotion/node_modules/
remotion/.cache/
.DS_Store
```

- [ ] **Step 2: 建立 Python 環境**

```bash
cd python && python3 -m venv .venv && source .venv/bin/activate
pip install faster-whisper pydantic
pip freeze | grep -iE 'faster-whisper|pydantic' > requirements.txt
```

- [ ] **Step 3: 建立 Remotion 專案（手動，React 版）**

`remotion/package.json` 依賴：`remotion`、`@remotion/cli`、`react`、`react-dom`，devDeps：`@types/react`、`typescript`、`vitest`、`@remotion/bundler`。`remotion.config.ts` 設定 `Config.setVideoImageFormat('jpeg')`、`Config.setOverwriteOutput(true)`。

```bash
cd remotion && npm install
```

- [ ] **Step 4: 驗證環境**

Run: `python -c "import faster_whisper, pydantic; print('ok')"` → 輸出 `ok`
Run: `cd remotion && npx remotion --version` → 顯示版本號

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "chore: scaffold python + remotion projects"
```

---

## Task 2: 資料契約 schema 與驗證（pydantic）

**Files:**
- Create: `python/schema.py`
- Create: `tests/test_schema.py`
- Modify: `python/requirements.txt`（確認含 pydantic）

**Interfaces:**
- Produces:
  - `parse_transcript(data: dict) -> Transcript`（`Transcript`、`Segment`、`Word` 型別）
  - `parse_slides(data: dict) -> Slides`（`Slides`、`Slide`、`Bullet`、`Highlight` 型別）
  - 驗證失敗拋 `pydantic.ValidationError`

**約束（來自 spec，寫進驗證）**：`title` 1~10 字；`bullet.text` 1~15 字；每頁 `bullets` 2~4 條；`slides` 3~6 頁；`start <= end`；`highlight` 可空。

- [ ] **Step 1: 寫失敗測試**

`tests/test_schema.py`：
```python
import pytest
from pydantic import ValidationError
from schema import parse_transcript, parse_slides

VALID_TRANSCRIPT = {"audio_file":"audio/input.wav","language":"zh","model":"large-v3",
  "segments":[{"id":0,"start":0.0,"end":3.2,"text":"今天跟大家聊。","words":[{"word":"今天","start":0.0,"end":0.5}]}]}

def test_parse_transcript_ok():
    t = parse_transcript(VALID_TRANSCRIPT)
    assert t.segments[0].text == "今天跟大家聊。"
    assert t.segments[0].words[0].end == 0.5

def test_title_over_10_chars_rejected():
    data = {"title":"t","duration":179.0,"slides":[{"index":0,"start":0.0,"end":10.0,
      "chapterLabel":"開場","title":"這是一個超過十個字的超長主標題","bullets":[
      {"text":"第一條重點","start":0.0,"end":5.0,"highlight":[]}]}]}
    with pytest.raises(ValidationError):
        parse_slides(data)

def test_bullet_over_15_chars_rejected():
    # bullet.text = 16 字 → ValidationError
    ...

def test_bullet_count_out_of_range_rejected():
    # bullets 僅 1 條 → ValidationError
    ...

def test_slide_count_out_of_range_rejected():
    # slides 僅 2 頁 → ValidationError
    ...
```

- [ ] **Step 2: 跑測試確認失敗**

Run: `cd python && .venv/bin/python -m pytest ../tests/test_schema.py -v`
Expected: FAIL（`ModuleNotFoundError: schema`）

- [ ] **Step 3: 實作 `python/schema.py`**

用 pydantic `BaseModel` 定義 `Word`、`Segment`、`Transcript`、`Highlight`、`Bullet`、`Slide`、`Slides`；`parse_transcript`/`parse_slides` 即 `Model.model_validate(data)`。字數上限用 `Field(max_length=…)`、列表數量用 `Field(min_length=…, max_length=…)`、時間用 `model_validator` 檢查 `start <= end`。

- [ ] **Step 4: 跑測試確認通過**

Run: `cd python && .venv/bin/python -m pytest ../tests/test_schema.py -v`
Expected: PASS（全部通過）

- [ ] **Step 5: Commit**

```bash
git add python/schema.py tests/test_schema.py python/requirements.txt
git commit -m "feat: add transcript/slides schema validation"
```

---

## Task 3: 靜音偵測與裁剪（ffmpeg）

**Files:**
- Create: `python/trim.py`
- Create: `tests/test_trim.py`

**Interfaces:**
- Produces:
  - `compute_cuts(silences: list[tuple[float,float]], total_duration: float, max_duration: float = 179.0) -> list[tuple[float,float]]`：回傳要剪掉的（start,end）區段。
  - `detect_silence(input_path: str, min_silence: float = 0.5, noise_threshold: str = "-30dB") -> list[tuple[float,float]]`：跑 `ffmpeg silencedetect`。
  - `cut_video(input_path: str, output_path: str, cuts: list[tuple[float,float]]) -> None`：用 `select`/`aselect` filter 剪接。

**規則**：開頭靜音（0 起到第一個發聲）與結尾靜音**恆剪**；中間靜音**僅當總時長仍 >max_duration 時由最長依序剪**。

- [ ] **Step 1: 寫失敗測試**

`tests/test_trim.py`：
```python
from trim import compute_cuts

def test_no_trim_when_under_max():
    # 無靜音、總長 120s < 179 → 回傳 []
    assert compute_cuts([], 120.0) == []

def test_trim_leading_and_trailing_silence():
    # 開頭 0~2s 靜音、結尾 170~180s 靜音 → 剪 [0,2]、[170,180]
    cuts = compute_cuts([(0.0,2.0),(170.0,180.0)], 180.0)
    assert cuts == [(0.0,2.0),(170.0,180.0)]

def test_cut_mid_silence_only_when_over_max():
    # 總長 200s、中間有 10s 靜音(100~110) → 仍超 179 → 剪該靜音
    cuts = compute_cuts([(100.0,110.0)], 200.0)
    assert (100.0,110.0) in cuts

def test_cut_longest_mid_silence_first():
    # 中間兩個靜音 5s 與 30s，需剪到 ≤179 → 先剪 30s 的
    ...
```

- [ ] **Step 2: 跑測試確認失敗**

Run: `cd python && .venv/bin/python -m pytest ../tests/test_trim.py -v`
Expected: FAIL（`ModuleNotFoundError: trim`）

- [ ] **Step 3: 實作 `compute_cuts`（純邏輯，先只做這支）**

演算法：`total - 剪去開頭/結尾靜音` 得「發聲總長」；若 >max_duration，把中間靜音依時長**由長到短**排序，逐一加入 cuts 直到「發聲總長 - 已剪中間」≤max_duration。開頭/結尾判定：`start==0` 者為開頭，`end==total_duration` 者為結尾。`detect_silence` 與 `cut_video` 本步先留 stub（下一 Task 用到）。

- [ ] **Step 4: 跑測試確認通過**

Run: `cd python && .venv/bin/python -m pytest ../tests/test_trim.py -v`
Expected: PASS

- [ ] **Step 5: 實作 `detect_silence` 與 `cut_video`（ffmpeg 包裝）**

`detect_silence` 解析 `ffmpeg -af silencedetect=noise=-30dB:d=0.5 -f null -` 的 stderr 輸出；`cut_video` 用 `-vf "select='...', setpts=..." -af "aselect='...', aselect setpts=..."`（或 `-f concat` 重接保留片段）產出裁剪後檔案。

- [ ] **Step 6: 冒煙測試（對合成音頻）**

Run: `ffmpeg -f lavfi -i "sine=frequency=1000:duration=3" tests/fixtures/tone.wav` 產生測試音檔，跑 `detect_silence` 確認無拋錯、回傳合理值。
Expected: 無錯誤，回傳 `list`。

- [ ] **Step 7: Commit**

```bash
git add python/trim.py tests/test_trim.py
git commit -m "feat: silence detection and trim logic"
```

---

## Task 4: 轉錄腳本（faster-whisper）

**Files:**
- Create: `python/transcribe.py`

**Interfaces:**
- Consumes: `python/schema.py` 的 `Transcript`／`parse_transcript`。
- Produces:
  - `transcribe(input_path: str, output_json: str, model_size: str = "large-v3", language: str = "zh") -> Transcript`：抽音頻 → faster-whisper（`word_timestamps=True`）→ 寫 `transcript.json` 並回傳。
  - CLI：`python transcribe.py <input.mov> -o transcript.json`

- [ ] **Step 1: 寫失敗測試（無音軌 → 報錯）**

`tests/test_transcribe.py`：
```python
import subprocess, pytest
def test_transcribe_no_audio_stream_raises():
    # 用 ffmpeg 產生「純畫面無音軌」的 mp4 fixture
    with pytest.raises(RuntimeError):
        run_transcribe("tests/fixtures/noaudio.mp4", "/tmp/out.json")
```

（`run_transcribe` 為 `transcribe.py` 內可呼叫的封裝，抽音頻失敗即拋 `RuntimeError`。）

- [ ] **Step 2: 跑測試確認失敗**

Run: `cd python && .venv/bin/python -m pytest ../tests/test_transcribe.py -v`
Expected: FAIL（未定義）

- [ ] **Step 3: 實作 `python/transcribe.py`**

抽音頻：`ffmpeg -i input -vn -ac 1 -ar 16000 audio/input.wav`；若 `ffprobe` 無音軌 stream 即拋 `RuntimeError`。轉錄：`WhisperModel(model_size, compute_type="int8")` → `model.transcribe(wav, language=language, word_timestamps=True)` → 組出 `Transcript` 結構（`segments[].words[]` 由 `result.words`/`word_timestamps` 對齊）→ 寫 JSON（`ensure_ascii=False, indent=2`）。

- [ ] **Step 4: 冒煙測試（對合成音檔跑真實模型，首次會下載 large-v3）**

Run: `cd python && .venv/bin/python transcribe.py tests/fixtures/tone.wav -o /tmp/transcript.json`
Expected: 產出 `/tmp/transcript.json` 且能通過 `parse_transcript` 驗證；無音軌異常。

- [ ] **Step 5: Commit**

```bash
git add python/transcribe.py tests/test_transcribe.py
git commit -m "feat: faster-whisper transcription to transcript.json"
```

---

## Task 5: 時間軸純邏輯（Remotion, TypeScript）

**Files:**
- Create: `remotion/src/lib/types.ts`
- Create: `remotion/src/lib/timeline.ts`
- Create: `remotion/src/lib/__tests__/timeline.test.ts`

**Interfaces:**
- Consumes: `slides.json` 結構（`Slide`/`Bullet`/`Highlight`，欄位同 spec §5）。
- Produces:
  - `currentSlide(slides: Slide[], t: number): Slide | null`：`start <= t < end` 的 slide；缺口回 `null`。
  - `visibleBullets(slide: Slide, t: number): Bullet[]`：`bullet.start <= t` 的 bullet（依序）。
  - `activeHighlights(slide: Slide, t: number): Highlight[]`：`highlight.start <= t < highlight.end`。

- [ ] **Step 1: 寫失敗測試**

`remotion/src/lib/__tests__/timeline.test.ts`：
```ts
import { describe, it, expect } from 'vitest'
import { currentSlide, visibleBullets, activeHighlights } from '../timeline'

const slides = [
  { index: 0, start: 0, end: 10, chapterLabel: '開場', title: '標題一',
    bullets: [{ text: '第一條', start: 0, end: 5, highlight: [{ word: '重點', start: 2, end: 3 }] }] },
  { index: 1, start: 10, end: 20, chapterLabel: '主體', title: '標題二', bullets: [] },
]

it('currentSlide 回傳涵蓋 t 的 slide，缺口回 null', () => {
  expect(currentSlide(slides, 5)?.index).toBe(0)
  expect(currentSlide(slides, 25)).toBeNull()
})

it('visibleBullets 依 start 過濾', () => {
  expect(visibleBullets(slides[0], 1)).toHaveLength(1)
  expect(visibleBullets(slides[0], -1)).toHaveLength(0)
})

it('activeHighlights 依 [start,end) 判斷，越界 highlight 不拋錯', () => {
  expect(activeHighlights(slides[0], 2.5).map(h => h.word)).toEqual(['重點'])
  expect(() => activeHighlights(slides[0], 99)).not.toThrow()
})
```

- [ ] **Step 2: 跑測試確認失敗**

Run: `cd remotion && npx vitest run src/lib/__tests__/timeline.test.ts`
Expected: FAIL（模組未建）

- [ ] **Step 3: 實作 `types.ts` 與 `timeline.ts`**

`types.ts` 定義 `Highlight`、`Bullet`、`Slide`、`Slides`、`Transcript` 介面（欄位對應 spec §5）。`timeline.ts` 實作三支純函式；`currentSlide` 用線性掃描或二分；`activeHighlights` 對越界時間安全回傳 `[]`。

- [ ] **Step 4: 跑測試確認通過**

Run: `cd remotion && npx vitest run src/lib/__tests__/timeline.test.ts`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add remotion/src/lib
git commit -m "feat: timeline pure logic"
```

---

## Task 6: Remotion 視覺元件

**Files:**
- Create: `remotion/src/components/Background.tsx`
- Create: `remotion/src/components/ProgressBar.tsx`
- Create: `remotion/src/components/Slide.tsx`
- Create: `remotion/src/components/PiP.tsx`

**Interfaces:**
- Consumes: `timeline.ts` 的 `visibleBullets`/`activeHighlights`、`types.ts`。
- Produces: 四個元件（props 見下）。

- [ ] **Step 1: 寫元件並以 TypeScript 型別檢查通過**

各元件 props：
- `Background`：無 props，渲染淺色商務漸變＋微弱網格／紋理（CSS `linear-gradient`＋`backgroundImage` 網格線）。
- `ProgressBar`：`{ current: number; total: number; label: string }`，頂部顯示章節標籤＋進度條。
- `Slide`：`{ slide: Slide; t: number }`，用 `visibleBullets`/`activeHighlights` 渲染標題與列表；bullet 用 `spring`/`fade` 上滑淡入；高亮詞加黃底／放大變色。
- `PiP`：`{ src: string; width: number; height: number }`，右上角圓角＋微陰影＋呼吸邊框（`keyframes` 邊框色透明度），用 `<Video>` 或 `<OffthreadVideo>` 播放。

- [ ] **Step 2: 型別檢查**

Run: `cd remotion && npx tsc --noEmit`
Expected: 無錯誤

- [ ] **Step 3: 靜態渲染冒煙測試**

用 `@remotion/renderer` 的 `renderStill` 對一個假 `Slide` 渲一幀 PNG，確認無 runtime 錯誤且檔案非空。

- [ ] **Step 4: Commit**

```bash
git add remotion/src/components
git commit -m "feat: remotion visual components"
```

---

## Task 7: 組合 Composition 與資料載入

**Files:**
- Create: `remotion/src/lib/loadData.ts`
- Create: `remotion/src/Video.tsx`
- Create: `remotion/src/Root.tsx`
- Modify: `remotion/src/index.ts`（`registerRoot(Root)`）

**Interfaces:**
- Produces:
  - `loadSlides(path: string): Slides`、`loadTranscript(path: string): Transcript`（讀 JSON，throw on parse error）。
  - `<Video/>`：props `{ slides: Slides; transcript: Transcript; videoSrc: string; audioSrc?: string }`，組出 Background＋ProgressBar＋每時刻的 Slide＋PiP。

- [ ] **Step 1: 寫 `loadData.ts` 並以測試驗證**

`loadData.test.ts`：對 fixture `slides.json`（合法）與（缺 `duration` 欄）驗證載入成功／拋錯。

- [ ] **Step 2: 實作 `Video.tsx` 與 `Root.tsx`**

`Root.tsx` 用 `<Composition id="Main" component={Video} durationInFrames={round(slides.duration*30)} fps={30} width={1080} height={1920} defaultProps={…}/>`；`Video.tsx` 以 `useCurrentFrame()` 算 `t=frame/30`，`currentSlide` 決定當前頁，並把 `transcript` 傳入以供音軌對齊（本步先接 `slides`）。

- [ ] **Step 3: 型別檢查＋renderStill 冒煙**

Run: `cd remotion && npx tsc --noEmit`
Run: `npx remotion still src/index.ts Main out/preview.png --props=…`（用臨時 fixture `slides.json`）
Expected: 產出 `out/preview.png` 非空。

- [ ] **Step 4: Commit**

```bash
git add remotion/src
git commit -m "feat: composition and data loading"
```

---

## Task 8: 自檢（renderStill）＋最終渲染腳本

**Files:**
- Create: `remotion/src/check.ts`（或 `remotion/scripts/check.sh`）
- Create: `remotion/scripts/render.sh`

**Interfaces:**
- Produces:
  - `renderKeyframes(...)`：對指定時間點（預設 3s、15s，及每頁起點）各渲一張 PNG 到 `output/keyframes/`。
  - `renderFinal(...)`：`npx remotion render src/index.ts Main output/日期-主題.mp4`。

- [ ] **Step 1: 寫自檢腳本**

`check.ts` 用 `renderStill` 對 `[3, 15]` 秒＋每頁 `start+0.1` 秒渲關鍵幀，輸出到 `output/keyframes/`。渲染後提示人工檢查「文字是否溢出／PiP 是否遮擋」。

- [ ] **Step 2: 冒煙（對 fixture slides 渲 2 幀）**

Run: `cd remotion && npx tsx src/check.ts --props=…`
Expected: `output/keyframes/` 出現對應 PNG。

- [ ] **Step 3: 寫最終渲染腳本**

`render.sh`：`cd remotion && npx remotion render src/index.ts Main ../output/${DATE}-${THEME}.mp4`（`${DATE}`/`${THEME}` 由環境變數傳入）。確認輸出畫質：`Config.setVideoImageFormat`、`Config.setPixelFormat`、CRF 等（值留實作者依畫質需求設定）。

- [ ] **Step 4: Commit**

```bash
git add remotion/src/check.ts remotion/scripts
git commit -m "feat: keyframe self-check and render scripts"
```

---

## Task 9: 管線串接 orchestrator ＋ 使用說明

**Files:**
- Create: `python/run_pipeline.py`
- Create: `README.md`

**Interfaces:**
- Produces: `run_pipeline.py` 依序執行：`trim` → `transcribe`，並在第二步停下印出「請 Claude 產出 slides.json 後再執行渲染」。

- [ ] **Step 1: 寫 `run_pipeline.py`**

`python run_pipeline.py <input.mov> --max-duration 179`：呼叫 `detect_silence`/`compute_cuts`（僅超長時裁剪）→ `cut_video` 得 `input.trimmed.mov` → `transcribe` 得 `transcript.json`。印出清晰的階段提示與下一步指引。

- [ ] **Step 2: 冒煙（合成短音檔全流程，不含真實模型）**

用 `tests/fixtures/tone.wav` 跑 `run_pipeline.py`，驗證流程走到「產出 transcript.json」且無拋錯（轉錄結果可為空但結構合法）。

- [ ] **Step 3: 寫 README**

記錄：環境安裝、四步用法、第二步「人機檢查點」說明（Claude 讀 `transcript.json` → 產 `slides.json` → 跑自檢 → 渲染）、`slides.json`/`transcript.json` 格式、字體與裁剪規則。

- [ ] **Step 4: Commit**

```bash
git add python/run_pipeline.py README.md
git commit -m "docs: pipeline orchestrator and usage"
```

---

## 執行順序與相依

- Task 1（地基）→ Task 2（schema）→ Task 3（trim）→ Task 4（transcribe）為 Python 主鏈。
- Task 5（timeline）→ Task 6（元件）→ Task 7（組合）→ Task 8（渲染）為 Remotion 主鏈，可與 Python 主鏈平行；二者只在 Task 7/8 需要 `slides.json` fixture 時才共用資料格式（由 Task 2 的 schema 定義）。
- Task 9（orchestrator）最後，串起 Python 端。

## 第二步（Claude 文案策劃）人機檢查點

不在上述程式任務內，屬執行階段的離線步驟：Claude 讀 `transcript.json` → 產出合規 `slides.json`（經 Task 2 的 `parse_slides` 驗證）→ 交付渲染。此步不接 API，由本次對話的 Claude 完成。
