#!/usr/bin/env bash
# new-biome.sh — cut a biome generation from the living source (leg 3).
#
# Cuts a FROZEN pre-run snapshot to CORSAIR (leg 2) and a RUNNABLE experiment to
# the desktop (leg 1), both from the git-tracked source, in one move. We only
# ever edit the source and run the desktop experiment; the CORSAIR snapshot stays
# frozen — the pristine still-frame of the moment this generation formed. The
# diff between leg 1 (mutated by running) and leg 2 (frozen) is what the run did.
#
#   usage: ./new-biome.sh v001 "hypothesis text"
set -euo pipefail
export COPYFILE_DISABLE=1   # macOS: don't write ._* AppleDouble sidecars to exFAT (CORSAIR)

VER="${1:?usage: new-biome.sh <vNNN> <hypothesis>}"
HYP="${2:?usage: new-biome.sh <vNNN> <hypothesis>}"

SRC="$(cd "$(dirname "$0")/.." && pwd)"              # src/
REPO="$(cd "$SRC/.." && pwd)"                         # repo root
RUN_ROOT="$HOME/Desktop/biome-runs"
SNAP_ROOT="/Volumes/CORSAIR/biome/biome-runs"
COMMIT="$(git -C "$REPO" rev-parse --short HEAD 2>/dev/null || echo uncommitted)"
CREATED="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

cut_to() {
  local dest="$1"
  mkdir -p "$dest"
  rsync -a --exclude '__pycache__' --exclude '*.pyc' "$SRC/spark" "$dest/"
  rsync -a --exclude '__pycache__' --exclude '*.pyc' "$SRC/biome" "$dest/"
  printf 'web: python3 biome/serve.py\n' > "$dest/Procfile"   # platform hosts read this; bare hosts ignore it
  printf '# stdlib only — Python marker for platform builds\n' > "$dest/requirements.txt"
  printf '3.12\n' > "$dest/.python-version"
  cat > "$dest/MANIFEST.md" <<EOF
# biome $VER

- created: $CREATED
- source commit: $COMMIT
- hypothesis: $HYP
- legs: experiment=$RUN_ROOT/$VER  snapshot=$SNAP_ROOT/$VER  source=$REPO@$COMMIT

## Activate (writes blocks/ here; this copy mutates)
    cd "$RUN_ROOT/$VER" && python3 biome/activate.py
EOF
}

if [ -d "/Volumes/CORSAIR" ]; then
  cut_to "$SNAP_ROOT/$VER"
  echo "leg2 frozen snapshot -> $SNAP_ROOT/$VER"
else
  echo "WARN: /Volumes/CORSAIR not mounted — leg2 snapshot skipped"
fi
cut_to "$RUN_ROOT/$VER"
echo "leg1 experiment       -> $RUN_ROOT/$VER"
echo "leg3 source           -> $REPO@$COMMIT  (edit here only)"
