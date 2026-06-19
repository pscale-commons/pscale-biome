"""relay-battery — the biome's vapour relay (endpoints 3.4, server-owned).

Run:  python3 relay-battery.py     (exits nonzero on any failure)

Proves the ephemeral channel with no network and a fake clock: presence,
frame-scoping (co-present share vapour; different frames do not), seeing
others-not-self, the staleness horizon (a silent heartbeat evaporates), clean
departure, and the LOAD / saturation signal the unfolder reads to decide
whether to raise another face. Out-of-band by construction — nothing here
touches a store, a block, or the membrane.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import relay as relay_mod

P = F = 0


def ok(label, got, exp):
    global P, F
    if got == exp:
        P += 1
        print("  pass", label)
    else:
        F += 1
        print("  FAIL", label, "\n    got", got, "\n    exp", exp)


class Clock:
    def __init__(self, t=1000.0):
        self.t = t

    def __call__(self):
        return self.t

    def advance(self, dt):
        self.t += dt


clk = Clock()
R = relay_mod.Relay(cap=3, stale_s=30.0, clock=clk)

print("presence and frame-scoping")
R.beat("taproom", "alice", "I read the run before I raise", "character")
R.beat("taproom", "bob", "hands flat, watching the hood", "character")
R.beat("cellar", "carol", "the draught from the bad seam", "author")
ok("alice and bob are co-present at the taproom", R.view("taproom")["here"], 2)
ok("the cellar is its own frame", R.view("cellar")["here"], 1)
ok("vapour is frame-scoped — carol is not in the taproom",
   [p["handle"] for p in R.view("taproom")["present"]], ["alice", "bob"])

print("you are shown others, not yourself")
seen = R.view("taproom", exclude="alice")["present"]
ok("alice is not shown her own draft", [p["handle"] for p in seen], ["bob"])
ok("alice sees bob's live vapour", seen[0]["vapour"], "hands flat, watching the hood")

print("the load signal (the capacity the unfolder reads)")
ok("load is the live count across all frames", R.load(), 3)
ok("at cap, the relay calls itself saturated", R.view("taproom")["saturated"], True)
R.depart("cellar", "carol")
ok("a clean departure drops the load", R.load(), 2)
ok("and clears saturation", R.view("taproom")["saturated"], False)

print("the staleness horizon (silent vapour evaporates)")
clk.advance(31)
ok("a heartbeat past the horizon is gone", R.view("taproom")["here"], 0)
ok("and the load falls to nothing", R.load(), 0)
R.beat("taproom", "alice", "back at the table", "character")
ok("a fresh beat reappears", R.view("taproom")["here"], 1)

print()
print("TOTAL: %d passed, %d failed" % (P, F))
sys.exit(1 if F else 0)
