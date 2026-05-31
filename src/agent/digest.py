#!/usr/bin/env python3
"""digest.py — summarise an experiment run at a glance. No copy-paste needed.

Run from the working copy's agent/ directory:

    python3 digest.py

Shows every real pulse — including REST pulses (γ=∅) — with its gap, edits,
failures, status, note, and any self-set heartbeat. The run's story in one screen.
"""
import glob
import json
import os


def short(t, n=100):
    return (t[:n] + "…") if isinstance(t, str) and len(t) > n else (t or "")


def main():
    files = sorted(glob.glob(os.path.join("filmstrip", "*.json")))
    real = [f for f in files if "status" in json.load(open(f))]   # rest + δ pulses
    print("%d filmstrips · %d real pulses" % (len(files), len(real)))
    prev = None
    for f in real:
        d = json.load(open(f))
        p = d.get("parsed", {})
        g = len(d.get("gamma", []))
        arrow = "" if prev is None else ("  (γ %d→%d)" % (prev, g))
        prev = g
        print("\n● %s   γ=%d  status=%s  applied=%s  failed=%d%s"
              % (os.path.basename(f), g, d.get("status"), d.get("applied", "-"),
                 len(d.get("failed") or []), arrow))
        print("  note: %s" % short(p.get("note") or d.get("note")))
        for e in (p.get("edits") or []):
            print("   edit  %s [%s]" % (e.get("address"), e.get("class")))
        for fl in (d.get("failed") or []):
            print("   FAIL  %s — %s" % (fl.get("address"), fl.get("error")))
        hb = p.get("heartbeat")
        if hb is not None:
            print("  self-set heartbeat: %ss" % hb)


if __name__ == "__main__":
    main()
