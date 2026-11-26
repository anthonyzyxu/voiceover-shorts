# Changelog

本專案變更記錄遵循 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)，版本號遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

## [0.1.0] - 2026-11-26

### 新增 · Added

- 完整管線：裁剪 → faster-whisper（`large-v3`）轉錄 → AI 文案提煉 → Remotion 渲染出片。
- `transcript.json`／`slides.json` 資料契約與 pydantic schema 驗證。
- 靜音偵測與超長裁剪（VFR 安全的 `trim/atrim`＋`concat`）。
- Remotion 視覺元件：淺色商務背景、進度條、動態文字＋高亮、右上角畫中畫。
- 關鍵幀自檢腳本（`check.py`）與渲染腳本（`render.sh`）。

### 修復 · Fixed

- 多段裁剪的 ffmpeg 表達式錯誤（改用保留區間＋`between` 相加）。
- VFR 素材影音不同步（`setpts=N/FRAME_RATE/TB` → `trim/atrim`＋`concat` 保留時序）。
- 全靜音輸入未報錯（轉錄結果為空時明確拋錯）。

### 文件 · Documentation

- MIT 授權、中英雙語 README、CLAUDE.md、設計文件與實作計畫。
