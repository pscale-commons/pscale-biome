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
    scenes = []
    sc = os.path.join(RUN_DIR, "scenes.json")
    if os.path.exists(sc):
        sb = sp.load(sc)
        scenes = [sb[k] for k in sorted(sb) if k != "0" and isinstance(sb[k], str)]
    window = frame.bind_window(shell, world, recent=play.recent_scenes(RUN_DIR))["text"]
    return {"char": char, "window": window,
            "conditions": [cond[k] for k in sorted(cond) if k != "0"], "scenes": scenes}


def run_turn(human_char, intention):
    world = frame.load_world(os.path.join(RUN_DIR, "world"))
    shells = {nm: frame.load_shell(os.path.join(RUN_DIR, "characters", nm)) for nm in CAST}
    here = frame.here_walk(shells[human_char])
    recent = play.recent_scenes(RUN_DIR)
    acts, log, you_learn = [], [], ""
    for nm in CAST:
        if nm == human_char:
            voice, act = "(you)", intention
        else:
            voice, act = tiers.soft_voice(frame.bind_window(shells[nm], world, recent=recent)["text"], nm)
        hid = frame.hidden_depth(shells[nm], world)
        g = tiers.medium_gate(nm, act, "\n".join("- " + x for x in hid["whos"]))
        if g["reveal"] and g["writeback"] and g["writeback"].lower() != "none":
            play.persist_to_conditions(RUN_DIR, nm, "[earned] " + g["writeback"] + " (%s)" % (g["certainty"] or "?"))
            if nm == human_char:
                you_learn = g["knowledge"]
        acts.append((nm, act))
        log.append({"who": nm, "voice": voice})
    arb = tiers.hard_arbitrate(acts, play.full_field(world, here, recent))
    play.persist_scene(RUN_DIR, arb["scene"] or arb["raw"])
    for nm, _ in acts:
        gg = arb["gains"].get(nm, "")
        if gg and gg.lower() != "none":
            play.persist_to_conditions(RUN_DIR, nm, "[outcome] " + gg)
    return {"scene": arb["scene"] or arb["raw"], "prevailed": arb["prevailed"],
            "you_learn": you_learn, "you_gain": arb["gains"].get(human_char, ""), "state": state(human_char)}


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
