#!/bin/sh
# walk-the-world — launch a hard-drive biome that serves the real-world map,
# with the human walker at /world. One command; then open the URL in a browser.
#
#   sh src/biome/walk-the-world.sh                  # default run-folder ~/biome-earth, port 3210
#   sh src/biome/walk-the-world.sh ~/my-biome 3300  # custom folder + port
#   BIOME_PEERS=https://<host> sh src/biome/walk-the-world.sh   # walk the wider network too
#
# To map more of the world INTO this running biome (overnight), in another shell:
#   BIOME_EARTH=<run-folder>/blocks python3 src/biome/cartographer.py --root Asia --depth 4

HERE="$(cd "$(dirname "$0")" && pwd)"
RUN="${1:-$HOME/biome-earth}"
PORT="${2:-3210}"
mkdir -p "$RUN/blocks"
cp "$HERE"/world/earth/*.json "$RUN/blocks/" 2>/dev/null

echo "real-world biome  ·  store: $RUN/blocks"
echo "open in a browser:   http://127.0.0.1:$PORT/world"
echo "(raw door: http://127.0.0.1:$PORT/.well-known/biome-beach?block=sol  ·  mcp: /mcp)"
echo
BIOME_ROOT="$RUN" python3 "$HERE/serve.py" "$PORT"
