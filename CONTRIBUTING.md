# 貢獻指南 · Contributing

感謝你有興趣貢獻！請依以下流程進行。

_Thanks for your interest in contributing! Here's how._

## 回報問題 · Reporting Issues

開 Issue 前請先搜尋是否已有人回報。請附上：

- 輸入影片格式（解析度、fps、時長）
- 錯誤訊息與重現步驟
- 環境（作業系統、Python 版本）

## 開發環境 · Development Setup

```bash
cd python
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt pytest

cd ../remotion && npm install
```

## 提交 Pull Request · Submitting a PR

1. 從 `main` 開一個新分支。
2. **先寫失敗測試（TDD），再寫最小實作**讓測試通過。
3. 跑完整測試（見下），確保全綠。
4. 寫清楚的 commit message，提交。
5. 開 PR，說明「改動內容」與「為什麼」。

## 測試 · Tests

```bash
cd python && .venv/bin/python -m pytest ../tests -v
cd remotion && npx vitest run && npx tsc --noEmit
```

## 程式碼風格 · Style

- 遵循現有程式碼的命名與結構。
- Python：加型別標註（type hints）。
- TypeScript：`strict` 模式（tsconfig 已開）。
- **勿提交** `*.mov`／`*.mp4`／`transcript.json`／`slides.json`（皆已 gitignore）。
