#!/usr/bin/env bash
# new-experiment.sh — snapshot the pristine agent SOURCE into an enumerated,
# self-contained experiment package: a frozen ARCHIVE clone (immutable) and a
# runnable WORKING clone. The project source is never run-mutated; each run is
# an experiment with a frozen start state and its own filmstrip.
#
#   Source  (pristine, git)  : src/agent/  + src/spark/{spark.py,slate,flint}
#   Archive (frozen, CORSAIR): $ARCHIVE_ROOT/vNNN   — read-only, never run
#   Working (mutating, Desk) : $WORKING_ROOT/vNNN   — runs; shell + filmstrip change
#
# Usage:   ./new-experiment.sh "one-line hypothesis for this run"
# Override roots via env: ARCHIVE_ROOT=... WORKING_ROOT=...
set -euo pipefail
export COPYFILE_DISABLE=1            # no macOS ._ AppleDouble files (esp. on exfat)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"        # .../src/agent
SRC_AGENT="$SCRIPT_DIR"
SRC_SPARK="$(cd "$SCRIPT_DIR/../spark" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

ARCHIVE_ROOT="${ARCHIVE_ROOT:-/Volumes/CORSAIR/mobius/mobius-3-runs}"
WORKING_ROOT="${WORKING_ROOT:-$HOME/Desktop/mobius-3-runs}"
HYPO="${1:-"(no hypothesis given)"}"

# --- preflight: the archive drive must really be mounted (don't shadow /Volumes) ---
case "$ARCHIVE_ROOT" in
  /Volumes/*)
    VOL="/Volumes/$(printf '%s' "$ARCHIVE_ROOT" | cut -d/ -f3)"
    if ! mount | grep -q "on ${VOL} "; then
      echo "archive volume not mounted: ${VOL}  (mount it, or set ARCHIVE_ROOT=...)" >&2
      exit 1
    fi ;;
esac
mkdir -p "$ARCHIVE_ROOT" "$WORKING_ROOT"

# --- next enumerated version across both roots ---
next=1
for d in "$ARCHIVE_ROOT"/v??? "$WORKING_ROOT"/v???; do
  [ -d "$d" ] || continue
  n="$(basename "$d")"; n="${n#v}"; n="$((10#$n))"
  (( n >= next )) && next="$((n + 1))"
done
V="$(printf 'v%03d' "$next")"
ARCH="$ARCHIVE_ROOT/$V"; WORK="$WORKING_ROOT/$V"
{ [ -e "$ARCH" ] || [ -e "$WORK" ]; } && { echo "$V already exists" >&2; exit 1; }

# --- assemble the self-contained package in staging ---
STAGE="$(mktemp -d)"; trap 'rm -rf "$STAGE"' EXIT
PKG="$STAGE/$V"
mkdir -p "$PKG/agent/shell" "$PKG/agent/filmstrip" "$PKG/spark"
cp "$SRC_AGENT/kernel.py" "$SRC_AGENT/heartbeat.py" "$SRC_AGENT/digest.py" "$PKG/agent/"
cp "$SRC_AGENT"/shell/*.json "$PKG/agent/shell/"
[ -f "$SRC_AGENT/shell/README.md" ] && cp "$SRC_AGENT/shell/README.md" "$PKG/agent/shell/"
cp "$SRC_SPARK/spark.py" "$SRC_SPARK/slate.json" "$SRC_SPARK/flint.json" "$PKG/spark/"

GIT_COMMIT="$(git -C "$PROJECT_DIR" rev-parse --short HEAD 2>/dev/null || echo uncommitted)"
GIT_STATE="$(git -C "$PROJECT_DIR" diff --quiet 2>/dev/null && echo clean || echo dirty)"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

cat > "$PKG/MANIFEST.md" <<EOF
# Experiment $V

- created: $TS
- source commit: $GIT_COMMIT ($GIT_STATE working tree)
- kernel: Stages 0-3 (F | rest | delta | fold)
- hypothesis: $HYPO

## Layout
- agent/ — kernel + shell. The shell MUTATES during the run; filmstrip/ accumulates.
- spark/ — the engine (spark.py) and the constant teaching (slate, flint), bundled standalone.

## One-time key setup (then every run, every version, just works)
    mkdir -p ~/.config/mobius && echo 'sk-ant-...' > ~/.config/mobius/anthropic-key
    chmod 600 ~/.config/mobius/anthropic-key

## Run (from the WORKING copy) — no key fuss after the one-time setup above
    cd "$WORK/agent"
    python3 kernel.py --compose-only      # inspect the window (no key needed)
    python3 kernel.py                     # one real pulse
    python3 heartbeat.py --max 5          # a self-paced multi-pulse run
    python3 digest.py                     # glance at the run
    # models default in the kernel; override e.g.:  export MOBIUS_MODEL=claude-opus-4-8

## Read the trajectory (working vs frozen seed)
    diff -ru "$ARCH/agent/shell" "$WORK/agent/shell"
EOF

cp -R "$PKG" "$ARCH"
cp -R "$PKG" "$WORK"
chmod -R a-w "$ARCH" 2>/dev/null || true     # freeze the archive

echo "experiment $V created"
echo "  archive (frozen): $ARCH"
echo "  working (run):    $WORK"
echo
echo "inspect first (no token):  cd \"$WORK/agent\" && python3 kernel.py --compose-only"
echo "first real pulse:          cd \"$WORK/agent\" && python3 kernel.py"
