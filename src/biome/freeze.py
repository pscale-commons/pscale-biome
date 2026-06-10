"""freeze — formalise the genome: the frozen base of biome conformality.

Writes sentinel/ztone/genome.json: a block stating what every conformal
instance shares — the 0-9 geometry, the one spark signature, the wire
surface, and the tezt battery as the conformance criterion — plus sha256
fingerprints of the carried reference artifacts (slate, flint, spark.py,
spark.ts). Two instances are kin when they carry the same genome version.

Freezing is deliberate and rare: a new version is an explicit act, never
drift. Run:  python3 freeze.py v1 2026-06-10
Verify:      python3 freeze.py --verify
"""

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPARK = os.path.join(HERE, "..", "spark")
GENOME = os.path.join(HERE, "..", "sentinel", "ztone", "genome.json")

ARTIFACTS = [("slate", "slate.json"), ("flint", "flint.json"),
             ("spark-py", "spark.py"), ("spark-ts", "spark.ts")]


def fingerprint(fn):
    with open(os.path.join(SPARK, fn), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]


def freeze(version, date):
    block = {
        "0": "Genome %s — the frozen base of biome conformality, set %s. Two instances "
             "are kin when they carry this same genome: the 0-9 geometry, the one spark, "
             "the wire surface, and the battery that proves an implementation conforms. "
             "A new version is a deliberate act of freezing, never drift." % (version, date),
        "1": version,
        "2": "Geometry. A block is JSON whose every key is a single digit 0-9. Digit 0 is "
             "a node's own semantic; 1-9 are its elaboration. The zero-spine sets the floor; "
             "pscale = floor - depth. Every position is reached by an ordinary walk; a second "
             "aspect of a coordinate lives in another block at the same coordinate. Addresses "
             "carry one decimal pinned to the floor; walks are written with commas.",
        "3": "Function. One call over two coordinates and an optional payload: "
             "spark(block, number, attention, content?). Content omitted reads; content "
             "provided writes the same shape. The shape — point, ring, directory, disc, "
             "spindle, whole — derives from (number, attention) against the floor, never chosen.",
        "4": "Wire. A commons serves every surface through the one spark, at world-typed "
             "doors. Beach: GET /.well-known/ztone-beach?block=NAME returns the whole block; "
             "POST the same path with {block, number, attention, content} writes — and the "
             "door's membrane refuses beach-world shapes (a `_` key anywhere). MCP at /mcp "
             "carries the single tool spark for connecting LLM apps. The legacy federation's "
             "/.well-known/pscale-beach is another world's door: a ztone host signposts it, "
             "never serves it. The URL is the instance's identity.",
        "5": "Conformance. An implementation is conformal when it passes the carried tezt "
             "battery (at %s: 42 Python, 33 TypeScript). The battery, not the fingerprint, "
             "judges a fresh implementation; the fingerprints below identify the reference "
             "artifacts this genome was frozen from." % version,
        "6": {"0": "Reference artifacts at %s, sha256 first 12 hex." % version},
    }
    for i, (name, fn) in enumerate(ARTIFACTS, start=1):
        block["6"][str(i)] = "%s %s" % (name, fingerprint(fn))
    with open(GENOME, "w", encoding="utf-8") as f:
        json.dump(block, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return block


def verify():
    """Check the carried artifacts against the frozen fingerprints."""
    with open(GENOME, encoding="utf-8") as f:
        block = json.load(f)
    version, drift = block["1"], []
    for i, (name, fn) in enumerate(ARTIFACTS, start=1):
        frozen = block["6"][str(i)].split()[-1]
        if fingerprint(fn) != frozen:
            drift.append(name)
    return version, drift


if __name__ == "__main__":
    if "--verify" in sys.argv:
        version, drift = verify()
        if drift:
            print("genome %s: DRIFT in %s — refreeze deliberately or restore" % (version, ", ".join(drift)))
            sys.exit(1)
        print("genome %s: conformal — carried artifacts match the freeze" % version)
    else:
        if len(sys.argv) < 3:
            sys.exit("usage: freeze.py <version> <date>   |   freeze.py --verify")
        b = freeze(sys.argv[1], sys.argv[2])
        print("frozen: genome %s -> %s" % (b["1"], os.path.relpath(GENOME)))
        for k in sorted(b["6"]):
            if k != "0":
                print("  " + b["6"][k])
