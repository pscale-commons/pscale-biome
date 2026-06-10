"""tezt_serve — regression battery for the commons surfaces.

Run:  python3 tezt_serve.py     (exits nonzero on any failure)

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


root = tempfile.mkdtemp(prefix="tezt-commons-")
store = FsStore(os.path.join(root, "blocks"))
store.save_block("biome", {"0": "biome — a tezt becoming", "1": "tezt · genome v1"})
sown = serve.seed(store)
serve.Commons.store = store
httpd = ThreadingHTTPServer(("127.0.0.1", 0), serve.Commons)
PORT = httpd.server_address[1]
threading.Thread(target=httpd.serve_forever, daemon=True).start()

try:
    print("seeding")
    ok("constitution + world sown", sorted(sown),
       ["arrive", "biome-shell", "flint", "genome", "marks", "slate", "thornkeep"])
    ok("a living store keeps its own", serve.seed(store), [])

    print("the beach surface (.well-known)")
    code, body = http("/")
    ok("the root is arrival", body["0"].startswith("Arrive"), True)
    code, body = http("/.well-known/pscale-beach?block=thornkeep")
    ok("whole block read", body["4"]["2"]["1"],
       "the taproom — long benches, a peat fire, the smell of wet wool")
    code, body = http("/.well-known/pscale-beach")
    ok("the surface lists its blocks", "thornkeep" in body["blocks"], True)
    code, body = http("/.well-known/pscale-beach",
                      {"block": "marks", "number": "1", "attention": 0,
                       "content": "first trace — tezt"})
    ok("a write lands", body["ok"], True)
    code, body = http("/.well-known/pscale-beach",
                      {"block": "marks", "number": "1", "attention": 0})
    ok("and reads back", body["text"], "first trace — tezt")

    print("the mcp surface")
    code, body = rpc("initialize", {"protocolVersion": "2025-03-26",
                                    "capabilities": {}, "clientInfo": {"name": "tezt"}})
    ok("initialize answers", body["result"]["serverInfo"]["name"], "biome-commons")
    code, body = http("/mcp", {"jsonrpc": "2.0", "method": "notifications/initialized"})
    ok("a notification is accepted", code, 202)
    code, body = rpc("tools/list")
    ok("one tool, named spark", [t["name"] for t in body["result"]["tools"]], ["spark"])
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
       ["first trace — tezt", "second trace — via mcp"])
    code, body = rpc("tools/call", {"name": "spark", "arguments": {"block": "arrive"}})
    ok("arrival reads whole", json.loads(body["result"]["content"][0]["text"])["mode"], "whole")
    code, body = rpc("nonsense/method")
    ok("unknown method refused", body["error"]["code"], -32601)
    code, body = rpc("tools/call", {"name": "hammer", "arguments": {}})
    ok("only spark is carried", body["error"]["code"], -32602)
finally:
    httpd.shutdown()
    shutil.rmtree(root)

print()
print("TOTAL: %d passed, %d failed" % (P, F))
sys.exit(1 if F else 0)
