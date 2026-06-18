"""resonance-battery — regression battery for the floor-aligned resonance read.

Run:  python3 resonance-battery.py     (exits nonzero on any failure)

Covers the arithmetic of resonance.py over synthetic floor-1 triads: structural
resonance (shape co-occupation via spark.fold), the content-overlap token proxy,
pairwise structural, the splay/collapse/drift verdict, the pscale band, and
read-only triad loading. The optional LLM judge is left to a live read.
"""

import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, "..", "..", "spark"))

import resonance  # noqa: E402

P = F = 0


def ok(label, got, exp):
    global P, F
    if got == exp:
        P += 1
        print("  pass", label)
    else:
        F += 1
        print("  FAIL", label, "\n    got", got, "\n    exp", exp)


def check(label, cond):
    ok(label, bool(cond), True)


# Floor-1 blocks: root "0" is a string (floor 1); branches 1,2 sit at pscale 0.
def blk(root, one, two=None):
    b = {"0": root, "1": one}
    if two is not None:
        b["2"] = two
    return b


print("structural resonance — identical triad (collapse: unison)")
same = blk("hold the standing intent", "build the world", "settle the rules")
triad = {"A": dict(same), "B": dict(same), "C": dict(same)}
r0 = resonance.read_pscale(triad, 0)
ok("identical: structural 1.0", r0["structural"], 1.0)
ok("identical: content 1.0", r0["content"], 1.0)
ok("identical: pairwise all 1.0", set(r0["pairwise_structural"].values()), {1.0})
ok("identical: 3 co-occupied of 3", (r0["co_occupied"], r0["union"]), (3, 3))

print("\nstructural resonance — one block missing a branch (shape diverges)")
shape = {"A": blk("r", "x", "y"), "B": blk("r", "x"), "C": blk("r", "x", "y")}
rs = resonance.read_pscale(shape, 0)
ok("shape-divergent: structural 2/3", round(rs["structural"], 3), round(2 / 3, 3))
check("shape-divergent: B shares less than A·C", rs["pairwise_structural"]["AC"]
      > rs["pairwise_structural"]["AB"])

print("\ncontent overlap — same shape, distinct voice (splay)")
splay = {"A": blk("root", "alpha beta gamma", "delta epsilon"),
         "B": blk("root", "omega psitwo chitwo", "sigma tautwo"),
         "C": blk("root", "oneone twotwo threee", "fourfour fivee")}
rp = resonance.read_pscale(splay, 0)
ok("splay: structural 1.0 (shared shape)", rp["structural"], 1.0)
check("splay: content overlap is low (< 0.5)", rp["content"] < 0.5)
check("splay: divergence cells recorded", len(rp["diverging"]) >= 1)

print("\nverdict — the three regimes")
ok("identical triad -> collapse",
   resonance.verdict(1.0, 1.0, {"AB": 1.0, "AC": 1.0, "BC": 1.0})[0], "collapse")
ok("shared shape, distinct content -> splay",
   resonance.verdict(0.9, 0.2, {"AB": 0.9, "AC": 0.9, "BC": 0.9})[0], "splay")
ok("no shared shape -> drift",
   resonance.verdict(0.2, None, {"AB": 0.2})[0], "drift")

print("\npscale band + token proxy")
deep = blk("r", {"0": "head", "1": "below the floor"})
ok("band: floor-1 with depth-2 content reads pscale 0 and -1",
   resonance.pscale_band([deep, blk("r", "x")]), [0, -1])
ok("token jaccard: identical sets = 1.0",
   resonance._jaccard(resonance._tokens("build the world"),
                      resonance._tokens("build the world")), 1.0)
ok("token jaccard: disjoint = 0.0",
   resonance._jaccard(resonance._tokens("alpha beta"),
                      resonance._tokens("gamma delta")), 0.0)

print("\nload_triad — read-only from a run-root")
tmp = tempfile.mkdtemp()
try:
    for a in ("A", "B", "C"):
        d = os.path.join(tmp, a, "agent", "shell")
        os.makedirs(d)
        with open(os.path.join(d, "purpose.json"), "w") as f:
            json.dump(same, f)
    loaded = resonance.load_triad(tmp, "purpose")
    ok("load_triad: finds all three", sorted(loaded), ["A", "B", "C"])
    check("load_triad: returns the blocks", loaded["A"]["1"] == "build the world")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n%d ok, %d failed" % (P, F))
sys.exit(1 if F else 0)
