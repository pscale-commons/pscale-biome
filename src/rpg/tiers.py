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


def _long(out, label):
    """A multi-sentence field; capture it whole, up to the next labelled field."""
    m = re.search(label + r":\s*(.*?)(?=\n[^\n]*(?:OUTCOME|PERCEIVED|PREVAILED):|\Z)", out, re.S)
    return m.group(1).strip().strip("*").strip() if m else _field(out, label)


def soft_act(window_text, name):
    """SOFT (act side): an AI character perceives its OWN bound window -- only what
    it can perceive -- and chooses an act. The human plays this tier by typing."""
    p = ("You ARE a character in a coordinate-addressed world: the %s. Below is your bound moment -- only "
"what you perceive. Speak from inside it; invent no facts beyond it.\n\n"
"Voice your moment -- 2 to 4 sentences, first person, present.\n"
"Then a new line: INTENTION: <one sentence -- what you do next>\n\n%s") % (name, window_text)
    out = call(TIERS["soft"], p)
    return out, (_field(out, "INTENTION") or (out.strip().splitlines()[-1] if out.strip() else ""))


def medium_resolve(acts, full_field):
    """MEDIUM: knows more than any character. Resolves what ACTUALLY happens across
    the acts, given the full field they cannot each see. This is world-truth -- it is
    shown to NO player; each character perceives only their slice (soft_render)."""
    actlines = "\n".join('- the %s acts: "%s"' % (n, a) for n, a in acts)
    out_fmt = "\n".join("%s OUTCOME: <one line -- what materially happens to them>" % n.upper() for n, _ in acts)
    p = ("You are the medium-LLM. You know the full field these characters cannot each see, and you resolve "
"what ACTUALLY happens when they act at the same instant -- omniscient and concrete, the more grounded "
"reading authoritative where they conflict.\n\n%s\n\nThe full field (true beyond any one view):\n%s\n\n"
"Respond EXACTLY:\nTRUTH: <3-5 sentences, what actually happens, third-person omniscient -- world-truth, "
"shown to no player>\n%s\nWHO PREVAILED: <one phrase and why>") % (actlines, full_field, out_fmt)
    out = call(TIERS["medium"], p, max_tokens=850)
    return {"raw": out, "truth": _long(out, "TRUTH"),
            "outcomes": {n: _field(out, n.upper() + " OUTCOME") for n, _ in acts},
            "prevailed": _field(out, "WHO PREVAILED")}


def soft_render(name, standpoint, act, truth):
    """SOFT (render side): ONE character's second-person, perception-limited experience
    of the resolution -- what THIS character can see, hear, or feel, and nothing else.
    Omit any other character's hidden hand, an unnoticed theft, others' interiors."""
    p = ("You render the moment for ONE character to read AS THEMSELVES: the %s. Their standpoint:\n%s\n\n"
"They just acted: \"%s\"\n\nWhat ACTUALLY happened (the omniscient resolution -- most of it they CANNOT "
"perceive):\n%s\n\n"
"Write what THIS character perceives of it, addressing them as \"you\", 2 to 4 sentences, present tense. "
"Include ONLY what they could see, hear, or feel from their standpoint and their act. OMIT everything "
"beyond their perception -- another's hidden hand, a theft they did not notice, others' private knowledge "
"or motives. If their act let them notice something subtle, give it as a sense or impression, at no more "
"certainty than it earns. Never narrate another character's interior.\n\n"
"Then a new line: PERCEIVED: <one line -- what you now know or feel, for your own record>") % (
        name, standpoint, act, truth)
    out = call(TIERS["soft"], p)
    return {"raw": out, "render": re.split(r"\n\s*\**PERCEIVED\**\s*:", out)[0].strip(),
            "perceived": _field(out, "PERCEIVED")}
