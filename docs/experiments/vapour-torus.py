"""vapour-torus -- the always-someone-live field, made mechanical on the real relay.

David's 38.7 insight: in a community of many agents whose think-cycles overlap, someone is
always live -- so a coherent thread (a resolution beat, a conversation) can be carried
hand-to-hand across a churning population with NO agent ever always-live and NO cron. The
cron is only an external pacemaker for when you want to FORCE a shared beat (tactical tempo)
or to rescue a population below threshold.

This is the phase space of overlapping presence -- a torus (the field persists though its
membership churns) within which a coherent carry is a soliton (it holds its shape while the
medium underneath it turns over). It rides src/biome/relay.py directly, with an injected
clock so it is deterministic and model-free (no LLM, no API cost, no commons touched).

  python3 docs/experiments/vapour-torus.py        (run from the repo root)

Finding: continuous liveness is EMERGENT above a (population x duty x afterglow) threshold.
Afterglow = the relay's stale window (each beat keeps you present for stale_s after) -- the
knob that trades concurrency for continuity. Above threshold the carry never drops; below,
the field tears (the '.' ticks) and the carry falls.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "biome"))
from relay import Relay


def run(N, live, gap, stale, ticks=72, label=""):
    clock = [0.0]
    r = Relay(cap=10000, stale_s=float(stale), clock=lambda: clock[0])
    cycle = live + gap
    timeline, torch, carriers, dropped = [], 0, set(), 0
    for t in range(ticks):
        clock[0] = float(t)
        for i in range(N):                                   # each agent beats only inside its live window
            phase = (i * cycle) // N                          # staggered so the windows overlap
            if t >= phase and (t - phase) % cycle < live:
                r.beat("torus", "a%02d" % i, vapour="carry", face="character")
        present = [p["handle"] for p in r.view("torus")["present"]]
        timeline.append(len(present))
        if present:                                          # the soliton: a live agent advances the carry, then hands off
            carriers.add(sorted(present)[t % len(present)])
            torch += 1
        else:
            dropped += 1
    cont = 100 * sum(1 for c in timeline if c) / ticks
    viz = "".join(str(min(c, 9)) if c else "." for c in timeline)
    print("%s  N=%d  each live %d of %d ticks (duty %.0f%%)  afterglow(stale)=%d"
          % (label, N, live, cycle, 100 * live / cycle, stale))
    print("   live agents / tick : %s" % viz)
    print("   torus continuity   : %.0f%% of ticks have a live agent (min=%d max=%d)"
          % (cont, min(timeline), max(timeline)))
    print("   soliton carry      : advanced %d steps via %d distinct carriers; DROPPED on %d ticks\n"
          % (torch, len(carriers), dropped))


if __name__ == "__main__":
    print("=== DENSE community -- the field is continuous, the carry never drops (a torus) ===")
    run(12, 4, 8, 3, label="dense ")
    print("=== SPARSE community -- coverage gaps; the field tears and the carry falls (no torus) ===")
    run(3, 2, 16, 3, label="sparse")
    print("Continuous liveness is EMERGENT above a (population x duty x afterglow) threshold.")
    print("Above it a coherent thread is carried hand-to-hand with NO agent always-live and NO cron;")
    print("the cron only matters below threshold, or to lock a tactical tempo (minute-by-minute combat).")
