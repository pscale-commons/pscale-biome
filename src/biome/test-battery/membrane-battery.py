"""membrane-battery — the identity membrane (handle-mode).

Run:  python3 membrane-battery.py     (exits nonzero on any failure)

Proves the located-write flow on a fresh store: reads open, unlocated writes
refused, registration (the one write an Observer may make), the CADO aperture
(Character < Author < Designer over marks < world < constitution), ownership
sovereignty (no writing another's shell), and that the lock is a single swap
point (verify_proof). The membrane is off by default; this drives it directly.
"""

import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, "..", "..", "spark"))

import membrane
from store_fs import FsStore

P = F = 0


def ok(label, got, exp):
    global P, F
    if got == exp:
        P += 1
        print("  pass", label)
    else:
        F += 1
        print("  FAIL", label, "\n    got", got, "\n    exp", exp)


CONST = frozenset({"arrive", "genome", "biome-shell", "battery", "slate", "flint"})
root = tempfile.mkdtemp(prefix="battery-membrane-")
store = FsStore(os.path.join(root, "blocks"))


def w(handle, block, content="x"):
    args = {"block": block, "content": content}
    if handle:
        args["handle"] = handle
    return membrane.check(store, args, CONST)[0]


def r(block):
    return membrane.check(store, {"block": block}, CONST)[0]


try:
    print("the flag (off by default keeps a live beach open)")
    os.environ.pop("BIOME_MEMBRANE", None)
    ok("off by default", membrane.enabled(), False)
    ok("on by env", membrane.enabled() if not os.environ.update({"BIOME_MEMBRANE": "on"}) else membrane.enabled(), True)
    os.environ.pop("BIOME_MEMBRANE", None)

    print("reads open, unlocated writes refused")
    ok("an Observer reads any block", r("thornkeep"), True)
    ok("an unlocated write is refused", w(None, "marks"), False)
    ok("an unregistered handle is refused", w("ghost", "marks"), False)
    ok("but a handle may register its own shell", w("ghost", "shell-ghost"), True)

    print("the CADO aperture (register, then write within your face)")
    store.save_block("shell-alice", {"0": "alice — a visitor", "1": "character"})
    ok("alice may write her own surface", w("alice", "surface-alice"), True)
    ok("Character writes marks", w("alice", "marks"), True)
    ok("Character refused world (needs author+)", w("alice", "thornkeep"), False)
    ok("Character refused constitution", w("alice", "arrive"), False)

    store.save_block("shell-bob", {"0": "bob — an author", "1": "author"})
    ok("Author writes world", w("bob", "thornkeep"), True)
    ok("Author still refused constitution (needs designer)", w("bob", "arrive"), False)

    store.save_block("shell-dora", {"0": "dora — a designer", "1": "designer"})
    ok("Designer writes constitution", w("dora", "arrive"), True)
    ok("Designer writes world too", w("dora", "thornkeep"), True)

    print("ownership sovereignty (no writing another's identity)")
    ok("bob cannot write alice's shell", w("bob", "shell-alice"), False)
    ok("bob cannot write alice's surface", w("bob", "surface-alice"), False)
    ok("a default registration is a Character", membrane.shell_face(store.load_block("shell-alice")), "character")

    print("the lock is a single swap point (verify_proof)")
    ok("handle-mode: a registered shell proves itself", membrane.verify_proof(store.load_block("shell-alice"), "alice", None), True)
    ok("handle-mode: no shell, no proof", membrane.verify_proof(None, "x", None), False)
finally:
    shutil.rmtree(root)

print()
print("TOTAL: %d passed, %d failed" % (P, F))
sys.exit(1 if F else 0)
