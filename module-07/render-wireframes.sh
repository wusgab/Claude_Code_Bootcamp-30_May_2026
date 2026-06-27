#!/usr/bin/env bash
# Render wireframe sources to PNG.
# Run from exercises/part-07/.
#
# Outputs:
#   wireframe.png         (from wireframe.mmd via mermaid-cli)
#   wireframe-sketch.png  (from wireframe-sketch.svg via resvg-js)

set -euo pipefail

cd "$(dirname "$0")"

echo "==> Rendering wireframe.mmd → wireframe.png (1280x720)"
npx -y @mermaid-js/mermaid-cli -i wireframe.mmd -o wireframe.png -w 1280 -H 720

echo "==> Rendering wireframe-sketch.svg → wireframe-sketch.png (1280x720)"
# rsvg-convert (from librsvg) preserves the 1280x720 aspect ratio cleanly.
if command -v rsvg-convert >/dev/null 2>&1; then
  rsvg-convert -w 1280 -h 720 wireframe-sketch.svg -o wireframe-sketch.png
else
  echo "  rsvg-convert not found. Install librsvg: 'brew install librsvg' (macOS)"
  echo "  or 'apt-get install librsvg2-bin' (Debian/Ubuntu), then re-run."
  exit 1
fi

echo "==> Done."
ls -la wireframe.png wireframe-sketch.png
