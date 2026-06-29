#!/bin/bash
set -e
REPO=/Users/yoyoboy/agent-publish
TASKS=(
  "AP-039:Implement YAML frontmatter schema extensibility in $REPO. The user can supply a custom .agent_publish_schema.yaml in repo root; if found, merge with built-in schema. Support required fields, type (str/int/date/bool/list), default, one_of enum. Validate on every build. Use existing code patterns; do not delete unrelated code."
  "AP-036:Implement multi-format export plugin in $REPO. Add --format epub,pdf and --to-gh flags. Hook-based architecture: register_exporter(ext, callable). Built-in: markdown passthrough, html default, epub zip-based, pdf weasyprint optional. Follow existing CLI patterns. Do not delete unrelated code."
  "AP-037:Implement image optimization pipeline in $REPO. When --optimize-images is passed, compress JPEG/PNG in-place, convert oversized PNG to WebP, strip EXIF. Zero dependencies: pure Python PIL or skip. Generate images_report.json with before/after sizes. Follow existing CLI patterns. Do not delete unrelated code."
  "AP-040:In $REPO, verify the existing fix for CLI --template crash. The task description says use args.template_override and add regression test. Inspect current code, ensure the fix is present and no regressions exist. If broken, fix it. Add regression test if missing. Do not delete unrelated code."
  "AP-041:In $REPO, verify the DESIGN.md theme system upgrade: 4 bug fixes (h2 left-bar, table WebKit, dark mode stepping, conditional Pygments CSS), serif display H1, 9-section DESIGN.md schema, and the new editorial theme (warm off-white, sienna accent, serif headlines). Inspect current implementation, add missing tests if any. Do not delete unrelated code."
)

: > /tmp/cc-results.log
for TASK in "${TASKS[@]}"; do
  ID="${TASK%%:*}"
  PROMPT="${TASK#*:}"
  TMPDIR="/tmp/agent-publish-${ID}"
  rm -rf "$TMPDIR"
  git clone "$REPO" "$TMPDIR" >/dev/null 2>&1
  cd "$TMPDIR"
  echo ">>> Running command-code for $ID"
  set +e
  command-code -p "$PROMPT" --model deepseek/deepseek-v4-pro --yolo --skip-onboarding --max-turns 20
  EXIT=$?
  set -e
  echo ">>> $ID exit code: $EXIT"
  if [ $EXIT -eq 0 ]; then
    echo "$ID: SUCCESS" >> /tmp/cc-results.log
  else
    echo "$ID: FAILED ($EXIT)" >> /tmp/cc-results.log
  fi
done
