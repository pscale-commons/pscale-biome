"""Test the located block and its three seams (docs/located-block-spec.md):
seam 1 (situate persists the standing), seam 3 (the membrane reads located.3 for
the live face, capped at the shell's grant), and seam 2 (the agent shell carries
located, referenced from the reflexive bundle)."""
import os
import sys
import json
import tempfile
import py_compile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spark"))
sys.path.insert(0, HERE)
import located
import membrane
from store_fs import FsStore


def main():
    checks = []
    store = FsStore(tempfile.mkdtemp())

    # seam 1 -- situate writes located-<handle>, idempotent, in the spec shape
    w1 = located.situate(store, "alice", kind="agent", world="real-world", face="author",
                         where="Ceidio", island="biome.example", infra="host")
    w2 = located.situate(store, "alice", kind="agent", world="real-world", face="author",
                         where="Ceidio", island="biome.example", infra="host")
    blk = located.read(store, "alice")
    checks += [
        ("situate writes then no-ops (idempotent)", w1 is True and w2 is False),
        ("face at .3", blk["3"] == "author"),
        ("world at .2, where at .4", blk["2"] == "real-world" and blk["4"] == "Ceidio"),
        ("biome-legal (digit keys only)", all(k.isdigit() for k in blk)),
        ("face_of reads .3", located.face_of(store, "alice") == "author"),
        ("face_of None when no block", located.face_of(store, "ghost") is None),
    ]

    # seam 3 -- located.3 is the live face, capped at the shell's grant
    C = frozenset(["genome", "slate"])
    store.save_block("shell-alice", {"0": "alice", "1": "author"})            # grant: author
    checks.append(("located author may write a world block",
                   membrane.check(store, {"block": "thornkeep", "content": {"0": "x"}, "handle": "alice"}, C)[0]))

    store.save_block("shell-bob", {"0": "bob", "1": "character"})             # grant: character
    located.situate(store, "bob", face="designer")                            # bob CLAIMS designer
    checks += [
        ("located cannot escalate past the grant (world refused)",
         membrane.check(store, {"block": "thornkeep", "content": {"0": "x"}, "handle": "bob"}, C)[0] is False),
        ("capped face still writes its own stratum (marks)",
         membrane.check(store, {"block": "marks", "content": {"0": "x"}, "handle": "bob"}, C)[0] is True),
    ]
    store.save_block("shell-carol", {"0": "carol", "1": "author"})           # no located block
    checks.append(("no located: falls back to the shell grant",
                   membrane.check(store, {"block": "thornkeep", "content": {"0": "x"}, "handle": "carol"}, C)[0]))

    # seam 2 -- the agent shell carries located; the reflexive bundle references it
    refl = json.load(open(os.path.join(HERE, "..", "agent", "shell", "reflexive.json")))
    al = json.load(open(os.path.join(HERE, "..", "agent", "shell", "located.json")))
    checks += [
        ("agent shell located.json valid, digit keys", all(k.isdigit() for k in al)),
        ("reflexive bundle still valid + references located + conditions",
         "located" in json.dumps(refl["9"]) and "conditions" in json.dumps(refl["9"])),
    ]

    # the concurrent multi-world ring -- a handle present in two worlds at once
    def legal(x):
        if isinstance(x, dict):
            return all(k.isdigit() and legal(v) for k, v in x.items())
        return True
    r = FsStore(tempfile.mkdtemp())
    located.situate(r, "nomad", kind="agent", world="real-world", face="author", where="Ceidio")
    located.situate(r, "nomad", kind="agent", world="thornkeep", face="character", where="the Drum")
    nb = located.read(r, "nomad")
    checks += [
        ("ring: active is the latest world", nb["2"] == "thornkeep" and nb["3"] == "character"),
        ("ring: the other world is preserved at 8", "real-world" in json.dumps(nb.get("8", {}))),
        ("ring: worlds() lists both, active first", located.worlds(r, "nomad") == ["thornkeep", "real-world"]),
        ("ring: face_of(world) is per-world", located.face_of(r, "nomad", "real-world") == "author"
                                              and located.face_of(r, "nomad", "thornkeep") == "character"),
        ("ring: face_of() is the active face", located.face_of(r, "nomad") == "character"),
        ("ring: still biome-legal (digit keys all the way down)", legal(nb)),
    ]
    located.situate(r, "nomad", kind="agent", world="real-world", face="author", where="Ceidio")
    checks.append(("ring: re-situating a ring world swaps it active",
                   located.worlds(r, "nomad") == ["real-world", "thornkeep"]))
    located.depart(r, "nomad", "thornkeep")
    checks.append(("ring: depart drops a ring world", located.worlds(r, "nomad") == ["real-world"]))
    located.depart(r, "nomad", "real-world")
    checks.append(("ring: departing the last leaves a neutral standing", located.worlds(r, "nomad") == []))

    try:
        py_compile.compile(os.path.join(HERE, "serve.py"), doraise=True)
        checks.append(("serve.py compiles with located wired into /relay", True))
    except Exception:
        checks.append(("serve.py compiles with located wired into /relay", False))

    for name, ok in checks:
        print(("  OK  " if ok else "  XX  ") + name)
    bad = [n for n, ok in checks if not ok]
    if bad:
        print("FAIL: %d/%d" % (len(bad), len(checks)))
        return 1
    print("OK: %d checks passed" % len(checks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
