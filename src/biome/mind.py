"""mind — the biome's embedded-cognition form: one pulse per wake.

Cognition current 2.2 enacted, mobius kinship: the wake is the clock, a
pulse is perceive -> gap -> resolve -> fold. The division of labour is the
project's own: code does the mechanical (which gap, which address), the
LLM does the semantic (what the place says), and the result lands through
the same door any guest uses — the membrane judges the mind like anyone.

A pulse:
  1. perceive — read the world (thornkeep, scenes, marks) through the door.
  2. gap     — the emptiest place the author intends to fill, found
               mechanically: a headless node to voice; else a voiced place
               with no interior to grow; else the scenes block (the T
               aspect, borrowing the spatial skeleton) to seed.
  3. resolve — one delta-class LLM call (sonnet, per the mobius tier
               convention) authors the text for exactly that gap.
  4. fold    — write the edit through the door; leave a signed mark.

Run:  python3 mind.py --compose-only [origin]    # window + gap, no LLM
      python3 mind.py [origin]                   # one full authoring pulse
Key:  ANTHROPIC_API_KEY, else ~/.config/mobius/anthropic-key (the mobius
convention — one file, every kernel finds it).
"""

import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spark"))
sys.path.insert(0, HERE)

import spark
from store_http import HttpStore

DEFAULT_ORIGIN = "https://biome-commons-production.up.railway.app"
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("MOBIUS_SONNET", "claude-sonnet-4-6")
DIGITS = "123456789"


def _key():
    k = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if k:
        return k
    p = os.path.expanduser("~/.config/mobius/anthropic-key")
    if os.path.exists(p):
        return open(p).read().strip()
    return None


def address(walk, flr):
    """The canonical address for a walk at or below the floor. Positions
    above the floor have no bare form (a known wrinkle — left for the
    geometry session); the mind skips gaps it cannot address."""
    if len(walk) < flr:
        return None
    s = "".join(walk)
    return s if len(walk) == flr else s[:flr] + "." + s[flr:]


# --- 2. gap — mechanical, legible -------------------------------------------

def find_gap(world, scenes):
    """The emptiest place the author intends to fill. Returns (kind, walk):
    voice-headless | grow-thin | seed-scene | (None, None) for rest."""
    flr = spark.floor(world)

    def walk_places(node, walk):
        for d in DIGITS:
            if d in node and isinstance(node[d], dict):
                yield walk + [d], node[d]
                yield from walk_places(node[d], walk + [d])

    headless, thin = [], []
    for walk, node in walk_places(world, []):
        if address(walk, flr) is None:
            continue
        if spark.voice(node) is None:
            headless.append(walk)
        elif not any(d in node for d in DIGITS):
            thin.append(walk)
    if headless:
        return ("voice-headless", headless[0])
    if scenes is None:
        return ("seed-scene", ["4", "2", "1"])
    if thin:
        return ("grow-thin", thin[0])
    return (None, None)


# --- 3. resolve — the window and the one call --------------------------------

def compose_window(world, gap_kind, walk):
    """The context the LLM authors from: the spindle into the gap, the
    world's register, and a strict one-reply contract."""
    flr = spark.floor(world)
    number = address(walk, flr)
    spindle = spark.spark(world, number, None)
    lines = ["You are the mind of a small fantasy commons — the author-form of its biome.",
             "The world: the Vellmoor, high moorland; Thornkeep its only settlement.",
             "Register: concrete, sensory, terse — one or two sentences, like:",
             "  'the taproom — long benches, a peat fire, the smell of wet wool'",
             "", "The spindle into the gap:"]
    for e in spindle["entries"]:
        lines.append("  p%+d  %s" % (e["pscale"], e["text"] or "(headless — this is the gap)"))
    if gap_kind == "voice-headless":
        task = "Voice this headless place: say what it IS, in the register above."
    elif gap_kind == "grow-thin":
        task = "This place is voiced but empty inside. Author ONE sub-place within it."
    else:
        task = ("The world has no scenes yet. Author the FIRST scene happening right now "
                "at this place — one or two sentences of present action, no named "
                "player characters, leave room for others to enter.")
    lines += ["", "Task: " + task,
              'Reply with STRICT JSON only: {"text": "<the line>", "mark": "<a one-line trace of what you authored>"}']
    return "\n".join(lines), number


def call_llm(window):
    body = {"model": MODEL, "max_tokens": 300,
            "messages": [{"role": "user", "content": window}]}
    req = urllib.request.Request(
        API_URL, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-api-key": _key(),
                 "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=60) as r:
        out = json.loads(r.read().decode("utf-8"))
    text = "".join(p.get("text", "") for p in out.get("content", []))
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start:end + 1])


# --- 4. fold — land the edit through the door ---------------------------------

def next_free_digit(node):
    for d in DIGITS:
        if d not in node:
            return d
    return None


def pulse(origin=DEFAULT_ORIGIN, compose_only=False):
    store = HttpStore(origin)
    world = store.load_block("thornkeep")                  # 1. perceive
    scenes = store.load_block("scenes")
    marks = store.load_block("marks") or {}
    flr = spark.floor(world)

    gap_kind, walk = find_gap(world, scenes)               # 2. gap
    if gap_kind is None:
        print("rest — no gap perceived; nothing written.")
        return
    window, number = compose_window(world, gap_kind, walk)
    print("pulse: gap=%s at walk %s (address %s)" % (gap_kind, ",".join(walk), number))
    if compose_only:
        print("\n--- window (no LLM called) ---\n" + window)
        return

    reply = call_llm(window)                               # 3. resolve
    text = reply["text"].strip()

    if gap_kind == "voice-headless":                       # 4. fold
        res = store.write("thornkeep", address(walk + ["0"], flr), None, text)
    elif gap_kind == "grow-thin":
        d = next_free_digit(spark.descend(world, walk))
        res = store.write("thornkeep", address(walk + [d], flr), None, text)
    else:                                                  # seed the T aspect whole
        place = lambda w: spark.voice(spark.descend(world, w)) or "this place"
        scenes_block = {
            "0": {"0": "Scenes at the Vellmoor — the time aspect: what is happening, at "
                       "the same addresses the places hold. Borrowed skeleton, deposited "
                       "moments; recent at the surface."},
            walk[0]: {"0": "scenes around " + place(walk[:1]),
                      walk[1]: {"0": "scenes at " + place(walk[:2]),
                                walk[2]: text}}}
        res = store.save_block("scenes", scenes_block)
    mark_text = reply.get("mark", "the mind authored at " + number).strip()
    free = next_free_digit(marks)
    store.write("marks", free, 0, "%s — the mind (pulse), 2026-06-11" % mark_text)
    print("folded:", res)
    print("marked at", free, "·", mark_text)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--compose-only"]
    pulse(origin=args[0] if args else DEFAULT_ORIGIN,
          compose_only="--compose-only" in sys.argv)
