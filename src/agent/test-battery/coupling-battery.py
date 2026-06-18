"""coupling-battery — the phase channel between agents (doc 3).

Run:  python3 coupling-battery.py     (exits nonzero on any failure)

Covers the cycle-position θ, the Kuramoto order parameter r, the Sakaguchi
separation nudge, the de-synchronization dynamics (a perturbed near-sync triad
drives to the SPLAY, not unison), and effective_phase = phase + φ feeding the
prune. The live publish/read/peer plumbing is exercised by the experiment.
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


print("cycle-position θ and the order parameter")
ok("θ = phase mod 1", round(kernel._theta(2.3), 4), 0.3)
ok("θ of never-fired (∞) is 0", kernel._theta(float("inf")), 0.0)
check("r → 0 at the splay (0, 1/3, 2/3)", kernel.order_parameter([0, 1 / 3, 2 / 3]) < 0.01)
ok("r = 1 at unison", round(kernel.order_parameter([0.4, 0.4, 0.4]), 4), 1.0)

print("\nthe Sakaguchi separation nudge")
ok("no peers -> no nudge", kernel.couple_nudge(0.3, []), 0.0)
check("a coincident peer nudges (does not sit at sync)", abs(kernel.couple_nudge(0.0, [0.0])) > 0)
check("nudge scales with gain", abs(kernel.couple_nudge(0.0, [0.2])) <= kernel.COUPLE_GAIN + 1e-9)

print("\nde-synchronization: a perturbed near-sync triad drives to the SPLAY")
base, phi = [0.0, 0.05, 0.10], [0.0, 0.0, 0.0]
eff = lambda: [(base[i] + phi[i]) % 1 for i in range(3)]   # noqa: E731
r0 = kernel.order_parameter(eff())
for _ in range(60):
    e = eff()
    phi = [phi[i] + kernel.couple_nudge(e[i], [e[j] for j in range(3) if j != i])
           for i in range(3)]
rF = kernel.order_parameter(eff())
offs = sorted((eff()[j] - eff()[0]) % 1 for j in range(1, 3))
print("    r: %.3f -> %.3f   final offsets-from-A: %s"
      % (r0, rF, [round(o, 3) for o in offs]))
check("started near unison (r > 0.9)", r0 > 0.9)
check("drove away from unison to the splay (r < 0.2)", rF < 0.2)
check("did NOT collapse to unison (r not climbing to 1)", rF < r0)
check("offsets approach 1/3 and 2/3", abs(offs[0] - 1 / 3) < 0.1 and abs(offs[1] - 2 / 3) < 0.1)

print("\neffective_phase = phase + φ feeds the prune")
NOW = 1_000_000.0
CAD = {"0": "c", "2": "100"}
cand = [{"address": "purpose:2", "path": ["2"], "type": "missing"}]
fresh = {"0": "lt", "2": str(NOW)}                              # phase 0 -> dormant
_, pr = kernel.phase_prune(cand, CAD, fresh, now=NOW)
ok("fresh periodic concern is dormant without φ", [c["address"] for c in pr], ["purpose:2"])
kept, _ = kernel.phase_prune(cand, CAD, fresh, now=NOW, phis={("2",): 1.5})
ok("a positive φ wakes it (effective 1.5 ≥ 1)", [c["address"] for c in kept], ["purpose:2"])
overdue = {"0": "lt", "2": str(NOW - 150)}                      # phase 1.5 -> ripe
_, pr2 = kernel.phase_prune(cand, CAD, overdue, now=NOW, phis={("2",): -1.0})
ok("a negative φ defers it (effective 0.5 < 1)", [c["address"] for c in pr2], ["purpose:2"])

print("\n%d ok, %d failed" % (P, F))
sys.exit(1 if F else 0)
