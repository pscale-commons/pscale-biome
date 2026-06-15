"""web.py -- the RPG bench's local web interface: play a character in a browser.

The seed of the biome's xstream face, scoped to one run. Serves a page that
renders your character's bound frame (HERE / NOW / WHO / SELF) and a box for your
intention -- you ARE the soft tier. On submit it runs the turn: the other
characters act (soft-LLM), the medium gates what each act earns (writing reveals
into the shells), the hard arbitrates the collision; then it shows you the scene
and your refreshed frame. Served from the experiment leg (a run dir), NEVER the
public commons -- the same grown-not-placed discipline.

  python3 web.py [run_dir] [port]        # run_dir default ., port default 3220
  RPG_HARD=claude-sonnet-4-6 python3 web.py .   # cheap arbiter
  open http://127.0.0.1:3220
"""
import os, sys, json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import frame, tiers, play
sp = frame.spark

RUN_DIR = os.path.abspath(os.environ.get("RPG_RUN") or _HERE)
CAST = os.environ.get("RPG_CAST", "merchant,watcher").split(",")
YOU = os.environ.get("RPG_YOU", CAST[0])


def state(char):
    world = frame.load_world(os.path.join(RUN_DIR, "world"))
    shell = frame.load_shell(os.path.join(RUN_DIR, "characters", char))
    cond = sp.load(os.path.join(RUN_DIR, "characters", char, "conditions.json"))
    lived = play.perceived_recent(RUN_DIR, char, n=99)   # the character's OWN lived history (its view)
    window = frame.bind_window(shell, world, recent=play.perceived_recent(RUN_DIR, char))["text"]
    return {"char": char, "window": window,
            "conditions": [cond[k] for k in sorted(cond) if k != "0"], "scenes": lived}


def run_turn(human_char, intention):
    world = frame.load_world(os.path.join(RUN_DIR, "world"))
    shells = {nm: frame.load_shell(os.path.join(RUN_DIR, "characters", nm)) for nm in CAST}
    here = frame.here_walk(shells[human_char])
    # SOFT (act): you typed yours; each AI character acts from ONLY its own perceived window
    acts = []
    for nm in CAST:
        if nm == human_char:
            act = intention
        else:
            w = frame.bind_window(shells[nm], world, recent=play.perceived_recent(RUN_DIR, nm))
            _, act = tiers.soft_act(w["text"], nm)
        acts.append((nm, act))
    # MEDIUM: resolve the world-truth (omniscient, shown to no player)
    res = tiers.medium_resolve(acts, play.full_field(world, here, play.recent_scenes(RUN_DIR)))
    play.persist_scene(RUN_DIR, res["truth"])                  # HARD (admin): record + advance
    # SOFT (render): each character perceives only its own slice; you read yours
    you_see = ""
    for nm, act in acts:
        r = tiers.soft_render(nm, frame.standpoint(shells[nm], world), act, res["truth"])
        play.append_perceived(RUN_DIR, nm, r["render"])
        if r["perceived"]:
            play.persist_to_conditions(RUN_DIR, nm, "[perceived] " + r["perceived"])
        if nm == human_char:
            you_see = r["render"]
    return {"render": you_see, "state": state(human_char)}


class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/":
            with open(os.path.join(_HERE, "play.html"), encoding="utf-8") as f:
                return self._send(200, f.read(), "text/html; charset=utf-8")
        if u.path == "/state":
            return self._send(200, json.dumps(state(parse_qs(u.query).get("char", [YOU])[0])))
        return self._send(404, json.dumps({"absent": u.path}))

    def do_POST(self):
        if urlparse(self.path).path == "/act":
            n = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(n) or b"{}")
            intent = (body.get("intention") or "").strip()
            if not intent:
                return self._send(400, json.dumps({"error": "type an intention"}))
            return self._send(200, json.dumps(run_turn(body.get("char", YOU), intent)))
        return self._send(404, json.dumps({"absent": self.path}))

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    if len(sys.argv) > 1:
        RUN_DIR = os.path.abspath(sys.argv[1])
    port = int(sys.argv[2]) if len(sys.argv) > 2 else int(os.environ.get("RPG_PORT", "3220"))
    print("RPG face at http://127.0.0.1:%d   (you are the %s; run: %s)" % (port, YOU, RUN_DIR))
    HTTPServer(("127.0.0.1", port), H).serve_forever()
