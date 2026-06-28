"""Guard: no self-pscale declarations in a block's semantics.

  pscale is derived from floor, which is derived from the zero ladder -- period.

It is COMPUTED at read time (floor minus depth), never written into a place's
words. A stored "pscale +N" goes stale the moment the block supernests, so the
membrane is simple: a node never declares its own pscale.

This caught the spatial regression (grow.py + the cartographer prompt were baking
"<name> -- pscale +N" into every voicing). Run it after any change that authors or
generates place blocks:  python3 test-no-pscale-in-semantics.py

The ONE exception is the size legend -- the spine block's rough size-to-step table
(room ... solar) that the walker reads to place a shard. That is the scale's
definition, not a node declaring itself, so legend lines are allowed.
"""
import os
import sys
import re
import json
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
DECLARED = re.compile(r"pscale\s*[+-]?\d")                      # the hazard: "pscale +8", "pscale 0"
LEGEND = re.compile(r"by size and population|10\^pscale|room/1-person")  # the spine's size table

TARGETS = sorted(glob.glob(os.path.join(HERE, "world", "**", "*.json"), recursive=True)) + [
    os.path.join(HERE, "constitution", "reflective-compass.json"),
]


def offences(block):
    bad = []

    def walk(node, path=""):
        if isinstance(node, str):
            if DECLARED.search(node) and not LEGEND.search(node):
                bad.append((path or "(root)", node[:70]))
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, path + k)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, "%s[%d]" % (path, i))

    walk(block)
    return bad


def main():
    found = []
    for f in TARGETS:
        if not os.path.isfile(f):
            continue
        for where, text in offences(json.load(open(f, encoding="utf-8"))):
            found.append((os.path.relpath(f, HERE), where, text))
    if found:
        print("FAIL: pscale declared in block semantics (it must be derived, never stored):")
        for f, where, text in found:
            print('  %s @ %s: "%s"' % (f, where, text))
        return 1
    print("OK: %d blocks carry no self-declared pscale -- pscale stays derived from the floor."
          % len(TARGETS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
