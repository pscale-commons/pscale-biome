"""launcher-battery — regression battery for biome.py (sense -> unfold -> become).

Run:  python3 launcher-battery.py     (exits nonzero on any failure)

Covers the role->form mapping and the become() branch decision against
synthetic conditions (no real sensing, no network, no LLM, nothing launched —
become is driven dry-run with injected conditions).
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, "..", "..", "spark"))

import biome

P = F = 0


def ok(label, got, exp):
    global P, F
    if got == exp:
        P += 1
        print("  pass", label)
    else:
        F += 1
        print("  FAIL", label, "\n    got", got, "\n    exp", exp)


print("role -> form mapping (forms = beach / mind / interface; courier retracted)")
ok("a commons is a beach", biome.form_for("commons"), "beach")
ok("a substrate is a beach", biome.form_for("substrate"), "beach")
ok("a key makes a mind", biome.form_for("mind"), "mind")
ok("courier maps to no form (retracted; relates, does not serve)", biome.form_for("courier"), None)
ok("an unknown role has no form", biome.form_for("whatever"), None)


def cond(key=False, removable=False, fs=True, port=True):
    return {"storage": {"filesystem_writable": fs, "fs_path": "/x" if fs else None,
                        "hosted_db": None, "upstream_beach": None},
            "capacity": {"disk_total_gb": 10.0, "disk_free_gb": 5.0, "removable": removable},
            "cognition": {"llm_key": key, "interactive_tty": False},
            "endpoints": {"port": 3210, "port_free": port, "browser": False},
            "federation": {"reachable_beaches": [], "watched": None},
            "neighbours": []}


print("become() resolves the fit form from the rock (dry-run, nothing launched)")
ok("storage + port -> beach", biome.become(cond(fs=True, port=True), dry_run=True), "beach")
ok("a key -> mind", biome.become(cond(key=True, fs=True, port=True), dry_run=True), "mind")
ok("removable surface -> no form (relates, does not serve)", biome.become(cond(removable=True, fs=True, port=False), dry_run=True), None)
ok("no storage, no key -> no form", biome.become(cond(fs=False, port=False), dry_run=True), None)

print()
print("TOTAL: %d passed, %d failed" % (P, F))
sys.exit(1 if F else 0)
