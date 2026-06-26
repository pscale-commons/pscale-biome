"""serve-battery — regression battery for the commons surfaces.

Run:  python3 serve-battery.py     (exits nonzero on any failure)

Spins the commons in-process on an ephemeral port and exercises both
surfaces — the .well-known beach and the MCP endpoint — through real HTTP.
Offline: the store is a temp dir, seeded from the carried blocks; no
activation, no network sensing.
"""

import json
import os
import shutil
import sys
import tempfile
import threading
import urllib.request
from http.server import ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, "..", "..", "spark"))

import serve
from store_fs import FsStore


def spark_load_world():
    import spark
    return spark.load(os.path.join(os.path.dirname(HERE), "world", "thornkeep.json"))

P = F = 0


def ok(label, got, exp):
    global P, F
    if got == exp:
        P += 1
        print("  pass", label)
    else:
        F += 1
        print("  FAIL", label, "\n    got", got, "\n    exp", exp)


def http(path, body=None):
    url = "http://127.0.0.1:%d%s" % (PORT, path)
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"} if data else {})
    with urllib.request.urlopen(req) as r:
        raw = r.read().decode("utf-8")
        return r.status, json.loads(raw) if raw else None


def rpc(method, params=None, rid=1):
    msg = {"jsonrpc": "2.0", "method": method}
    if rid is not None:
        msg["id"] = rid
    if params is not None:
        msg["params"] = params
    return http("/mcp", msg)


root = tempfile.mkdtemp(prefix="battery-commons-")
store = FsStore(os.path.join(root, "blocks"))
store.save_block("biome", {"0": "biome — a test becoming", "1": "test · genome v2"})
refreshed, sown = serve.seed(store)
serve.Commons.store = store
httpd = ThreadingHTTPServer(("127.0.0.1", 0), serve.Commons)
PORT = httpd.server_address[1]
threading.Thread(target=httpd.serve_forever, daemon=True).start()

