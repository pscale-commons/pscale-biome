"""cadence-battery — the time prune (doc 2: period, last-touched, phase).

Run:  python3 cadence-battery.py     (exits nonzero on any failure)

PA1 — a recently-fired periodic concern is pruned; an overdue one is admitted.
PA2 — stamping on a fold closes the loop (fired this wake -> pruned next).
Plus: aperiodic pass-through, hierarchical dormancy (a periodic parent sleeps its
subtree), the necessary-not-sufficient rule (admitted-but-coherent does not
stamp), and the inert default (no cadence -> phase prune is a no-op).
All on pure functions with an injected `now` — no clock, no shell, no LLM.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, "..", "..", "spark"))

import kernel  # noqa: E402

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


NOW = 1_000_000.0
# branch 2 is periodic (period 100s); branch 1 is NOT, but its child 1.3 is (10s).
CAD = {"0": "cadence", "2": "100", "1": {"3": "10"}}


def cand(addr, path, kind="missing"):
    return {"address": "purpose:" + addr, "path": list(path), "type": kind}


print("phase arithmetic")
ok("never fired -> infinite (admit)", kernel._phase("100", None, NOW), float("inf"))
ok("(now-touched)/period", kernel._phase("100", NOW - 200, NOW), 2.0)
ok("just fired -> 0", kernel._phase("100", NOW, NOW), 0.0)
ok("zero period -> infinite (never sleeps)", kernel._phase("0", NOW, NOW), float("inf"))

print("\ncadence paths (which branches are periodic)")
ok("periodic branches, parent-9-voicing excluded",
   set(kernel._cadence_paths(CAD)), {("2",), ("1", "3")})
ok("inert cadence -> nothing periodic", kernel._cadence_paths({"0": "c"}), [])

print("\nphase prune (PA1)")
cands = [cand("1", ("1",)), cand("2", ("2",)), cand("1.3", ("1", "3"))]
fresh = {"0": "lt", "2": str(NOW), "1": {"3": str(NOW)}}        # 2 and 1.3 just fired
kept, pruned = kernel.phase_prune(cands, CAD, fresh, now=NOW)
ok("aperiodic branch 1 is kept", "purpose:1" in [c["address"] for c in kept], True)
ok("fresh periodic branch 2 is pruned", "purpose:2" in [c["address"] for c in pruned], True)
ok("fresh periodic branch 1.3 is pruned", "purpose:1.3" in [c["address"] for c in pruned], True)

overdue = {"0": "lt", "2": str(NOW - 500), "1": {"3": str(NOW - 500)}}   # both long overdue
kept2, pruned2 = kernel.phase_prune(cands, CAD, overdue, now=NOW)
ok("overdue periodic branches are admitted", sorted(c["address"] for c in kept2),
   ["purpose:1", "purpose:1.3", "purpose:2"])
ok("nothing pruned when all overdue", pruned2, [])

print("\nhierarchical dormancy (a periodic parent sleeps its subtree)")
sub = [cand("2.1", ("2", "1")), cand("2.4", ("2", "4"))]       # children of periodic, fresh-fired branch 2
ksub, psub = kernel.phase_prune(sub, CAD, fresh, now=NOW)
ok("children of a dormant periodic parent are pruned", ksub, [])
ok("both children pruned via the ancestor period", len(psub), 2)

print("\ninert default (no behaviour change)")
k0, p0 = kernel.phase_prune(cands, {"0": "cadence"}, {}, now=NOW)
ok("no cadence -> everything kept", len(k0), 3)
ok("no cadence -> nothing pruned", p0, [])

print("\nstamp on fold (PA2) + necessary-not-sufficient")
g_in = [{"address": "purpose:2.1", "path": ["2", "1"], "type": "missing"}]
lasts = {"0": "lt"}
stamped = kernel.stamp_touched(g_in, applied=2, cadence=CAD, lasts=lasts, now=NOW)
ok("a γ under a periodic concern, with edits, stamps it", stamped, [("2",)])
ok("the stamp is now, at the concern address", lasts["2"], str(int(NOW)))
# the loop closes: having fired this wake, branch 2 is pruned next wake
k3, p3 = kernel.phase_prune([cand("2", ("2",))], CAD, lasts, now=NOW + 1)
ok("a concern fired this wake is pruned next wake", [c["address"] for c in p3], ["purpose:2"])

ns_lasts = {"0": "lt"}
ns = kernel.stamp_touched([{"address": "purpose:1", "path": ["1"], "type": "missing"}],
                          applied=2, cadence=CAD, lasts=ns_lasts, now=NOW)
ok("a γ at an aperiodic branch stamps nothing", ns, [])
ok("no applied edits -> no stamp even with a γ under a concern",
   kernel.stamp_touched(g_in, applied=0, cadence=CAD, lasts={"0": "lt"}, now=NOW), [])

print("\n%d ok, %d failed" % (P, F))
sys.exit(1 if F else 0)
