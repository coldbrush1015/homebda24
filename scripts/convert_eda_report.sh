#!/usr/bin/env bash
set -euo pipefail

# Simple helper to convert diamond/eda_report.md -> diamond/eda_report.docx using pandoc
SRC="diamond/eda_report.md"
OUT="diamond/eda_report.docx"

if [ ! -f "$SRC" ]; then
  echo "Source file not found: $SRC"
  exit 2
fi

if ! command -v pandoc >/dev/null 2>&1; then
  cat <<'MSG'
pandoc is not installed in this environment.
Install pandoc or run this script on a machine with pandoc available.

Example install (Debian/Ubuntu with root):
  apt-get update && apt-get install -y pandoc

Then run:
  ./scripts/convert_eda_report.sh

MSG
  exit 1
fi

echo "Converting $SRC -> $OUT"
pandoc "$SRC" -o "$OUT"
echo "Done: $OUT"
