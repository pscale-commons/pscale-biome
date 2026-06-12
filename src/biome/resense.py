"""resense — the becoming stays true: re-run the neighbour sense and record
what changed (shell 8.0: the procedure re-runs to detect condition changes).

A biome's becoming-block records the kin it saw when it unfolded. Kin come
and go — a stick docks, a new biome unfolds nearby, a door goes dark. The
re-sense pulse re-runs the neighbour scan, diffs it against the becoming's
key 9, and rewrites the kin digits when they differ — so inter-biome
evolution is observable, not archaeological. The intention voicing at 9.0
is kept; only the kin lines move.

Run:  python3 resense.py [root]        (anywhere a becoming lives)
The commons runs this on a slow daemon cadence from serve.py.
"""

import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spark"))
sys.path.insert(0, HERE)

import sense
import unfold
from store_fs import FsStore

DIGITS = "123456789"


def resense(root=".", network=True):
    """Re-sense kin; update the becoming if they changed. Returns
    (changed, kin_lines) — changed is False when the world looks the same."""
    store = FsStore(os.path.join(root, "blocks"))
    becoming = store.load_block("biome")
    if becoming is None:
        return False, []                                  # nothing has unfolded here yet
    kin = sense.sense_neighbours(root, network=network)
    lines = [unfold._neighbour_line(n) for n in kin][:9]
    nine = becoming.get("9") if isinstance(becoming.get("9"), dict) else {"0": ""}
    old = [nine[d] for d in DIGITS if d in nine]
    if old == lines:
        return False, lines
    stamp = time.strftime("%Y-%m-%d", time.gmtime())
    voicing = nine.get("0", "intention")
    base = voicing.split(" · re-sensed")[0]               # one note, not an accretion
    fresh = {"0": "%s · re-sensed %s: %d kin (was %d)" % (base, stamp, len(lines), len(old))}
    for i, line in enumerate(lines, start=1):
        fresh[str(i)] = line
    becoming["9"] = fresh
    store.save_block("biome", becoming)
    return True, lines


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    changed, lines = resense(root)
    print("re-sensed: %s (%d kin)" % ("the world changed" if changed else "steady", len(lines)))
    for l in lines:
        print("  -", l)
