#!/bin/sh
set -e

if [ -z "$DATABASE_URL" ]; then
  echo "DATABASE_URL is not set."
  exit 1
fi

BACKUP_DIR="${BACKUP_DIR:-backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILE="$BACKUP_DIR/memorial_$TIMESTAMP.sql"

mkdir -p "$BACKUP_DIR"

pg_dump "$DATABASE_URL" > "$FILE"

echo "Backup written to $FILE"
