#!/usr/bin/env bash
# Copy the generated Gobber floorplan into the read-only project folder.
# Run this from a shell that has write access to /home/abdallahmohamedabdallah277/Gobber-.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/floorplan"
DEST_ROOT="${1:-/home/abdallahmohamedabdallah277/Gobber-}"
DEST="$DEST_ROOT/floorplan"

if [ ! -f "$SRC/index.html" ]; then
  echo "No map at $SRC/index.html" >&2
  exit 1
fi

mkdir -p "$DEST"
cp -a "$SRC/." "$DEST/"

echo "Copied the Gobber floorplan to $DEST"
echo "Open: $DEST/index.html"