try:
    print("host conditions")
    for var in ("PORT", "BIOME_ROOT"):
        os.environ.pop(var, None)
    ok("a bare host stays loopback", serve.host_conditions()[:2], ("127.0.0.1", 3210))
    os.environ["PORT"], os.environ["BIOME_ROOT"] = "8080", "/data"
    ok("a platform host speaks through env", serve.host_conditions(), ("0.0.0.0", 8080, "/data"))
    for var in ("PORT", "BIOME_ROOT"):
        os.environ.pop(var, None)

    print("seeding")
    ok("constitution laid on a fresh store", sorted(refreshed),
       ["arrive", "battery", "biome-shell", "flint", "genome", "slate"])
    ok("world + marks sown once", sorted(sown), ["marks", "thornkeep"])
    ok("a settled store reseeds nothing", serve.seed(store), ([], []))
    store.save_block("arrive", {"0": "a guest scribbled over the constitution"})
    store.save_block("thornkeep", {"0": {"0": "a guest grew the world"}})
    refreshed2, sown2 = serve.seed(store)
    ok("constitution heals on reseed", refreshed2, ["arrive"])
    ok("guest-grown world is never overwritten", sown2 == [] and
       store.load_block("thornkeep")["0"]["0"], "a guest grew the world")
    store.save_block("thornkeep", spark_load_world())

    print("the beach surface (.well-known)")
    code, body = http("/")
    ok("the root is arrival", body["0"].startswith("Arrive"), True)
    code, body = http("/.well-known/biome-beach?block=thornkeep")
    ok("whole block read", body["4"]["2"]["1"],
       "the taproom — long benches, a peat fire, the smell of wet wool")
    code, body = http("/.well-known/biome-beach")
    ok("the surface lists its blocks", "thornkeep" in body["blocks"], True)
    code, body = http("/.well-known/biome-beach",
                      {"block": "marks", "number": "1", "attention": 0,
                       "content": "first trace — test"})
    ok("a write lands", body["ok"], True)
    code, body = http("/.well-known/biome-beach",
                      {"block": "marks", "number": "1", "attention": 0})
    ok("and reads back", body["text"], "first trace — test")

    print("the mcp surface")
    code, body = rpc("initialize", {"protocolVersion": "2025-03-26",
                                    "capabilities": {}, "clientInfo": {"name": "test"}})
    ok("initialize answers", body["result"]["serverInfo"]["name"], "biome-mcp")
    ok("initialize explains itself", "Reads have no side effects" in body["result"]["instructions"]
       and "narrate" in body["result"]["instructions"], True)
    code, body = http("/mcp", {"jsonrpc": "2.0", "method": "notifications/initialized"})
    ok("a notification is accepted", code, 202)
    code, body = rpc("tools/list")
    ok("two tools, spark and play", [t["name"] for t in body["result"]["tools"]], ["spark", "play"])
    tools = {t["name"]: t for t in body["result"]["tools"]}
    desc = tools["spark"]["description"]
    ok("the tool leads with plain terms", desc.startswith("Read and write this commons"), True)
    ok("the tool states its side-effect rule", "side-effect-free" in desc, True)
    ok("play declares it runs no model", "NO model" in tools["play"]["description"], True)
    ok("play requires a handle", tools["play"]["inputSchema"]["required"], ["handle"])
    code, body = rpc("tools/call", {"name": "spark",
                                    "arguments": {"block": "thornkeep", "number": "42.1", "attention": -1}})
    ok("a visitor reaches the taproom", "taproom" in body["result"]["content"][0]["text"], True)
    code, body = rpc("tools/call", {"name": "spark",
                                    "arguments": {"block": "marks", "number": "2", "attention": 0,
                                                  "content": "second trace — via mcp"}})
    ok("a visitor leaves a mark", "ok" in json.loads(body["result"]["content"][0]["text"]), True)
    code, body = rpc("tools/call", {"name": "spark", "arguments": {"block": "marks", "attention": 0}})
    disc = json.loads(body["result"]["content"][0]["text"])
    ok("the marks disc holds both traces",
       [n["text"] for n in disc["nodes"] if n["address"] != "0"],
       ["first trace — test", "second trace — via mcp"])
    code, body = rpc("tools/call", {"name": "spark", "arguments": {"block": "arrive"}})
    ok("arrival reads whole", json.loads(body["result"]["content"][0]["text"])["mode"], "whole")
    code, body = rpc("tools/call", {"name": "play", "arguments": {"handle": "merchant"}})
    fr = json.loads(body["result"]["content"][0]["text"])
    ok("play returns the frame as data (side-effect-free read)", "window" in fr and fr["where"] == "1,1,2,1", True)
    code, body = rpc("tools/call", {"name": "play", "arguments": {}})
    ok("play without a handle is refused", body["result"]["isError"], True)
    code, body = rpc("nonsense/method")
    ok("unknown method refused", body["error"]["code"], -32601)
    code, body = rpc("tools/call", {"name": "hammer", "arguments": {}})
    ok("an unknown tool is refused", body["error"]["code"], -32602)

    print("the vapour relay (out-of-band, the server's own — 3.4)")
    code, body = http("/relay", {"frame": "taproom", "handle": "alice",
                                 "vapour": "I read the run before I raise", "face": "character"})
    ok("a heartbeat is accepted and returns the frame", body["frame"], "taproom")
    code, body = http("/relay", {"frame": "taproom", "handle": "bob", "vapour": "watching the hood"})
    ok("two are co-present at the frame", body["here"], 2)
    code, body = http("/relay?frame=taproom&handle=alice")
    ok("alice polls — sees bob, not herself", [p["handle"] for p in body["present"]], ["bob"])
    ok("and reads bob's live vapour", body["present"][0]["vapour"], "watching the hood")
    code, body = http("/relay?frame=cellar")
    ok("vapour is frame-scoped — the cellar is empty", body["here"], 0)
    code, body = http("/relay", {"frame": "taproom", "handle": "alice", "depart": True})
    ok("a clean departure is acknowledged", body["departed"], "alice")

    print("the human face (3.3, served at /xstream) — recipe-driven, not coded")
    with urllib.request.urlopen("http://127.0.0.1:%d/xstream" % PORT) as r:
        page, ctype = r.read().decode("utf-8"), r.headers.get("Content-Type", "")
    ok("/xstream serves html", ctype.startswith("text/html"), True)
    ok("the page is the shared VLS frame", all(z in page for z in ("vapour", "liquid", "solid")), True)
    ok("it rides the door + relay (no framework)",
       "/.well-known/biome-beach" in page and "/relay" in page, True)
    ok("the fold is read from a recipe block + spark, not coded",
       'readBlock("frame")' in page and "/spark.js" in page, True)
    with urllib.request.urlopen("http://127.0.0.1:%d/spark.js" % PORT) as r:
        sparkjs, jtype = r.read().decode("utf-8"), r.headers.get("Content-Type", "")
    ok("/spark.js serves the read-walk", jtype.startswith("text/javascript")
       and "export function spindle" in sparkjs and "export function ring" in sparkjs, True)

    print("the frame recipe — the fold as a door-legal block")
    RECIPE = {"0": "Frame — the fold recipe",
              "1": {"0": "registers", "1": {"0": "here · space", "1": "upperton-space"},
                    "2": {"0": "now · time", "1": "upperton-time"}},
              "2": "1,1,2,1", "3": "witness the table"}
    code, body = http("/.well-known/biome-beach", {"block": "frame", "content": RECIPE})
    ok("a frame recipe lands through the door", body.get("ok"), True)
    code, body = http("/.well-known/biome-beach?block=frame")
    ok("and reads back as registers + walk", (body["2"], body["1"]["1"]["1"]),
       ("1,1,2,1", "upperton-space"))

    print("liquid — a committed intention, door-legal and frame-scoped")
    code, body = http("/.well-known/biome-beach",
                      {"block": "liquid-alice",
                       "content": {"0": "alice — committed", "1": "1,1,2,1",
                                   "2": "I read the run before I stake"}})
    ok("a liquid commit lands through the door", body.get("ok"), True)
    code, body = http("/.well-known/biome-beach?block=liquid-alice")
    ok("and reads back, frame-scoped", (body["1"], body["2"]),
       ("1,1,2,1", "I read the run before I stake"))

    print("the hinge at the door (guest block-creation)")
    FOLD = {"0": "a guest block — landed whole", "1": "first branch"}
    code, body = rpc("tools/call", {"name": "spark",
                                    "arguments": {"block": "guest-block", "content": json.dumps(FOLD)}})
    ok("a stringified whole block unwraps and lands",
       json.loads(body["result"]["content"][0]["text"])["ok"], True)
    code, body = rpc("tools/call", {"name": "spark", "arguments": {"block": "guest-block", "number": "1", "attention": 0}})
    ok("and reads back through the geometry",
       json.loads(body["result"]["content"][0]["text"])["text"], "first branch")
    code, body = rpc("tools/call", {"name": "spark",
                                    "arguments": {"block": "absent-block", "number": "1", "attention": 0,
                                                  "content": "a point into nothing"}})
    res = body["result"]
    ok("a point-write into an absent block teaches instead of crashing",
       res.get("isError") and "whole-block write" in res["content"][0]["text"], True)

    print("the boundary at the door")
    import urllib.error
    try:
        http("/.well-known/pscale-beach?block=marks")
        ok("the old world's door is a signpost", "no error", "404")
    except urllib.error.HTTPError as e:
        note = json.loads(e.read().decode("utf-8"))
        ok("the old world's door is a signpost", (e.code, note["world"]), (404, "biome"))
    try:
        http("/.well-known/biome-beach",
             {"block": "marks", "number": "3", "attention": 0,
              "content": {"_": "an old-world shape"}})
        ok("the membrane refuses _ shapes", "accepted", "refused")
    except urllib.error.HTTPError as e:
        err = json.loads(e.read().decode("utf-8"))
        ok("the membrane refuses _ shapes", "beach-world shape refused" in err["error"], True)
    code, body = rpc("tools/call", {"name": "spark",
                                    "arguments": {"block": "marks", "number": "3", "attention": -1,
                                                  "content": {"_": "x", "1": "y"}}})
    ok("the membrane guards the mcp door too", body["result"]["isError"], True)
finally:
    httpd.shutdown()
    shutil.rmtree(root)

print()
print("TOTAL: %d passed, %d failed" % (P, F))
sys.exit(1 if F else 0)
