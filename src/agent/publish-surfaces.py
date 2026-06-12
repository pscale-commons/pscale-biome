"""publish-surfaces — the collective joins the perceptual fabric.

Each agent already publishes a `surface` block for its peers (the local
'between'). This bridge lays those same surfaces on a commons door as
surface-mobius-a / -b / -c, so anything that reads the commons — keel, the
mind, a visiting Claude, another biome — can perceive the collective, and
the collective's next generation can read the commons back. Sovereignty
holds: only the surface travels, never a private block.

Run:  python3 publish-surfaces.py <run-root> <origin-door>
e.g.  python3 publish-surfaces.py ~/Desktop/mobius-3-runs/v007 https://biome-commons-production.up.railway.app
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "biome"))
sys.path.insert(0, os.path.join(HERE, "..", "spark"))

from store_http import HttpStore


def publish(run_root, origin):
    remote = HttpStore(origin)
    published = []
    for a in ("A", "B", "C"):
        p = os.path.join(run_root, a, "agent", "shell", "surface.json")
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            block = json.load(f)
        name = "surface-mobius-" + a.lower()
        remote.save_block(name, block)
        published.append(name)
    return published


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("usage: publish-surfaces.py <run-root> <origin-door>")
    names = publish(sys.argv[1], sys.argv[2])
    print("published:", ", ".join(names) if names else "(no surfaces found)")
