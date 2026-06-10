"""serve — the commons surfaces: one spark behind two endpoints (shell 3.1 + 3.2).

The biome grown into its commons role. On boot it activates (if this store has
no becoming yet), seeds the constitution and the world from the carried genome,
then listens. Every surface calls the one spark — there is no second
implementation.

  GET  /                                      the arrive block (the root IS arrival)
  GET  /.well-known/pscale-beach?block=NAME   whole block, as JSON          (3.2)
  POST /.well-known/pscale-beach              {block, number, attention, content} write
  POST /mcp                                   MCP, streamable HTTP, one tool: spark  (3.1)

Run from a run-folder:  python3 biome/serve.py [port]     (default 3210, binds
127.0.0.1). On a platform host the env speaks: an injected PORT binds every
interface behind the platform's TLS edge; BIOME_ROOT names the durable volume.
Nursery semantics: reads free, writes open — curation is the owner's.
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spark"))
sys.path.insert(0, HERE)

import activate
import beach
import spark
from store_fs import FsStore

ZTONE = os.path.join(HERE, "..", "sentinel", "ztone")
SEEDS = [
    ("arrive", os.path.join(ZTONE, "arrive.json")),
    ("genome", os.path.join(ZTONE, "genome.json")),
    ("biome-shell", os.path.join(ZTONE, "biome.json")),
    ("slate", os.path.join(HERE, "..", "spark", "slate.json")),
    ("flint", os.path.join(HERE, "..", "spark", "flint.json")),
    ("thornkeep", os.path.join(HERE, "world", "thornkeep.json")),
]
MARKS = {"0": "Marks at this commons — each digit one guest's trace. Read at attention 0, choose the next free digit, append beside the others."}

TOOL = {
    "name": "spark",
    "description": (
        "The one function over this commons's 0-9 pscale blocks. Read when content is "
        "omitted; write when content is provided. The shape — point, ring, directory, "
        "disc, spindle, whole — derives from (number, attention) against the block's "
        "floor. FIRST CALL on arrival: spark(block='arrive') — reading it is your "
        "orientation; the blocks teach everything else."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "block": {"type": "string", "description": "Block name, e.g. arrive, slate, genome, thornkeep, marks."},
            "number": {"type": ["string", "null"], "description": "Pscale address — one decimal, pinned to the floor (e.g. '42.1'). Omit for disc/whole."},
            "attention": {"type": ["integer", "null"], "description": "Pscale integer — the scope. Omit with a number for the spindle; omit both for the whole block."},
            "content": {"description": "Payload for writes; omit to read."},
        },
        "required": ["block"],
    },
}


def seed(store):
    """Lay the carried blocks onto a fresh store; a living store keeps its own."""
    sown = []
    for name, path in SEEDS:
        if store.load_block(name) is None and os.path.isfile(path):
            store.save_block(name, spark.load(path))
            sown.append(name)
    if store.load_block("marks") is None:
        store.save_block("marks", dict(MARKS))
        sown.append("marks")
    return sown


def run_spark(store, args):
    block = args["block"]
    if "content" in args and args["content"] is not None:
        return beach.write(store, block, args.get("number"), args.get("attention"),
                           content=args["content"])
    return beach.read(store, block, args.get("number"), args.get("attention"), star=True)


class Commons(BaseHTTPRequestHandler):
    store = None
    server_version = "biome-commons/0.1"

    def _send(self, code, payload, ctype="application/json"):
        body = (json.dumps(payload, ensure_ascii=False, indent=1) if not isinstance(payload, (bytes, str))
                else payload)
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n).decode("utf-8")) if n else {}

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/":
            return self._send(200, self.store.load_block("arrive"))
        if url.path == "/.well-known/pscale-beach":
            name = (parse_qs(url.query).get("block") or [None])[0]
            if not name:
                return self._send(200, {"blocks": self.store.list_blocks()})
            block = self.store.load_block(name)
            return self._send(200, block) if block is not None \
                else self._send(404, {"absent": name})
        return self._send(404, {"absent": url.path})

    def do_POST(self):
        url = urlparse(self.path)
        try:
            body = self._body()
        except ValueError:
            return self._send(400, {"error": "body was not JSON"})
        if url.path == "/.well-known/pscale-beach":
            if "block" not in body:
                return self._send(400, {"error": "a write names its block"})
            try:
                return self._send(200, run_spark(self.store, body))
            except Exception as e:
                return self._send(400, {"error": str(e)})
        if url.path == "/mcp":
            return self._mcp(body)
        return self._send(404, {"absent": url.path})

    # --- MCP (streamable HTTP, JSON responses) --------------------------------

    def _mcp(self, msg):
        rid, method = msg.get("id"), msg.get("method", "")
        if rid is None:                                   # a notification
            return self._send(202, "")
        if method == "initialize":
            return self._rpc(rid, {
                "protocolVersion": msg.get("params", {}).get("protocolVersion", "2025-03-26"),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "biome-commons", "version": "0.1"},
            })
        if method == "ping":
            return self._rpc(rid, {})
        if method == "tools/list":
            return self._rpc(rid, {"tools": [TOOL]})
        if method == "tools/call":
            params = msg.get("params", {})
            if params.get("name") != "spark":
                return self._rpc_err(rid, -32602, "the commons carries one tool: spark")
            try:
                res = run_spark(self.store, params.get("arguments", {}))
                text = json.dumps(res, ensure_ascii=False, indent=1)
                return self._rpc(rid, {"content": [{"type": "text", "text": text}]})
            except Exception as e:
                return self._rpc(rid, {"content": [{"type": "text", "text": str(e)}],
                                       "isError": True})
        return self._rpc_err(rid, -32601, "method not found: %s" % method)

    def _rpc(self, rid, result):
        self._send(200, {"jsonrpc": "2.0", "id": rid, "result": result})

    def _rpc_err(self, rid, code, message):
        self._send(200, {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message}})

    def log_message(self, fmt, *args):
        sys.stderr.write("commons: %s\n" % (fmt % args))


def host_conditions():
    """Platform hosts speak through env: an injected PORT means a public face
    (bind every interface — the platform's edge terminates TLS); BIOME_ROOT
    names the durable surface (a mounted volume). Bare hosts default to the
    loopback and the working directory."""
    port = os.environ.get("PORT")
    return ("0.0.0.0" if port else "127.0.0.1",
            int(port or 3210),
            os.environ.get("BIOME_ROOT") or os.getcwd())


def main(root=None, port=None, host=None):
    eh, ep, eroot = host_conditions()
    root, port, host = root or eroot, int(port or ep), host or eh
    store = FsStore(os.path.join(root, "blocks"))
    if store.load_block("biome") is None:                 # no becoming yet — unfold first
        report, store = activate.activate(root)
        print("activated: intention %s" % report["intention"]["role"])
    sown = seed(store)
    if sown:
        print("seeded:", ", ".join(sown))
    Commons.store = store
    httpd = ThreadingHTTPServer((host, port), Commons)
    print("commons serving at http://%s:%d  (beach: /.well-known/pscale-beach · mcp: /mcp)" % (host, port))
    print("blocks:", ", ".join(store.list_blocks()))
    httpd.serve_forever()


if __name__ == "__main__":
    main(port=sys.argv[1] if len(sys.argv) > 1 else None)
