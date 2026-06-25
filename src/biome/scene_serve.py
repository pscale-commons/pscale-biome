"""scene_serve -- Track B multiplayer server (stdlib http.server). Reuses scene.py.

Each character is a SEAT, controlled one of three ways (explicit, set at startup):
  human  (env SCENE_HUMANS) -- a browser at /play?who=<seat>, submits via POST /submit
  agent  (env SCENE_AGENTS) -- driven over the HTTP API by an LLM player (me), same POST
  nhitl  (the rest)         -- the server perceives + submits for it, autonomously

A BEAT: window opens -> nhitl seats auto-submit (a bg thread) -> human/agent seats POST ->
when ALL seats have submitted -> resolve (mechanical designer rule) -> echoes per seat ->
clients show their echo and POST /next -> the next beat opens.

Outcome shared (the mechanical verdict); perception + echo personal (per seat). Nothing is
computed centrally but the verdict. Authority gating is deferred (writes open). This is a
SEPARATE Track-B surface -- it does NOT touch Track A's serve.py / interface.html.

  python3 scene_serve.py [port]            # default 3221, binds 0.0.0.0 (LAN-reachable)
  SCENE_HUMANS=merchant,keeper SCENE_AGENTS=watcher python3 scene_serve.py
"""
import json
import os
import sys
import threading
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scene

STORE = scene.STORE_DEFAULT
WHERE = scene._where(scene.TAPROOM)
SEATS = ["merchant", "watcher", "keeper", "regular"]
PAGE = os.path.join(HERE, "scene.html")

HUMANS = set(filter(None, os.environ.get("SCENE_HUMANS", "merchant,keeper").split(",")))
AGENTS = set(filter(None, os.environ.get("SCENE_AGENTS", "watcher").split(",")))
NHITL = [h for h in SEATS if h not in HUMANS and h not in AGENTS]

LOCK = threading.RLock()
STATE = {"beat": 1, "phase": "open", "sees": {}, "echoes": {}, "verdict": None, "filling": False}
CHARS = None


def submitted_set():
    return {h for h, _ in scene.submissions(STORE)}


def all_in():
    return all(h in submitted_set() for h in SEATS)


def fill_nhitl():
    """Autonomously perceive + submit for every NHITL seat this beat (LLM, off-lock)."""
    with LOCK:
        if STATE["filling"]:
            return
        STATE["filling"] = True
    try:
        for h in NHITL:
            with LOCK:
                done = STATE["phase"] != "open" or h in submitted_set()
            if done:
                continue
            try:
                exp = scene.perceive(STORE, WHERE, h, CHARS[h])
                scene.submit(STORE, WHERE, h, CHARS[h], exp)
            except Exception as e:
                print("nhitl %s error: %s" % (h, e))
        maybe_resolve()
    finally:
        with LOCK:
            STATE["filling"] = False


def maybe_resolve():
    """When every seat has submitted, commit the mechanical verdict + echoes (once)."""
    with LOCK:
        if STATE["phase"] != "open" or not all_in():
            return
        STATE["phase"] = "resolving"
    verdict, _ = scene.resolve(STORE, WHERE, CHARS)
    echoes = {}
    for h in SEATS:
        try:
            echoes[h] = scene.echo(STORE, WHERE, h, CHARS[h], verdict)
        except Exception as e:
            echoes[h] = "(echo error: %s)" % e
    with LOCK:
        STATE.update(phase="resolved", verdict=verdict, echoes=echoes)


def open_beat():
    with LOCK:
        STATE.update(phase="open", sees={}, echoes={}, verdict=None)
    scene.clear_window(STORE)
    threading.Thread(target=fill_nhitl, daemon=True).start()


def sees_for(h):
    """Bespoke perception for a controlled seat; cached per beat so polls don't re-call the LLM."""
    with LOCK:
        if h in STATE["sees"]:
            return STATE["sees"][h]
    exp = scene.perceive(STORE, WHERE, h, CHARS[h])
    with LOCK:
        STATE["sees"].setdefault(h, exp)
        return STATE["sees"][h]


def do_submit(who, move):
    with LOCK:
        if STATE["phase"] != "open" or who in submitted_set() or who not in SEATS:
            return False
    scene.submit_write(STORE, who, move)
    maybe_resolve()
    return True


def do_next(beat):
    with LOCK:
        if STATE["phase"] != "resolved" or beat != STATE["beat"]:
            return False
        STATE["beat"] += 1
    open_beat()
    return True


def state_for(who):
    with LOCK:
        sub = submitted_set()
        out = {"beat": STATE["beat"], "phase": STATE["phase"], "you": who,
               "seats": SEATS, "humans": sorted(HUMANS), "agents": sorted(AGENTS), "nhitl": NHITL,
               "submitted": sorted(sub), "waiting": [h for h in SEATS if h not in sub],
               "your_submitted": who in sub,
               "verdict": STATE["verdict"], "your_echo": STATE["echoes"].get(who)}
    if out["phase"] == "open" and who in SEATS and not out["your_submitted"]:
        out["sees"] = sees_for(who)        # may block ~5s on first poll (LLM), then cached
    return out


class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        b = body.encode("utf-8") if isinstance(body, str) else json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def log_message(self, *a):
        pass

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path in ("/", "/play"):
            try:
                with open(PAGE, encoding="utf-8") as f:
                    return self._send(200, f.read(), "text/html; charset=utf-8")
            except OSError:
                return self._send(404, {"absent": "scene.html"})
        if u.path == "/state":
            return self._send(200, state_for((q.get("who") or [""])[0]))
        if u.path == "/sees":
            return self._send(200, {"sees": sees_for((q.get("who") or [""])[0])})
        if u.path == "/scene":
            return self._send(200, scene._b(STORE, "scene") or {})
        return self._send(404, {"absent": u.path})

    def do_POST(self):
        u = urlparse(self.path)
        n = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return self._send(400, {"error": "bad json"})
        if u.path == "/submit":
            ok = do_submit(body.get("who", ""), (body.get("move") or "").strip())
            return self._send(200 if ok else 409, {"ok": ok})
        if u.path == "/next":
            return self._send(200, {"ok": do_next(int(body.get("beat", -1)))})
        return self._send(404, {"absent": u.path})


def main():
    global CHARS
    port = int(sys.argv[1]) if sys.argv[1:] else int(os.environ.get("PORT", 3221))
    if not os.path.isdir(STORE) or not os.path.isfile(os.path.join(STORE, "upperton-spatial.json")):
        scene.seed(store=STORE)
    CHARS = scene.load_chars(STORE)
    open_beat()
    print("scene_serve on 0.0.0.0:%d  store=%s" % (port, STORE))
    print("  seats: humans=%s  agents=%s  nhitl=%s" % (sorted(HUMANS), sorted(AGENTS), NHITL))
    print("  play:  http://<this-host>:%d/play?who=<seat>" % port)
    ThreadingHTTPServer(("0.0.0.0", port), H).serve_forever()


if __name__ == "__main__":
    main()
