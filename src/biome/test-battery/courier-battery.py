"""courier-battery — regression battery for the carry and the re-sense pulse.

Run:  python3 courier-battery.py     (exits nonzero on any failure)

Spins an in-process commons as the visited door, carries from it onto a
second store (the stick), and checks: world content travels, per-space
blocks stay home, the carry is recorded with provenance, the visited door
gains the courier's mark. Then re-sense: a becoming's kin lines update
when the landscape changes and hold steady when it does not.
"""

import json
import os
import shutil
import sys
import tempfile
import threading
from http.server import ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, "..", "..", "spark"))

import courier
import resense as resense_mod
import serve
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


print("the carry (commons -> stick)")
door_root = tempfile.mkdtemp(prefix="battery-door-")
stick_root = tempfile.mkdtemp(prefix="battery-stick-")
door = FsStore(os.path.join(door_root, "blocks"))
door.save_block("biome", {"0": "becoming", "1": "battery · genome v5"})
serve.seed(door)
door.save_block("scenes", {"0": {"0": "scenes"}, "4": {"0": "a scene"}})
door.save_block("fold-synthesis", {"0": "a guest theory block, landed at this door"})
serve.Commons.store = door
httpd = ThreadingHTTPServer(("127.0.0.1", 0), serve.Commons)
origin = "http://127.0.0.1:%d" % httpd.server_address[1]
threading.Thread(target=httpd.serve_forever, daemon=True).start()
try:
    stick = FsStore(os.path.join(stick_root, "blocks"))
    stick.save_block("biome", {"0": "becoming", "1": "stick · genome v5",
                               "9": {"0": "intention: courier"}})
    stick.save_block("marks", {"0": "the stick's own ledger", "1": "a local trace"})
    carried = courier.carry(origin, stick_root)
    ok("world content travels", sorted(carried), ["fold-synthesis", "scenes", "thornkeep"])
    ok("the world reads on the stick", stick.load_block("thornkeep")["4"]["2"]["1"],
       "the taproom — long benches, a peat fire, the smell of wet wool")
    ok("the stick's own ledger stays home", stick.load_block("marks")["1"], "a local trace")
    ok("the becoming is untouched", stick.load_block("biome")["1"], "stick · genome v5")
    record = stick.load_block("carried")
    ok("the carry is recorded with provenance",
       origin in record["1"] and "3 blocks" in record["1"], True)
    door_marks = door.load_block("marks")
    ok("the visited door gains the courier's mark",
       any("courier docked" in str(v) for k, v in door_marks.items() if k != "0"), True)
    carried2 = courier.carry(origin, stick_root)
    record = stick.load_block("carried")
    ok("a second carry takes the next digit", "2" in record, True)
finally:
    httpd.shutdown()

print("the re-sense pulse")
land = tempfile.mkdtemp(prefix="battery-resense-")
me = os.path.join(land, "me")
os.makedirs(os.path.join(me, "blocks"))
biome0 = {"0": "becoming", "1": "x · genome v5",
          "9": {"0": "intention: commons [8.83] — a surface to serve"}}
with open(os.path.join(me, "blocks", "biome.json"), "w") as f:
    json.dump(biome0, f)
try:
    changed, lines = resense_mod.resense(me, network=False)
    # the scan roams real ledges too; hold the check to the synthetic land
    kin_here = [l for l in lines if land in l]
    ok("first re-sense records the empty land", kin_here, [])
    neighbour = os.path.join(land, "v900")
    os.makedirs(os.path.join(neighbour, "blocks"))
    with open(os.path.join(neighbour, "blocks", "biome.json"), "w") as f:
        json.dump({"0": "biome — kin", "1": "py · genome v5"}, f)
    changed, lines = resense_mod.resense(me, network=False)
    ok("a new kin changes the becoming", changed, True)
    b = json.load(open(os.path.join(me, "blocks", "biome.json")))
    ok("the intention voicing survives the rewrite",
       b["9"]["0"].startswith("intention: commons"), True)
    ok("the re-sense note is stamped", "re-sensed" in b["9"]["0"], True)
    ok("the kin line lands in a digit",
       any("v900" in str(v) for k, v in b["9"].items() if k != "0"), True)
finally:
    shutil.rmtree(land)
    shutil.rmtree(door_root)
    shutil.rmtree(stick_root)

print()
print("TOTAL: %d passed, %d failed" % (P, F))
sys.exit(1 if F else 0)
