"""resense-battery — regression battery for the re-sense pulse.

Run:  python3 resense-battery.py     (exits nonzero on any failure)

Re-sense: a becoming's kin lines update when the landscape changes and
hold steady when it does not; the intention voicing survives the rewrite.
(Split from the old courier-battery when the courier form was retracted —
resense.py stays live; serve.py runs it as a slow daemon.)
"""

import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, "..", "..", "spark"))

import resense as resense_mod

P = F = 0


def ok(label, got, exp):
    global P, F
    if got == exp:
        P += 1
        print("  pass", label)
    else:
        F += 1
        print("  FAIL", label, "\n    got", got, "\n    exp", exp)


print("the re-sense pulse")
land = tempfile.mkdtemp(prefix="battery-resense-")
me = os.path.join(land, "me")
os.makedirs(os.path.join(me, "blocks"))
biome0 = {"0": "becoming", "1": "x · genome v5",
          "9": {"0": "intention: commons [8.83] — a surface to serve"}}
with open(os.path.join(me, "blocks", "biome.json"), "w") as f:
    json.dump(biome0, f)
try:
    changed, lines = resense_mod.resense(me, network=False)
    # the scan roams real ledges too; hold the check to the synthetic land
    kin_here = [l for l in lines if land in l]
    ok("first re-sense records the empty land", kin_here, [])
    neighbour = os.path.join(land, "v900")
    os.makedirs(os.path.join(neighbour, "blocks"))
    with open(os.path.join(neighbour, "blocks", "biome.json"), "w") as f:
        json.dump({"0": "biome — kin", "1": "py · genome v5"}, f)
    changed, lines = resense_mod.resense(me, network=False)
    ok("a new kin changes the becoming", changed, True)
    b = json.load(open(os.path.join(me, "blocks", "biome.json")))
    ok("the intention voicing survives the rewrite",
       b["9"]["0"].startswith("intention: commons"), True)
    ok("the re-sense note is stamped", "re-sensed" in b["9"]["0"], True)
    ok("the kin line lands in a digit",
       any("v900" in str(v) for k, v in b["9"].items() if k != "0"), True)
finally:
    shutil.rmtree(land)

print()
print("TOTAL: %d passed, %d failed" % (P, F))
sys.exit(1 if F else 0)
