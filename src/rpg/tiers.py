"""tiers.py -- the three LLM roles (SMH) for the RPG bench.

  soft   voices a character's perceived moment and chooses an act
  medium gates what an act earns from the hidden depth (the negative-I reveal)
  hard   arbitrates a collision into one canonical scene

Key-loading and model tiers mirror src/agent/kernel.py. SMH maps to model size:
soft/medium small-and-fast, hard the most authoritative reading. Override any
with RPG_SOFT / RPG_MEDIUM / RPG_HARD env vars (e.g. RPG_HARD=claude-sonnet-4-6
to run the whole bench cheaply).
"""
import os, re, json, urllib.request, urllib.error

API_URL = "https://api.anthropic.com/v1/messages"


def _load_key():
    k = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if k:
        return k
    for p in (os.environ.get("MOBIUS_KEY_FILE", ""),
              os.path.expanduser("~/.config/mobius/anthropic-key"),
              os.path.expanduser("~/.mobius-key")):
        if p and os.path.exists(p):
            t = open(p, encoding="utf-8").read().strip()
            if t and not t.startswith("ANTHROPIC_API_KEY"):
                return t
            for line in t.splitlines():
                if line.startswith("ANTHROPIC_API_KEY") and "=" in line:
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


API_KEY = _load_key()
TIERS = {"soft": os.environ.get("RPG_SOFT", "claude-sonnet-4-6"),
         "medium": os.environ.get("RPG_MEDIUM", "claude-sonnet-4-6"),
         "hard": os.environ.get("RPG_HARD", "claude-opus-4-8")}


def call(model, prompt, max_tokens=750):
    if not API_KEY:
        return "[NO API KEY -- set ~/.config/mobius/anthropic-key]"
    body = json.dumps({"model": model, "max_tokens": max_tokens,
                       "messages": [{"role": "user", "content": prompt}]}).encode("utf-8")
    req = urllib.request.Request(API_URL, data=body, method="POST",
        headers={"content-type": "application/json", "x-api-key": API_KEY,
                 "anthropic-version": "2023-06-01"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.loads(r.read().decode("utf-8"))
        return "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text").strip()
    except urllib.error.HTTPError as e:
        return "[API ERROR %s] %s" % (e.code, e.read().decode("utf-8")[:300])


def _field(text, label):
    """Pull a 'LABEL: value' field, tolerant of markdown (**LABEL:**, leading -/#)."""
    up = label.upper() + ":"
    for line in text.splitlines():
        s = line.strip().lstrip("-*# ").strip()
        if s.upper().startswith(up):
            return s.split(":", 1)[1].strip().strip("*").strip()
    return ""


def _scene_field(out):
    """SCENE is multi-sentence; capture it whole, up to the next labelled field."""
    m = re.search(r"SCENE:\s*(.*?)(?=\n[^\n]*GAINS:|\nWHO PREVAILED:|\Z)", out, re.S)
    return m.group(1).strip().strip("*").strip() if m else _field(out, "SCENE")


def soft_voice(window_text, name):
    p = ("You ARE a character in a coordinate-addressed world: the %s. Below is your bound moment. "
"Speak ONLY from inside it -- you know only what is given here, and invent no facts beyond it.\n\n"
"Voice your perceived moment -- 2 to 4 sentences, first person, present tense.\n"
"Then on a new line: INTENTION: <one sentence -- what you do next>\n\n%s") % (name, window_text)
    out = call(TIERS["soft"], p)
    act = _field(out, "INTENTION") or (out.strip().splitlines()[-1] if out.strip() else "")
    return out, act


def medium_gate(name, act, hidden):
    p = ("You are the medium-LLM, arbiter of what a character comes to know. The newcomer character "
"(the %s) just acted with this intention:\n\n\"%s\"\n\n"
"He perceives only the public surface. Here is what he CANNOT see -- the private standpoints of others "
"present, and the true nature of things in reach:\n%s\n\n"
"RULE: a newcomer earns hidden knowledge ONLY through an act that actively investigates the relevant "
"thing. Default to NO reveal. If his act investigates, reveal only what an attentive newcomer could "
"plausibly infer, at a certainty no greater than the act earns -- proving takes more than noticing.\n\n"
"Respond EXACTLY:\nREVEAL: yes|no\nKNOWLEDGE: <what he now suspects, or none>\n"
"CERTAINTY: proven|suspected|hunch|none\nWRITE-BACK: <one line for his conditions, or none>\n"
"REASON: <one sentence>") % (name, act, hidden)
    out = call(TIERS["medium"], p)
    return {"raw": out, "reveal": _field(out, "REVEAL").lower().startswith("y"),
            "knowledge": _field(out, "KNOWLEDGE"), "certainty": _field(out, "CERTAINTY"),
            "writeback": _field(out, "WRITE-BACK"), "reason": _field(out, "REASON")}


def hard_arbitrate(acts, full_field):
    """acts: list of (name, act). Resolve the collision -> scene + per-character gains."""
    actlines = "\n".join('- THE %s acts: "%s"' % (n.upper(), a) for n, a in acts)
    gains_fmt = "\n".join("%s GAINS: <one line for their shell>" % n.upper() for n, _ in acts)
    p = ("You are the hard-LLM, the world's arbiter. These characters bind the SAME instant and act; the "
"more definite, better-grounded reading is the more authoritative where they conflict, and the warp "
"concentrates here where selves meet.\n\n%s\n\nThe full field (true beyond any one view):\n%s\n\n"
"Resolve what ACTUALLY happens. Respond EXACTLY:\n"
"SCENE: <3-4 sentences, the canonical moment, for the world's scene block>\n%s\n"
"WHO PREVAILED: <one phrase and why>") % (actlines, full_field, gains_fmt)
    out = call(TIERS["hard"], p, max_tokens=850)
    return {"raw": out, "scene": _scene_field(out),
            "gains": {n: _field(out, n.upper() + " GAINS") for n, _ in acts},
            "prevailed": _field(out, "WHO PREVAILED")}
