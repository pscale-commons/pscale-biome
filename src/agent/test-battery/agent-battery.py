"""agent-battery — regression battery for the spark-speaking mobius-3 kernel.

Run:  python3 agent-battery.py     (exits nonzero on any failure)

Covers the address formatter, frontier gap-finding (Stage 1, structural),
result unwrapping across every spark shape, the teaching skeleton, scoop
hydration with cross-block star resolution, the reflexive bundle, window
composition on the default recipe, the flatten guard, and peer sovereignty.
The LLM stages are left to live pulses.
"""

import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, "..", "..", "spark"))

import kernel
import spark

P = F = 0


def ok(label, got, exp):
    global P, F
    if got == exp:
        P += 1
        print("  pass", label)
    else:
        F += 1
        print("  FAIL", label, "\n    got", got, "\n    exp", exp)


print("address formatting")
ok("at the floor", kernel._format_address(["1"], 1), "1")
ok("below the floor", kernel._format_address(["1", "2"], 1), "1.2")
ok("two below", kernel._format_address(["1", "2", "3"], 1), "1.23")

print("frontier (Stage 1, structural)")
PI = {"0": "purpose", "1": {"0": "build the door", "1": "hinge fitted"},
      "2": "vision:9", "3": {"0": "tend the world"}}
RHO = {"0": "conditions", "1": {"0": "the door exists"}}
cells = kernel.frontier_candidates(PI, RHO)
kinds = [(c["type"], c["address"]) for c in cells]
ok("compare where both carry", ("compare", "purpose:1") in kinds, True)
ok("missing where rho stops", ("missing", "purpose:3") in kinds, True)
ok("a reference anchor is not a cell", any("purpose:2" in a for _, a in kinds), False)
ok("descent past the compare", ("missing", "purpose:1.1") in kinds, True)

print("unwrapping every spark shape")
B = {"0": "r", "1": {"0": "A", "2": "A2"}}
ok("point", kernel._nest(spark.spark(B, "1", 0)), "A")
ok("directory", kernel._nest(spark.spark(B, "1", -1)), {"0": "A", "2": "A2"})
ok("ring", kernel._nest(spark.spark(B, "1.2", 0)), {"1": "A"})
ok("disc keeps 0-positions first-class", kernel._nest(spark.spark(B, None, -1)),
   {"10": "A", "12": "A2"})
ok("spindle", kernel._nest(spark.spark(B, "1.2", None)), ["A", "A2"])
ok("whole", kernel._nest(spark.spark(B)), B)

print("teaching skeleton + scoop")
slate = spark.load(os.path.join(HERE, "..", "..", "spark", "slate.json"))
sk = kernel._skeleton(slate)
ok("skeleton keeps the voicings", sk["0"].startswith("Slate"), True)
ok("skeleton is one level deep", all(isinstance(v, str) for v in sk.values()), True)

kernel._cache.clear()
kernel._cache["slate"] = slate
kernel._cache["vision"] = {"0": "vision", "9": {"0": "the long view", "1": "a forest"}}
kernel._cache["pointer"] = {"0": "p", "1": "vision:9:-1"}
ok("a constant teaching scoops to skeleton", kernel.scoop("slate")["0"].startswith("Slate"), True)
ok("a dilated address scoops unwrapped", kernel.scoop("vision:9:-1"),
   {"0": "the long view", "1": "a forest"})
ok("star resolves across blocks through the loader",
   kernel.scoop("pointer:1:0"), {"0": "the long view", "1": "a forest"})

print("the bundle and the window")
kernel._cache["reflexive"] = {"0": "refl", "2": {"0": "field", "1": "the anchors"},
                              "9": {"0": "bundle", "1": "slate", "4": "purpose"}}
kernel._cache["purpose"] = PI
kernel._cache["conditions"] = RHO
ok("the bundle re-dials, zero excluded", kernel.read_reflexive_current(),
   {"1": "slate", "4": "purpose"})
gamma = kernel.run_F(use_llm=False)
ok("F without an LLM keeps structural gaps only",
   all(g["type"] == "missing" for g in gamma) and len(gamma) == 2, True)
system, message, bundle = kernel.compose_window(gamma)
ok("the window carries the hydrated self", '"slate"' in system and "Slate" in system, True)
ok("the given side carries the gap", "purpose:3" in message, True)

print("writes: the guard and the fold")
tmp = tempfile.mkdtemp(prefix="battery-agent-")
kernel.SHELL_DIR = tmp
kernel._cache.clear()
try:
    kernel.apply_write("surface", "1", "what I am working on")
    saved = json.load(open(os.path.join(tmp, "surface.json")))
    ok("a point write folds and persists", saved["1"], "what I am working on")
    kernel._cache.clear()
    kernel._cache["surface"] = {"0": "s", "1": {"0": "head", "2": "kept"}}
    try:
        kernel.apply_write("surface", "1", "flattening string")
        ok("the flatten guard holds", "no error", "refused")
    except ValueError as e:
        ok("the flatten guard holds", "refusing to flatten" in str(e), True)
    kernel.load_peers = lambda: {"B": "/elsewhere"}
    status, applied, failed = kernel.route({"writes": {"B:1": "trespass", "surface:3": "mine to write"}})
    ok("a peer's block is read-only", failed[0]["address"], "B:1")
    ok("own blocks still fold", applied, 1)
    kernel._cache["conditions"] = {"0": "conditions"}
    kernel.report_failures([{"address": "surface:1", "error": "refusing to flatten"}])
    ok("refused writes become perceived conditions",
       kernel.load_block("conditions")["9"].startswith("kernel report"), True)
    kernel.report_failures([])
    ok("a clean fold clears the report", "9" in kernel.load_block("conditions"), False)
finally:
    shutil.rmtree(tmp)

print()
print("TOTAL: %d passed, %d failed" % (P, F))
sys.exit(1 if F else 0)
