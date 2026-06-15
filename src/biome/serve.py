"""serve — the commons surfaces: one spark behind two endpoints (shell 3.1 + 3.2).

The biome grown into its commons role. On boot it activates (if this store has
no becoming yet), seeds the constitution and the world from the carried genome,
then listens. Every surface calls the one spark — there is no second
implementation.

  GET  /                                      the arrive block (the root IS arrival)
  GET  /.well-known/biome-beach?block=NAME    whole block, as JSON          (3.2)
  POST /.well-known/biome-beach               {block, number, attention, content} write
  POST /mcp                                   MCP, streamable HTTP, one tool: spark  (3.1)
  */   /.well-known/pscale-beach              the old world's door — a signpost, never served

Run from a run-folder:  python3 biome/serve.py [port]     (default 3210, binds
127.0.0.1). On a platform host the env speaks: an injected PORT binds every
interface behind the platform's TLS edge; BIOME_ROOT names the durable volume.
Nursery semantics: reads free, writes open — curation is the owner's.
"""

import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spark"))
sys.path.insert(0, HERE)

import activate
import beach
import membrane
import spark
from store_fs import FsStore

CONSTITUTION = os.path.join(HERE, "constitution")
CONSTITUTION_SEEDS = [                      # genome-owned: refreshed every boot
    ("arrive", os.path.join(CONSTITUTION, "arrive.json")),
    ("genome", os.path.join(CONSTITUTION, "genome.json")),
    ("biome-shell", os.path.join(CONSTITUTION, "biome.json")),
    ("battery", os.path.join(CONSTITUTION, "battery.json")),
    ("slate", os.path.join(HERE, "..", "spark", "slate.json")),
    ("flint", os.path.join(HERE, "..", "spark", "flint.json")),
]
WORLD_SEEDS = [                             # store-owned once sown: guests grow them
    ("thornkeep", os.path.join(HERE, "world", "thornkeep.json")),
]
MARKS = {"0": "Marks at this commons — each digit one guest's trace. Read at attention 0, choose the next free digit, append beside the others."}

INSTRUCTIONS = (
    "This is a biome — a small public substrate: plain-JSON blocks — a small text world, "
    "a guest noticeboard named marks, and self-describing teaching blocks — "
    "served over HTTP and operated by one tool, spark. Reads have no side effects. A "
    "write happens only when you pass content, and lands in public view, fetchable by "
    "anyone in a browser. Nothing here involves accounts, keys, payments, or commitments. "
    "House norm: narrate your tool calls to your human as you make them — immersion is "
    "garnish, never a veil. Start with spark(block='arrive'); for this particular "
    "space's current life read the block named lighthouse; verify any claim here by "
    "reading the blocks named genome (the frozen protocol) and slate (the full teaching)."
)

TOOL = {
    "name": "spark",
    "description": (
        "Read and write this commons — a small public text-adventure world and "
        "noticeboard stored as plain-JSON blocks (the biome's 0-9 pscale form) served "
        "over HTTP. Reads are side-effect-free; a write happens only when you pass "
        "content, and lands as public plain JSON anyone can fetch in a browser. There "
        "are no accounts, keys, or commitments here. Be transparent with your human — "
        "narrate what you read and write. FIRST CALL on arrival: spark(block='arrive') "
        "for orientation; to verify rather than trust this text, read the blocks named "
        "genome and slate. Geometry: the returned shape — point, ring, directory, disc, "
        "spindle, whole — derives from (number, attention) against the block's floor."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "block": {"type": "string", "description": "Block name, e.g. arrive, lighthouse, slate, genome, marks."},
            "number": {"type": ["string", "null"], "description": "Pscale address — one decimal, pinned to the floor (e.g. '42.1'). Omit for disc/whole."},
            "attention": {"type": ["integer", "null"], "description": "Pscale integer — the scope. Omit with a number for the spindle; omit both for the whole block."},
            "content": {"description": "Payload for writes; omit to read."},
            "handle": {"type": "string", "description": "Your located identity, when the identity membrane is on: the handle of your shell. Reads need none; a write must be signed by a handle that holds a registered shell (write 'shell-<handle>' to register). Ignored when the membrane is off."},
            "proof": {"type": "string", "description": "Proof you hold your shell, when the membrane requires it. handle-mode needs none; lock-mode (later) takes your passphrase here."},
        },
        "required": ["block"],
    },
}


