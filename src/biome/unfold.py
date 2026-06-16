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

SHELL = os.path.join(HERE, "constitution", "biome.json")

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
    local_kin = [n for n in cond.get("neighbours", []) if n["kind"] in ("biome", "agent")]
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

    # 6 federation — a set when local kin are sensed alongside network reach
    fed_sel = []
    if local_kin:
        fed_sel.append((2, "%d local instance%s sensed — watched surfaces"
                        % (len(local_kin), "" if len(local_kin) == 1 else "s")))
    if reach:
        fed_sel.append((3, "a beach is reachable — outbound peering"))
    sel[6] = fed_sel or [(1, "no reach sensed — commons fallback")]

    # 7 cadence
    sel[7] = [(4, "an embedded loop runs always-on")] if key \
        else [(1, "no loop — runs when called")]

    return sel


def _opt(shell, branch, idx):
    """Read option text at branch.idx from the shell via spark (a point read)."""
    return spark.spark(shell, "%d.%d" % (branch, idx), -1).get("text")


ROLES = {"mind": 1, "related": 2, "commons": 3, "substrate": 4}


def resolve_role(cond, shell):
    """Resolve a role from surface + capacity + neighbours — an intention to
    grow into, never a hard mode. The role's meaning is read from the shell
    (the nodes under 8.8, address 8.8N walks 8,8,N); code only senses which
    condition holds."""
    st, cog, cap = cond["storage"], cond["cognition"], cond.get("capacity", {})
    ep, fed = cond["endpoints"], cond["federation"]
    kin = cond.get("neighbours", [])
    local = [n for n in kin if n["kind"] in ("biome", "agent")]
    durable = st["filesystem_writable"] or st["hosted_db"]

    if cog["llm_key"]:
        name, reasons = "mind", ["an LLM key is present — cognition lives here"]
    elif cap.get("removable"):
        name, reasons = "related", ["the surface is removable — it relates by shared currents"]
        if local:
            reasons.append("%d local instance%s to relate to"
                           % (len(local), "" if len(local) == 1 else "s"))
    elif durable and ep["port_free"]:
        name, reasons = "commons", ["durable storage and a free port — a surface to serve"]
        if fed["reachable_beaches"] or local:
            reasons.append("neighbours sensed — someone to serve")
    else:
        name, reasons = "substrate", ["no role condition met — rest as a pure beach"]

    node = "8.8%d" % ROLES[name]
    return {"role": name, "node": node, "reasons": reasons,
            "text": spark.spark(shell, node, -2).get("text")}


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
    return {"conditions": cond, "unfolding": report,
            "intention": resolve_role(cond, shell)}


def _short(text, n=44):
    if not text:
        return "(unvoiced)"
    head = text.split(". ")[0]
    return head if len(head) <= n else head[:n - 1] + "…"


def _neighbour_line(n):
    if n["kind"] == "beach":
        return "beach %s (%s world)" % (n["url"], n["world"])
    if n["kind"] == "agent":
        return "agent shell at %s (%s)" % (n["path"], ", ".join(n["blocks"][:4]))
    tail = " — %s" % n["intention"] if n.get("intention") else ""
    return "biome %s at %s%s" % (n["state"], n["path"], tail)


def print_report(r):
    c = r["conditions"]
    st, cog, ep, fed = c["storage"], c["cognition"], c["endpoints"], c["federation"]
    cap, kin = c.get("capacity", {}), c.get("neighbours", [])
    print("biome — sense-and-print")
    print("runtime:", c["runtime"])
    print()
    print("conditions sensed")
    print("  storage    : fs_writable=%s  hosted_db=%s  upstream=%s"
          % (st["filesystem_writable"], bool(st["hosted_db"]), bool(st["upstream_beach"])))
    print("  capacity   : disk %s/%s GB free  removable=%s"
          % (cap.get("disk_free_gb"), cap.get("disk_total_gb"), cap.get("removable")))
    print("  cognition  : llm_key=%s  tty=%s" % (cog["llm_key"], cog["interactive_tty"]))
    print("  endpoints  : port %s free=%s" % (ep["port"], ep["port_free"]))
    print("  federation : reachable=%s" % (", ".join(fed["reachable_beaches"]) or "none"))
    print("  neighbours :%s" % ("" if kin else " none sensed"))
    for n in kin:
        print("    - %s" % _neighbour_line(n))
    print()
    print("would unfold as  (walking the 0-9 biome shell through spark)")
    for _, name in CURRENTS:
        for j, it in enumerate(r["unfolding"][name]):
            label = "%-11s" % name if j == 0 else " " * 11
            print("  %s [%d.%d] %-44s  ← %s"
                  % (label, it["branch"], it["option"], _short(it["text"]), it["reason"]))
    it = r["intention"]
    print()
    print("intention   [%s] %s — %s" % (it["node"], it["role"], "; ".join(it["reasons"])))
    text = it["text"] or "(unvoiced)"
    print("            %s" % (text if len(text) <= 88 else text[:87] + "…"))
    print()
    print("no surface committed — this is what the biome would become here.")


if __name__ == "__main__":
    print_report(unfold())
