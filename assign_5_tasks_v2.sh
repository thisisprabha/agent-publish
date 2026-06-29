#!/bin/bash
set -e

REPO=/Users/yoyoboy/agent-publish
BASE_DIR=/tmp/cc-batch2

rm -rf "$BASE_DIR"
mkdir -p "$BASE_DIR"

declare -A TASKS=(
  ["AP-042"]="Add footnotes support in REPO. Detect markdown footnotes syntax [^1] [^note] etc, render as styled footnotes section at bottom of article with inline superscript refs and back-links. Use a post-processing step in converter pipeline. Add tests. REPO=/Users/yoyoboy/agent-publish"
  ["AP-043"]="Enhance TOC in REPO. Add section numbering (1. 1.1 1.1.1), make nested items collapsible with details disclosure, add scroll-spy highlighting of active section. Follow existing TOC patterns in converter.py and cli.py. Do not delete unrelated code. REPO=/Users/yoyoboy/agent-publish"
  ["AP-044"]="Implement smart typography post-processing in REPO. Convert -- to em-dash, 'single quotes' to smart quotes, \"double quotes\" to smart quotes, ... to ellipsis. Add as a post-processing step in converter pipeline, controlled by --humanize flag or new --smart-typography flag. Follow existing post-processing hook pattern. Do not delete unrelated code. REPO=/Users/yoyoboy/agent-publish"
  ["AP-045"]="Add reading progress bar in REPO. Show a thin sticky bar at top of page tracking scroll progress through article. Use CSS-only progress or minimal JS injection. Wire via --progress flag or config. Follow existing converter hooks. Do not delete unrelated code. REPO=/Users/yoyoboy/agent-publish"
  ["AP-046"]="Add code quality checks in REPO. After processing code blocks, optionally run ruff check on extracted code and emit warnings in code_report.json. Controlled by --lint-code flag. Follow existing CLI patterns. Do not delete unrelated code. REPO=/Users/yoyoboy/agent-publish"
)

for TASK_ID in AP-042 AP-043 AP-044 AP-045 AP-046; do
  TASKDIR="$BASE_DIR/$TASK_ID"
  rm -rf "$TASKDIR"
  git clone --depth 1 "$REPO" "$TASKDIR" >/dev/null 2>&1
  PROMPT="${TASKS[$TASK_ID]}"
  echo "[$TASK_ID] Starting..."
  set +e
  (cd "$TASKDIR" && command-code -p "$PROMPT" --model deepseek/deepseek-v4-pro --yolo --max-turns 20 2>&1 | tail -n 3; echo "EXIT:$?" > /tmp/${TASK_ID}.exit)
  EXIT=$?
  set -e
  if [ $EXIT -eq 0 ] || [ $EXIT -eq 8 ]; then
    echo "[$TASK_ID] command done (code $EXIT)"
  else
    echo "[$TASK_ID] failed (code $EXIT)"
  fi
done
echo "ALL DONE"