"""tezt_mind — regression battery for the mind-pulse and the HTTP store.

Run:  python3 tezt_mind.py     (exits nonzero on any failure)

Covers the address form, mechanical gap-finding, window composition, and
the HttpStore membrane against an in-process commons. The LLM call is left
to live pulses.
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

import mind
import serve
from store_fs import FsStore
from store_http import HttpStore

P = F = 0


def ok(label, got, exp):
    global P, F
    if got == exp:
        P += 1
        print("  pass", label)
    else:
        F += 1
        print("  FAIL", label, "\n    got", got, "\n    exp", exp)


print("address form (floor 2)")
ok("at the floor", mind.address(["4", "2"], 2), "42")
ok("below the floor", mind.address(["4", "2", "1"], 2), "42.1")
ok("above the floor is skipped", mind.address(["7"], 2), None)

print("gap finding")
W = {"0": {"0": "region"},
     "4": {"0": "town",
           "2": {"0": "tavern", "1": "taproom"},
           "5": {"1": "a stair"}}}                        # 4,5 headless (no 0)
ok("a headless place is voiced first", mind.find_gap(W, None), ("voice-headless", ["4", "5"]))
W["4"]["5"] = {"0": "the watchtower"}
ok("absent scenes block seeds the T aspect", mind.find_gap(W, None), ("seed-scene", ["4", "2", "1"]))
ok("a thin place grows once scenes exist", mind.find_gap(W, {"0": "scenes"}), ("grow-thin", ["4", "5"]))
W["4"]["5"]["2"] = "a beacon"
ok("a settled world rests", mind.find_gap(W, {"0": "scenes"}), (None, None))

print("the window")
W["4"]["5"] = {"0": "the watchtower"}
win, number = mind.compose_window(W, "grow-thin", ["4", "5"])
ok("the window walks the spindle", "the watchtower" in win and "p+0" in win, True)
ok("the window carries the contract", "STRICT JSON" in win, True)
ok("the gap's address", number, "45")

print("the http store membrane")
root = tempfile.mkdtemp(prefix="tezt-mind-")
store = FsStore(os.path.join(root, "blocks"))
store.save_block("biome", {"0": "becoming", "1": "tezt · genome v4"})
serve.seed(store)
serve.Commons.store = store
httpd = ThreadingHTTPServer(("127.0.0.1", 0), serve.Commons)
port = httpd.server_address[1]
threading.Thread(target=httpd.serve_forever, daemon=True).start()
try:
    remote = HttpStore("http://127.0.0.1:%d" % port)
    ok("loads through the door", remote.load_block("thornkeep")["4"]["2"]["1"],
       "the taproom — long benches, a peat fire, the smell of wet wool")
    ok("absence reads as None", remote.load_block("scenes"), None)
    remote.save_block("scenes", {"0": "scenes — sown over the wire"})
    ok("saves whole blocks through the door", remote.load_block("scenes")["0"],
       "scenes — sown over the wire")
    ok("shaped writes land", remote.write("thornkeep", "42.4", None,
       "the cellar — cool dark, barrels of moor-ale")["ok"], True)
    ok("and read back", remote.load_block("thornkeep")["4"]["2"]["4"],
       "the cellar — cool dark, barrels of moor-ale")
    ok("lists the surface", "thornkeep" in remote.list_blocks(), True)
finally:
    httpd.shutdown()
    shutil.rmtree(root)

print()
print("TOTAL: %d passed, %d failed" % (P, F))
sys.exit(1 if F else 0)
