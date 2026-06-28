#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-$ROOT/backups}"
mkdir -p "$BACKUP_DIR"
STAMP="$(date +%Y%m%d_%H%M%S)"
if [ -f "$ROOT/life_ai.db" ]; then
  cp "$ROOT/life_ai.db" "$BACKUP_DIR/life_ai_${STAMP}.db"
fi
if [ -d "$ROOT/data" ]; then
  tar -czf "$BACKUP_DIR/data_${STAMP}.tar.gz" -C "$ROOT" data
fi
echo "Backup saved to $BACKUP_DIR"
