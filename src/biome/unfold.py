"""unfold — the biome unfolder (branch 8 of the shell, enacted).

Read the 0-9 biome shell with the spark it carries, and for each of the seven
currents choose the form the sensed host conditions call for. No surface is
committed — this reports what the biome WOULD become here.

The biome reads its own genome with the function it carries and composes itself:
branch 8 sensed, branch 9 (the reading IS the unfolding) made real.

Run:  python3 unfold.py     (sense-and-print on the current host)
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spark"))
sys.path.insert(0, HERE)

import spark
import sense as sensor

SHELL = os.path.join(HERE, "..", "sentinel", "ztone", "biome.json")

CURRENTS = [
    (1, "storage"), (2, "cognition"), (3, "endpoints"), (4, "persistence"),
    (5, "concurrency"), (6, "federation"), (7, "cadence"),
]


def choose(cond):
    """Map sensed conditions onto an option (or options) per current.
    Returns {branch: [(option_index, reason), ...]}. Richest available wins."""
    st, cog, ep, fed = cond["storage"], cond["cognition"], cond["endpoints"], cond["federation"]
    fs, db, up = st["filesystem_writable"], st["hosted_db"], st["upstream_beach"]
    key, tty = cog["llm_key"], cog["interactive_tty"]
    reach = bool(fed["reachable_beaches"])
    sel = {}

    # 1 storage — richest available adapter wins (shell 1.7)
    if db:
        sel[1] = [(4, "a hosted DB is in env")]
    elif fs:
        sel[1] = [(1, "the filesystem is writable")]
    elif up:
        sel[1] = [(5, "an upstream beach is configured")]
    else:
        sel[1] = [(5, "no local surface — borrow an upstream beach")]

    # 2 cognition
    sel[2] = [(2, "an LLM key is present — embedded loop")] if key \
        else [(1, "no key — await a connecting app over MCP")]

    # 3 endpoints — a set, not one
    eps = []
    if tty:
        eps.append((5, "a TTY is attached"))
    if ep["port_free"]:
        eps.append((1, "a port is free"))
        eps.append((2, "a port is free"))
    sel[3] = eps or [(1, "default surface")]

    # 4 persistence
    if fs or db:
        sel[4] = [(3, "writes survive on a durable local surface")]
    elif up:
        sel[4] = [(4, "writes replicate to the upstream beach")]
    else:
        sel[4] = [(1, "no durable surface — ephemeral")]

    # 5 concurrency
    sel[5] = [(1, "one inhabitant sensed")]

    # 6 federation
    sel[6] = [(3, "a beach is reachable — outbound peering")] if reach \
        else [(1, "no reach sensed — commons fallback")]

    # 7 cadence
    sel[7] = [(4, "an embedded loop runs always-on")] if key \
        else [(1, "no loop — runs when called")]

    return sel


def _opt(shell, branch, idx):
    """Read option text at branch.idx from the shell via spark (a point read)."""
    return spark.spark(shell, "%d.%d" % (branch, idx), -1).get("text")


def unfold(cond=None, shell=None):
    cond = sensor.sense() if cond is None else cond
    shell = spark.load(SHELL) if shell is None else shell
    sel = choose(cond)
    report = {}
    for branch, name in CURRENTS:
        report[name] = [
            {"branch": branch, "option": idx, "text": _opt(shell, branch, idx), "reason": reason}
            for idx, reason in sel[branch]
        ]
    return {"conditions": cond, "unfolding": report}


def _short(text, n=44):
    if not text:
        return "(unvoiced)"
    head = text.split(". ")[0]
    return head if len(head) <= n else head[:n - 1] + "…"


def print_report(r):
    c = r["conditions"]
    st, cog, ep, fed = c["storage"], c["cognition"], c["endpoints"], c["federation"]
    print("biome — sense-and-print")
    print("runtime:", c["runtime"])
    print()
    print("conditions sensed")
    print("  storage    : fs_writable=%s  hosted_db=%s  upstream=%s"
          % (st["filesystem_writable"], bool(st["hosted_db"]), bool(st["upstream_beach"])))
    print("  cognition  : llm_key=%s  tty=%s" % (cog["llm_key"], cog["interactive_tty"]))
    print("  endpoints  : port %s free=%s" % (ep["port"], ep["port_free"]))
    print("  federation : reachable=%s" % (", ".join(fed["reachable_beaches"]) or "none"))
    print()
    print("would unfold as  (walking the 0-9 biome shell through spark)")
    for _, name in CURRENTS:
        for j, it in enumerate(r["unfolding"][name]):
            label = "%-11s" % name if j == 0 else " " * 11
            print("  %s [%d.%d] %-44s  ← %s"
                  % (label, it["branch"], it["option"], _short(it["text"]), it["reason"]))
    print()
    print("no surface committed — this is what the biome would become here.")


if __name__ == "__main__":
    print_report(unfold())
