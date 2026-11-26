#!/usr/bin/env bash
# 最終渲染：輸出 <repo>/output/${DATE}-${THEME}.mp4
# 用法：DATE=2026-11-26 THEME=主題 ./scripts/render.sh
set -euo pipefail

cd "$(dirname "$0")/.."  # remotion/

DATE="${DATE:-$(date +%Y-%m-%d)}"
THEME="${THEME:-影片}"
OUT="../output/${DATE}-${THEME}.mp4"

mkdir -p ../output

npx remotion render src/index.ts Main "$OUT"

echo "rendered $OUT"
