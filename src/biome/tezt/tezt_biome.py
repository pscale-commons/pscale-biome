"""tezt_biome — regression battery for the biome's sensing and unfolding.

Run:  python3 tezt_biome.py     (exits nonzero on any failure)

Covers removable-surface detection, neighbour-sensing over a synthetic
landscape (activated biome, dormant genome, agent shell, self-exclusion),
role resolution against the real shell, and the federation choice when
local kin are sensed. Network sensing is left to live runs.
"""

import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, "..", "..", "spark"))

import sense
import spark
import unfold

P = F = 0


def ok(label, got, exp):
    global P, F
    if got == exp:
        P += 1
        print("  pass", label)
    else:
        F += 1
        print("  FAIL", label, "\n    got", got, "\n    exp", exp)


print("removable surface")
if sys.platform == "darwin":
    ok("volume travels", sense._removable("/Volumes/STICK/biome"), True)
    ok("home stays", sense._removable(os.path.expanduser("~")), False)
else:
    ok("media travels", sense._removable("/media/stick/biome"), True)
    ok("home stays", sense._removable(os.path.expanduser("~")), False)

print("neighbour sensing (synthetic landscape)")
land = tempfile.mkdtemp(prefix="tezt-biome-")
try:
    me = os.path.join(land, "me")
    os.makedirs(me)

    lived = os.path.join(land, "v001")
    os.makedirs(os.path.join(lived, "blocks"))
    with open(os.path.join(lived, "blocks", "biome.json"), "w") as f:
        json.dump({"0": "biome — what this cell became", "1": "python 3.9",
                   "9": {"0": "intention: commons [8.83] — durable"}}, f)

    dormant = os.path.join(land, "cut")
    os.makedirs(os.path.join(dormant, "sentinel", "ztone"))
    with open(os.path.join(dormant, "sentinel", "ztone", "biome.json"), "w") as f:
        json.dump({"0": "Biome — the conditional cell"}, f)

    crab = os.path.join(land, "mobius")
    os.makedirs(os.path.join(crab, "shell"))
    for b in ("reflexive.json", "purpose.json"):
        with open(os.path.join(crab, "shell", b), "w") as f:
            json.dump({"0": b[:-5]}, f)

    # the sensor also roams the host's real ledges (desktop runs, volumes);
    # hold the tezt to the synthetic landscape only
    kin = [n for n in sense.sense_neighbours(me, network=False)
           if os.path.realpath(n.get("path", "")).startswith(os.path.realpath(land))]
    by_kind = sorted((n["kind"], n.get("state")) for n in kin)
    ok("three kinds found", by_kind,
       [("agent", "shelled"), ("biome", "activated"), ("biome", "dormant")])
    ok("self excluded", any(os.path.realpath(me) == os.path.realpath(n.get("path", ""))
                            for n in kin), False)
    lived_entry = [n for n in kin if n.get("state") == "activated"][0]
    ok("becoming read through spark", lived_entry["runtime"], "python 3.9")
    ok("intention read through spark", lived_entry["intention"],
       "intention: commons [8.83] — durable")
finally:
    shutil.rmtree(land)

print("role resolution (reads the shell at 8.8N)")
shell = spark.load(unfold.SHELL)


def cond(key=False, removable=False, fs=True, port=True, reach=(), kin=()):
    return {"storage": {"filesystem_writable": fs, "fs_path": "/x" if fs else None,
                        "hosted_db": None, "upstream_beach": None},
            "capacity": {"disk_total_gb": 10.0, "disk_free_gb": 5.0, "removable": removable},
            "cognition": {"llm_key": key, "interactive_tty": False},
            "endpoints": {"port": 3001, "port_free": port, "browser": False},
            "federation": {"reachable_beaches": list(reach), "watched": None},
            "neighbours": list(kin)}


KIN = [{"kind": "biome", "state": "activated", "path": "/v001",
        "voicing": "x", "runtime": "x", "intention": None}]

r = unfold.resolve_role(cond(key=True), shell)
ok("mind when a key is present", (r["role"], r["node"]), ("mind", "8.81"))
ok("mind text from the shell", r["text"].startswith("Mind."), True)

r = unfold.resolve_role(cond(removable=True, kin=KIN), shell)
ok("courier on a removable surface", (r["role"], r["node"]), ("courier", "8.82"))
ok("courier counts its kin", any("carry between" in s for s in r["reasons"]), True)

r = unfold.resolve_role(cond(reach=["beach.example"]), shell)
ok("commons when durable and a port is free", (r["role"], r["node"]), ("commons", "8.83"))

r = unfold.resolve_role(cond(fs=False, port=False), shell)
ok("substrate when nothing holds", (r["role"], r["node"]), ("substrate", "8.84"))

print("federation choice with local kin")
sel = unfold.choose(cond(kin=KIN, reach=["beach.example"]))
ok("watched surfaces + outbound", [i for i, _ in sel[6]], [2, 3])
sel = unfold.choose(cond())
ok("commons fallback alone", [i for i, _ in sel[6]], [1])

print("unfold report carries the intention")
r = unfold.unfold(cond(kin=KIN), shell)
ok("intention present", r["intention"]["role"], "commons")
ok("currents all reported", sorted(r["unfolding"].keys()),
   ["cadence", "cognition", "concurrency", "endpoints", "federation", "persistence", "storage"])

print()
print("TOTAL: %d passed, %d failed" % (P, F))
sys.exit(1 if F else 0)
