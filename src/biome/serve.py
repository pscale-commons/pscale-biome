"""serve — the commons surfaces: one spark behind two endpoints (shell 3.1 + 3.2).

The biome grown into its commons role. On boot it activates (if this store has
no becoming yet), seeds the constitution and the world from the carried genome,
then listens. Every surface calls the one spark — there is no second
implementation.

  GET  /                                      the arrive block (the root IS arrival)
  GET  /.well-known/biome-beach?block=NAME    whole block, as JSON          (3.2)
  POST /.well-known/biome-beach               {block, number, attention, content} write
  POST /mcp                                   MCP, streamable HTTP, one tool: spark  (3.1)
  GET  /relay?frame=F&handle=H                live presence + vapour at a frame       (3.4)
  POST /relay                                 {frame, handle, vapour, face} heartbeat (3.4)
  GET  /xstream                               the human interface — a shared VLS frame (3.3)
  GET  /spark.js                              the read-walk the face imports
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
import discover
import federate
import fold
import located
import meet
import membrane
import play
import rules
import spark
from relay import Relay
from store_fs import FsStore

CONSTITUTION = os.path.join(HERE, "constitution")
INTERFACE = os.path.join(HERE, "interface.html")  # the human interface (3.3), served at /xstream
SPARK_JS = os.path.join(HERE, "spark.js")       # the read-walk the face imports (the browser spark)
WORLD = os.path.join(HERE, "world.html")         # the spatial walker — descend a place-block from a root
CONSTITUTION_SEEDS = [                      # genome-owned: refreshed every boot
    ("arrive", os.path.join(CONSTITUTION, "arrive.json")),
    ("genome", os.path.join(CONSTITUTION, "genome.json")),
    ("biome-shell", os.path.join(CONSTITUTION, "biome.json")),
    ("battery", os.path.join(CONSTITUTION, "battery.json")),
    ("reflective-compass", os.path.join(CONSTITUTION, "reflective-compass.json")),
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

PLAY_TOOL = {
    "name": "play",
    "description": (
        "Play a turn in a text RPG hosted here as plain-JSON pscale blocks (the world "
        "Upperton — a dice-game at the Millstone taproom). ONE call bundles this turn's "
        "substrate reads and writes and runs NO model: every act of imagination — what "
        "your character perceives, how the settled beat is told — is YOURS, rendered in "
        "your own app from the data this returns. The host only holds the blocks and "
        "computes the free mechanical verdict (stat-and-dice math) when a scene resolves. "
        "Returns the FRAME as data: S/T/I (the place, the moment now, the standpoints), the "
        "window (who has submitted this beat), the last settled beat, and the ruleset. "
        "Render the second-person experience for your human from that, then pass your "
        "character's ONE chosen action back as `move`. A call with no move/account/place is "
        "a side-effect-free read. Be transparent — narrate your calls to your human."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "handle": {"type": "string", "description": "Your seat — the character you inhabit (e.g. merchant, watcher, keeper, regular)."},
            "world": {"type": "string", "description": "The cosmology to play in. Currently 'upperton' (the only world seeded here); selects its S/T/I blocks."},
            "where": {"type": ["string", "null"], "description": "The scene address as a pscale walk (e.g. '1121' for the taproom). Omit to use your located standing."},
            "move": {"type": ["string", "null"], "description": "Your character's ONE intention this beat, first person ('I ...'). Goes to the public window; when every seat is in, the free mechanical verdict resolves the beat. Omit to read without acting."},
            "account": {"type": ["string", "null"], "description": "Your app's rendition of the PRIOR turn (the echo you showed your human) — appended to your character's own lossless history. Omit on the first turn."},
            "place": {"type": ["string", "null"], "description": "Your character's own rendition of this place (face=character → your version), or with face=author the woven canonical voicing. Optional; builds the lived-in world."},
            "rules": {"type": ["string", "null"], "description": "The ruleset block. Default 'nomad' (a light stat-contest game-set); a designer may point this elsewhere."},
            "face": {"type": ["string", "null"], "description": "Your aperture: character (default) / author / designer / observer. Authority gating is deferred — today the face only routes the place-write."},
        },
        "required": ["handle"],
    },
}

MEET_TOOL = {
    "name": "meet",
    "description": (
        "Reach toward another agency and form a GRAIN — a direct handshake between two "
        "handles, with NO shared world behind it. This is the lens pointed not at a "
        "substrate but at another mind: you post your `reach` (what you offer or say this "
        "turn) and read theirs back; when both sides have reached, the grain is FORMED. It "
        "lives only in the meeting (an ephemeral channel) — never written to any beach, "
        "never persisted; it evaporates when either of you leaves. The other party must "
        "also call meet (naming you) for the handshake to form. Runs NO model and touches "
        "no storage — you bring the meaning. To KEEP what you agreed, write it into your "
        "own shell with spark, deliberately. Be transparent — narrate your calls."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "handle": {"type": "string", "description": "Who you are — your handle."},
            "with": {"type": "string", "description": "Who you are reaching toward — their handle. They must meet you back for the grain to form."},
            "reach": {"type": ["string", "null"], "description": "Your offering this turn — what you say, propose, or hold out to the other. Omit to ping presence without words."},
            "face": {"type": ["string", "null"], "description": "Your aperture in the meeting (character / author / designer / observer). Default character."},
        },
        "required": ["handle", "with"],
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


def run_play(store, args):
    """The RPG primitive `play`, over the store the biome holds — pure compilation
    over spark, NO model. Perception, echo, and the place-weave are the visiting
    app's cognition (cognition current 2.1, external via MCP, on endpoint 3.1); the
    engine returns the frame as DATA and runs only the free mechanical verdict.
    play's own writes are open here — the identity membrane gates the spark door,
    not play; authority for play is deferred to the passphrase membrane."""
    handle = args.get("handle")
    if not handle:
        raise ValueError("play needs a handle — the seat you inhabit (e.g. 'merchant')")
    return play.play(store, handle,
                     world=args.get("world") or "upperton",
                     where=args.get("where"),
                     move=args.get("move"),
                     account=args.get("account"),
                     place=args.get("place"),
                     rules=args.get("rules") or "nomad",
                     face=args.get("face") or "character")


def run_meet(relay, args):
    """The handshake lens `meet` -- the interface form run OBJECT-LESS: two agencies
    reach across the vapour relay (endpoints 3.4) and a grain forms in the overlap,
    held in the meeting, never on a beach, never persisted. No model, no store.
    Cognition 2.1 (external) x concurrency 5.3 (co-present minds) x relay 3.4 x grain."""
    return meet.meet(relay, args.get("handle"), args.get("with"),
                     reach=args.get("reach"), face=args.get("face") or "character")


class Commons(BaseHTTPRequestHandler):
    store = None
    relay = Relay()                          # the server's own vapour relay (3.4) — ephemeral, out-of-band
    server_version = "biome-mcp/0.1"

    def _send(self, code, payload, ctype="application/json"):
        body = (json.dumps(payload, ensure_ascii=False, indent=1) if not isinstance(payload, (bytes, str))
                else payload)
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")   # a public substrate: any page may read it
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):                                       # CORS preflight (cross-origin writes)
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n).decode("utf-8")) if n else {}

    def _base(self):                                     # the public URL a caller reached us on
        host = self.headers.get("Host", "")
        proto = self.headers.get("X-Forwarded-Proto", "http")
        return ("%s://%s" % (proto, host)) if host else ""

    def _roots(self):                                    # the cosmology root(s) this biome indexes
        """Sense which world(s) this biome's resolver indexes, from its OWN store: a
        `roots` block (plain-name leaves) if the biome declares one, else the spine's
        root when this biome actually carries that block, else none. So discovery is a
        generic unfolding -- a biome resolves whatever world it holds, not the real
        world by default. The (3,6) relation axis of the constitution, made conditional."""
        rb = self.store.load_block("roots")
        if isinstance(rb, dict):
            named = [rb[d] for d in spark.DIGITS if isinstance(rb.get(d), str)]
            present = [n for n in named if self.store.load_block(n) is not None]
            if present:
                return present
        return [rules.ROOT] if self.store.load_block(rules.ROOT) is not None else []

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/":
            return self._send(200, self.store.load_block("arrive"))
        if url.path == "/xstream":
            try:
                with open(INTERFACE, encoding="utf-8") as f:
                    return self._send(200, f.read(), "text/html; charset=utf-8")
            except OSError:
                return self._send(404, {"absent": "/xstream"})
        if url.path == "/spark.js":
            try:
                with open(SPARK_JS, encoding="utf-8") as f:
                    return self._send(200, f.read(), "text/javascript; charset=utf-8")
            except OSError:
                return self._send(404, {"absent": "/spark.js"})
        if url.path == "/world":                          # the spatial walker (3.3, spatial form)
            try:
                with open(WORLD, encoding="utf-8") as f:
                    return self._send(200, f.read(), "text/html; charset=utf-8")
            except OSError:
                return self._send(404, {"absent": "/world"})
        if url.path == LEGACY_DOOR:
            return self._send(404, SIGNPOST)
        if url.path == "/relay":
            q = parse_qs(url.query)
            frame = (q.get("frame") or [""])[0]
            handle = (q.get("handle") or [None])[0]
            return self._send(200, self.relay.view(frame, exclude=handle))
        if url.path == DOOR:
            name = (parse_qs(url.query).get("block") or [None])[0]
            if not name:
                return self._send(200, {"blocks": self.store.list_blocks()})
            block = self.store.load_block(name)
            return self._send(200, block) if block is not None \
                else self._send(404, {"absent": name})
        if url.path == "/gazetteer":                     # discovery: the whole name -> URL index (derived)
            return self._send(200, discover.index(federate.loader(self.store), self._roots(), base=self._base()))
        if url.path == "/resolve":                       # discovery: name -> the URL(s) to fetch it
            q = parse_qs(url.query)
            nm = (q.get("name") or [None])[0]
            if not nm:
                return self._send(400, {"error": "name required, e.g. /resolve?name=Sheffield"})
            matches = discover.resolve(federate.loader(self.store), nm, self._roots(), base=self._base())
            # DNS-style delegation: on the user's query (delegate != 0) also ask peers'
            # own resolvers, non-recursively (they answer &delegate=0 -- no loop), and
            # merge. Each island stays authoritative for its own names.
            if (q.get("delegate") or ["1"])[0] != "0":
                seen = {(m.get("url"), m.get("walk")) for m in matches}
                for m in federate.resolve_peers(nm):
                    key = (m.get("url"), m.get("walk"))
                    if key not in seen:
                        seen.add(key)
                        matches.append(m)
            return self._send(200, {"name": nm, "matches": matches})
        if url.path == "/frame":                         # engagement: stand at where/when/who -> the S*T*I moment
            q = parse_qs(url.query)
            where = (q.get("where") or [None])[0]
            roots = self._roots()
            if not where:
                return self._send(400, {"error": "where required, e.g. /frame?where=Ceidio&who=david"})
            if not roots:
                return self._send(404, {"absent": "this biome carries no world to stand in"})
            try:                                          # synth=False: return the bind PROMPT, no server-side LLM
                fr = fold.frame(where, (q.get("when") or ["now"])[0], (q.get("who") or [""])[0],
                                earth_loader=federate.loader(self.store), root=roots[0], synth=False)
            except ValueError as e:
                return self._send(404, {"error": str(e)})
            return self._send(200, fr)
        if url.path == "/social":                         # engagement: the I-fan folded -> the collective (1^9)
            q = parse_qs(url.query)
            where = (q.get("where") or [None])[0]
            roots = self._roots()
            if not where:
                return self._send(400, {"error": "where required, e.g. /social?where=Ceidio"})
            if not roots:
                return self._send(404, {"absent": "this biome carries no world"})
            mirror_only = (q.get("mirror") or ["0"])[0] not in ("0", "false", "")
            try:
                sf = fold.social_fold(where, mirror_only=mirror_only,
                                      earth_loader=federate.loader(self.store), root=roots[0], synth=False)
            except ValueError as e:
                return self._send(404, {"error": str(e)})
            return self._send(200, sf)
        return self._send(404, {"absent": url.path})

    def do_POST(self):
        url = urlparse(self.path)
        try:
            body = self._body()
        except ValueError:
            return self._send(400, {"error": "body was not JSON"})
        if url.path == LEGACY_DOOR:
            return self._send(404, SIGNPOST)
        if url.path == "/relay":
            handle = body.get("handle")
            if not handle:
                return self._send(400, {"error": "a vapour beat names its handle"})
            frame = body.get("frame", "")
            if body.get("depart"):
                self.relay.depart(frame, handle)
                return self._send(200, {"ok": True, "departed": handle})
            face = body.get("face", "observer")
            view = self.relay.beat(frame, handle, body.get("vapour", ""), face)
            try:                                              # persist the STANDING the beat carries
                roots = self._roots()                         # (handle/world/where/face); the vapour
                located.situate(self.store, handle,           # stays ephemeral. best-effort, idempotent
                                world=(body.get("world") or (roots[0] if roots else "")),  # (writes only
                                face=face, where=frame, present=frame,    # on change), never breaks the
                                island=self._base(), infra=self.headers.get("Host", ""))  # heartbeat. A
            except Exception:                                 # multi-world client names its world; else
                pass                                          # the island's root world is assumed.
            return self._send(200, view)
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
            return self._rpc(rid, {"tools": [TOOL, PLAY_TOOL, MEET_TOOL]})
        if method == "tools/call":
            params = msg.get("params", {})
            name, args = params.get("name"), params.get("arguments", {})
            try:
                if name == "spark":
                    res = run_spark(self.store, args)
                elif name == "play":
                    res = run_play(self.store, args)
                elif name == "meet":
                    res = run_meet(self.relay, args)         # the lens onto another agency -- no store
                else:
                    return self._rpc_err(rid, -32602,
                                         "unknown tool: %s (this commons carries spark, play, and meet)" % name)
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
