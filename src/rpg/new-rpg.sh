#!/usr/bin/env bash
# new-rpg.sh — cut a generation of the RPG bench: a frozen SNAPSHOT on CORSAIR and
# a working EXPERIMENT copy on the Desktop, from the git source. Mirrors
# new-collective.sh. Edit source only; run the Desktop copy; the snapshot stays frozen.
#
#   ./new-rpg.sh "hypothesis for this run"
set -euo pipefail
export COPYFILE_DISABLE=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_RPG="$SCRIPT_DIR"
SRC_SPARK="$(cd "$SCRIPT_DIR/../spark" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
ARCHIVE_ROOT="${ARCHIVE_ROOT:-/Volumes/CORSAIR/biome/rpg-runs}"
WORKING_ROOT="${WORKING_ROOT:-$HOME/Desktop/rpg-runs}"
HYPO="${1:-"(no hypothesis given)"}"

case "$ARCHIVE_ROOT" in
  /Volumes/*)
    VOL="/Volumes/$(printf '%s' "$ARCHIVE_ROOT" | cut -d/ -f3)"
    mount | grep -q "on ${VOL} " || { echo "archive volume not mounted: ${VOL}" >&2; exit 1; } ;;
esac
mkdir -p "$ARCHIVE_ROOT" "$WORKING_ROOT"

next=1
for d in "$ARCHIVE_ROOT"/v??? "$WORKING_ROOT"/v???; do
  [ -d "$d" ] || continue
  n="$(basename "$d")"; n="${n#v}"; n="$((10#$n))"
  (( n >= next )) && next="$((n + 1))"
done
V="$(printf 'v%03d' "$next")"
ARCH="$ARCHIVE_ROOT/$V"; WORK="$WORKING_ROOT/$V"
{ [ -e "$ARCH" ] || [ -e "$WORK" ]; } && { echo "$V already exists" >&2; exit 1; }

STAGE="$(mktemp -d)"; trap 'rm -rf "$STAGE"' EXIT
PKG="$STAGE/$V"
mkdir -p "$PKG/spark"

# the bench source
cp "$SRC_RPG"/frame.py "$SRC_RPG"/tiers.py "$SRC_RPG"/play.py "$SRC_RPG"/rpg-battery.py "$SRC_RPG"/README.md "$PKG/"
cp -R "$SRC_RPG"/world "$SRC_RPG"/characters "$PKG/"
# spark rides along so the cut is self-contained (frame.py finds ./spark/spark.py)
cp "$SRC_SPARK"/spark.py "$SRC_SPARK"/slate.json "$SRC_SPARK"/flint.json "$PKG/spark/"

GIT_COMMIT="$(git -C "$PROJECT_DIR" rev-parse --short HEAD 2>/dev/null || echo uncommitted)"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

cat > "$PKG/MANIFEST.md" <<EOF
# RPG bench $V

- created: $TS
- source commit: $GIT_COMMIT
- hypothesis: $HYPO

The experiment leg of the RPG three-leg rig. Character-LLMs play turns against a
persisted world + shells; the play grows \`scenes.json\` and the characters'
\`conditions\`/\`history\`. Runs diverge from source — never fold back.

## Conformance (no key, no cost)
    python3 rpg-battery.py

## Play
    RPG_TURNS=2 python3 play.py .
    cat scenes.json characters/*/conditions.json   # what the play grew

Tiers map to model size in tiers.py; RPG_HARD=claude-sonnet-4-6 runs it cheaply.
Key at ~/.config/mobius/anthropic-key.
EOF

cp -R "$PKG" "$ARCH"
cp -R "$PKG" "$WORK"
chmod -R a-w "$ARCH" 2>/dev/null || true

echo "RPG bench $V created"
echo "  snapshot (frozen):  $ARCH"
echo "  experiment (run):   $WORK"
echo
echo "play:  cd \"$WORK\" && RPG_TURNS=2 python3 play.py ."
