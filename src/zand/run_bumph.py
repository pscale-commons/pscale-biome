#!/usr/bin/env python3
"""
run_bumph.py — battery of zand calls against bumph.json.

Each test prints:
  - the call signature
  - my prediction (what I think the call should return)
  - the actual result, compactly formatted
The user compares both against their own expectation.

Run: python3 run_bumph.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from zand import zand, floor_depth, canonicalise


def load(name):
    p = os.path.normpath(os.path.join(HERE, "..", "sentinel", f"{name}.json"))
    with open(p) as f:
        return json.load(f)


def trunc(s, n=55):
    if s is None:
        return "None"
    s = str(s)
    return s if len(s) <= n else s[: n - 3] + "..."


def render(r):
    mode = r.get("mode")
    if mode == "whole":
        return f"whole, floor={r['floor']}"
    if mode == "spindle":
        entries = r.get("entries", [])
        parts = [
            f"p{e['pscale']:+d}[{e['status'][:3]}] {trunc(e['text'], 38)}"
            for e in entries
        ]
        return f"spindle addr={r.get('address')!r} len={len(entries)}\n      " + \
               "\n      ".join(parts)
    if mode == "point":
        return f"point p{r['pscale']:+d} [{r['status']}] {trunc(r['text'], 60)}"
    if mode == "ring":
        sibs = r.get("siblings", [])
        parts = [
            f"  {s['digit']}{' *' if s['is_walked'] else '  '} "
            f"[{s['status'][:3]}{'B' if s['is_branch'] else 'L'}] "
            f"{trunc(s['text'], 50)}"
            for s in sibs
        ]
        return f"ring p{r['pscale']:+d} ({len(sibs)} siblings)\n" + \
               "\n".join(parts)
    if mode == "directory":
        sub = r.get("subtree")
        if isinstance(sub, dict):
            return f"directory subtree=\n      " + \
                   json.dumps(sub, indent=2).replace("\n", "\n      ")
        return f"directory subtree={trunc(json.dumps(sub), 80)}"
    if mode == "disc":
        nodes = r.get("nodes", [])
        parts = [
            f"  {n['address']!r:8} [{n['status'][:3]}] {trunc(n['text'], 50)}"
            for n in nodes
        ]
        return f"disc p{r['pscale']:+d} ({len(nodes)} positions)\n" + \
               "\n".join(parts)
    return repr(r)


def show(call_label, prediction, actual):
    print(f"\n--- {call_label}")
    print(f"  predict:  {prediction}")
    print(f"  actual:   {render(actual)}")


bumph = load("bumph")
print("=" * 70)
print(f"bumph.json — floor = {floor_depth(bumph)}")
print("=" * 70)

# --------------------------------------------------------------------------
print("\n############ A: WHOLE BLOCK ############")

show("zand(bumph)",
     "whole, floor=3",
     zand(bumph))

# --------------------------------------------------------------------------
print("\n############ B: SPINDLES (number only; varying lengths) ############")

show("zand(bumph, '2')",
     "bare '2' on floor 3 pads to walk 0,0,2 (depth 3); "
     "4 entries; last = 'second at p0 (leaf)'",
     zand(bumph, "2"))

show("zand(bumph, '32.4')",
     "dotted '32.4' on floor 3 pads to walk 0,3,2,4 (depth 4); "
     "5 entries; pscales 3,2,1,0,-1; last = 'fourth at p-1 under 32,'",
     zand(bumph, "32.4"))

show("zand(bumph, '32.61')",
     "dotted '32.61' on floor 3 pads to walk 0,3,2,6,1 (depth 5); "
     "6 entries; last = 'first at p-2 under 326,'",
     zand(bumph, "32.61"))

show("zand(bumph, '6')",
     "bare '6' on floor 3 pads to walk 0,0,6 (depth 3); "
     "4 entries; last is HEADLESS (root[0][0][6] has no 0-voicing)",
     zand(bumph, "6"))

show("zand(bumph, '6.1')",
     "dotted '6.1' on floor 3 pads to walk 0,0,6,1 (depth 4); "
     "entry 3 is HEADLESS, entry 4 = 'first at p-1 under headless 6,'",
     zand(bumph, "6.1"))

show("zand(bumph, '9')",
     "bare '9' on floor 3 pads to walk 0,0,9 (depth 3); "
     "root[0][0][9] does not exist; entry 3 = ABSENT",
     zand(bumph, "9"))

# --------------------------------------------------------------------------
print("\n############ C: DISCS (no number; varying attention) ############")

show("zand(bumph, attention=0)",
     "all positions at depth 3 (at floor); under root[0][0]: 0,2,5,6,8; "
     "under root[0][3]: 0,9; total 7 entries (5 are root[0][0]'s, 2 are root[0][3]'s)",
     zand(bumph, attention=0))

show("zand(bumph, attention=-1)",
     "all positions at depth 4 (p-1); root[0][0][5][1,7]; root[0][0][6][1]; "
     "root[0][3][2][0,4,6]; total ~6",
     zand(bumph, attention=-1))

show("zand(bumph, attention=-2)",
     "all positions at depth 5 (p-2); root[0][3][2][6][0,1] only; 2 entries",
     zand(bumph, attention=-2))

show("zand(bumph, attention=1)",
     "all positions at depth 2 (p1); root[0]'s digit children: 0,3,6,7; 4 entries",
     zand(bumph, attention=1))

show("zand(bumph, attention=2)",
     "all positions at depth 1 (p2); just root[0]; 1 entry",
     zand(bumph, attention=2))

show("zand(bumph, attention=3)",
     "all positions at depth 0 (p3); just root itself; 1 entry, address ''",
     zand(bumph, attention=3))

# --------------------------------------------------------------------------
print("\n############ D: SPINDLE + ATTENTION (specific shapes) ############")

show("zand(bumph, '32.4', attention=-1)  # point at terminus",
     "point at p-1, text='fourth at p-1 under 32,', status=voiced",
     zand(bumph, "32.4", attention=-1))

show("zand(bumph, '32.4', attention=0)  # ring one shallower",
     "ring at p0; parent=root[0][3][2]; siblings 0,4,6; '2' is walked... "
     "WAIT: parent at depth 2 is root[0][3]; walked='2' at depth 3",
     zand(bumph, "32.4", attention=0))

show("zand(bumph, '32.4', attention=1)  # ring two shallower",
     "ring at p1; parent=root[0]; siblings 0,3,6,7; walked='3' at depth 2",
     zand(bumph, "32.4", attention=1))

show("zand(bumph, '32.4', attention=2)  # ring three shallower",
     "ring at p2; parent=root; siblings just '0'; walked='0' at depth 1",
     zand(bumph, "32.4", attention=2))

show("zand(bumph, '5', attention=-1)  # directory one deeper",
     "bare '5' pads to walk 0,0,5; terminus=root[0][0][5] (branch); "
     "directory shows its subtree one level: 0,1,7",
     zand(bumph, "5", attention=-1))

show("zand(bumph, '5', attention=-2)  # directory two deeper (children are leaves)",
     "same subtree as above; nothing deeper to descend",
     zand(bumph, "5", attention=-2))

show("zand(bumph, '3', attention=-2)  # directory at absent position",
     "bare '3' pads to walk 0,0,3; root[0][0][3] is ABSENT; "
     "directory returns subtree=None, status=absent",
     zand(bumph, "3", attention=-2))

show("zand(bumph, '32', attention=-1)  # spindle to branch + directory below",
     "bare '32' pads to walk 0,3,2; terminus=root[0][3][2] (branch); "
     "directory shows subtree to depth 4: 0,4,6 (where 6 is a subbranch)",
     zand(bumph, "32", attention=-1))

show("zand(bumph, '32', attention=-2)  # same, descend deeper",
     "directory descends two levels from root[0][3][2]; "
     "now the [6] sub-branch's children also show",
     zand(bumph, "32", attention=-2))