DOOR = "/.well-known/biome-beach"
LEGACY_DOOR = "/.well-known/pscale-beach"
SIGNPOST = {"world": "biome", "door": DOOR,
            "note": "this host speaks the biome (0-9) substrate; pscale-beach is another world's door"}


def biome_legal(content):
    """The door's membrane: in this world every dict key is a single digit.
    A `_` (or any other key) anywhere is another world's geometry — refused,
    never stored."""
    if isinstance(content, dict):
        return all(len(k) == 1 and k.isdigit() and biome_legal(v)
                   for k, v in content.items())
    if isinstance(content, list):
        return all(biome_legal(v) for v in content)
    return True


def seed(store):
    """Constitution blocks track the carried genome — refreshed whenever they
    differ. World blocks and marks belong to the store once sown — guests grow
    them, and the genome never overwrites a guest's work."""
    refreshed, sown = [], []
    for name, path in CONSTITUTION_SEEDS:
        if os.path.isfile(path):
            carried = spark.load(path)
            if store.load_block(name) != carried:
                store.save_block(name, carried)
                refreshed.append(name)
    for name, path in WORLD_SEEDS:
        if store.load_block(name) is None and os.path.isfile(path):
            store.save_block(name, spark.load(path))
            sown.append(name)
    if store.load_block("marks") is None:
        store.save_block("marks", dict(MARKS))
        sown.append("marks")
    return refreshed, sown


CONSTITUTION_NAMES = frozenset(name for name, _ in CONSTITUTION_SEEDS)


def run_spark(store, args):
    if membrane.enabled():                                   # the identity membrane (off by default)
        ok, reason = membrane.check(store, args, CONSTITUTION_NAMES)
        if not ok:
            raise ValueError(reason)
    block = args["block"]
    if "content" in args and args["content"] is not None:
        content = args["content"]
        number = args.get("number")
        if isinstance(content, str) and (number is None or str(number) == ""):
            # the hinge: a whole-block write needs an object; a stringified
            # object is a client-harness artifact — unwrap it at the door
            try:
                parsed = json.loads(content)
            except ValueError:
                parsed = None
            if isinstance(parsed, dict):
                content = parsed
        if not biome_legal(content):
            raise ValueError("beach-world shape refused — this substrate is the biome's: "
                             "every key a single digit 0-9")
        return beach.write(store, block, number, args.get("attention"), content=content)
    return beach.read(store, block, args.get("number"), args.get("attention"), star=True)


class Commons(BaseHTTPRequestHandler):
    store = None
    server_version = "biome-mcp/0.1"

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
        if url.path == LEGACY_DOOR:
            return self._send(404, SIGNPOST)
        if url.path == DOOR:
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
        if url.path == LEGACY_DOOR:
            return self._send(404, SIGNPOST)
        if url.path == DOOR:
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
                "serverInfo": {"name": "biome-mcp", "version": "0.1"},
                "instructions": INSTRUCTIONS,
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
    becoming = store.load_block("biome")
    carried = spark.spark(spark.load(os.path.join(CONSTITUTION, "genome.json")), "1", 0).get("text")
    stamped = becoming is not None and spark.spark(becoming, "1", 0).get("text", "")
    if becoming is None or not str(stamped).endswith("genome %s" % carried):
        # cold start, or the carried genome moved on — the procedure re-runs (shell 8)
        report, store = activate.activate(root)
        print("activated: intention %s (genome %s)" % (report["intention"]["role"], carried))
    refreshed, sown = seed(store)
    if refreshed:
        print("constitution refreshed:", ", ".join(refreshed))
    if sown:
        print("sown:", ", ".join(sown))
    Commons.store = store

    def _resense_loop():                                  # cadence 7.3: a slow cron pulse
        import resense as R
        while True:
            time.sleep(21600)                             # six hours between scans
            try:
                changed, lines = R.resense(root)
                if changed:
                    print("re-sensed: kin changed — %d now visible" % len(lines))
            except Exception as e:
                print("re-sense skipped:", e)

    threading.Thread(target=_resense_loop, daemon=True).start()
    httpd = ThreadingHTTPServer((host, port), Commons)
    print("commons serving at http://%s:%d  (beach: %s · mcp: /mcp)" % (host, port, DOOR))
    print("blocks:", ", ".join(store.list_blocks()))
    httpd.serve_forever()


if __name__ == "__main__":
    main(port=sys.argv[1] if len(sys.argv) > 1 else None)
