#!/usr/bin/env bash
# new-collective.sh — cut a THREE-agent collective (A, B, C), each a full agent
# package, wired as peers: each publishes a `surface` and reads the other two's
# surfaces (the 'between' / Locus 0). The agents share one shell EXCEPT their
# purpose, which is seeded toward a distinct trajectory:
#   A -> RPG · B -> MAGI · C -> open-business (beach / xstream)
# Frozen archive on CORSAIR + working copy on Desktop, same discipline as
# new-experiment.sh.
#
#   ./new-collective.sh "hypothesis"
set -euo pipefail
export COPYFILE_DISABLE=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_AGENT="$SCRIPT_DIR"
SRC_SPARK="$(cd "$SCRIPT_DIR/../spark" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
ARCHIVE_ROOT="${ARCHIVE_ROOT:-/Volumes/CORSAIR/mobius/mobius-3-runs}"
WORKING_ROOT="${WORKING_ROOT:-$HOME/Desktop/mobius-3-runs}"
HYPO="${1:-"(no hypothesis given)"}"
AGENTS=(A B C)

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

for a in "${AGENTS[@]}"; do
  mkdir -p "$PKG/$a/agent/shell" "$PKG/$a/agent/filmstrip" "$PKG/$a/spark"
  cp "$SRC_AGENT/kernel.py" "$SRC_AGENT/heartbeat.py" "$SRC_AGENT/digest.py" "$PKG/$a/agent/"
  cp "$SRC_AGENT"/shell/*.json "$PKG/$a/agent/shell/"
  [ -f "$SRC_AGENT/shell/README.md" ] && cp "$SRC_AGENT/shell/README.md" "$PKG/$a/agent/shell/"
  # differentiate: override purpose branch 2 with this agent's trajectory
  python3 -c "import json; \
p=json.load(open('$PKG/$a/agent/shell/purpose.json')); \
p['2']=json.load(open('$SRC_AGENT/collective/$a.json')); \
f=open('$PKG/$a/agent/shell/purpose.json','w'); json.dump(p,f,indent=2,ensure_ascii=False); f.write(chr(10))"
  cp "$SRC_SPARK/spark.py" "$SRC_SPARK/slate.json" "$SRC_SPARK/flint.json" "$PKG/$a/spark/"
  # peers.json: the other two, pointing at their WORKING agent dirs
  others=(); for b in "${AGENTS[@]}"; do [ "$a" != "$b" ] && others+=("$b"); done
  printf '{\n  "%s": "%s/%s/agent",\n  "%s": "%s/%s/agent"\n}\n' \
    "${others[0]}" "$WORK" "${others[0]}" "${others[1]}" "$WORK" "${others[1]}" \
    > "$PKG/$a/agent/peers.json"
done

GIT_COMMIT="$(git -C "$PROJECT_DIR" rev-parse --short HEAD 2>/dev/null || echo uncommitted)"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

cat > "$PKG/MANIFEST.md" <<EOF
# Collective $V — A · B · C

- created: $TS
- source commit: $GIT_COMMIT
- three peer-wired agents (neutral names); each publishes a \`surface\` block and reads the
  other two's surfaces. They share one shell EXCEPT purpose, seeded toward distinct trajectories:
    - A — RPG (the pscale-block shared-world game)
    - B — MAGI (the agent ecology / coordination)
    - C — open-business (value through the beach via xstream)
- hypothesis: $HYPO

## Run one round (pulse each agent once)
    cd "$WORK" && ./run-round.sh

## Run several rounds (so they perceive each other's updated surfaces)
    cd "$WORK" && for i in 1 2 3 4 5 6; do ./run-round.sh; done

## Read a run
    cd "$WORK"/A/agent && python3 digest.py
    cat "$WORK"/*/agent/shell/surface.json              # the published surfaces
    cat "$WORK"/*/agent/shell/purpose.json | grep -A2 '"2"'   # the divergent purposes
EOF

cat > "$PKG/run-round.sh" <<'EOF'
#!/usr/bin/env bash
# one round of the collective: pulse each agent once
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for a in A B C; do
  echo "=== $a ==="
  ( cd "$HERE/$a/agent" && python3 kernel.py ) || echo "  ($a errored)"
done
EOF
chmod +x "$PKG/run-round.sh"

cp -R "$PKG" "$ARCH"
cp -R "$PKG" "$WORK"
chmod -R a-w "$ARCH" 2>/dev/null || true

echo "collective $V created"
echo "  archive (frozen): $ARCH"
echo "  working (run):    $WORK"
echo
echo "run a round:  cd \"$WORK\" && ./run-round.sh"
