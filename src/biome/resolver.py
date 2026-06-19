"""resolver — the RPG's verbs de-crystallised: the rules live in the `mechanic`
block (flint), the kernel only routes. Gather the committed acts, hand the rule
+ the field to an LLM via spark, write the resolved scene back through the same
store serve.py serves. The kernel knows the FLOW (gather -> resolve -> settle),
never the rules — those are read from `mechanic`. A new game is a new mechanic
block, not new kernel code; this is the de-crystallisation the rig's tiers.py
proved (verbs as code) run forwards (verbs as blocks).

  python3 resolver.py [root]                 # root = the served cut's BIOME_ROOT
  RESOLVER_MODEL=claude-opus-4-8 python3 resolver.py .   # the heavier arbiter

Keyed (the cognition current): the LLM key at ~/.config/mobius/anthropic-key.
No key (or RESOLVER_DRY=1) -> the witness fallback (the no-cognition baseline),
so the flow runs free. This is one resolution pass; a watch-loop (resolve on a
cadence as acts land) is the next increment.
"""
import os
import sys
import json
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spark"))
sys.path.insert(0, HERE)

import spark
from store_fs import FsStore

MODEL = os.environ.get("RESOLVER_MODEL", "claude-sonnet-4-6")


def _key():
    k = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if k:
        return k
    p = os.path.expanduser("~/.config/mobius/anthropic-key")
    if os.path.exists(p):
        t = open(p, encoding="utf-8").read().strip()
        if t.startswith("ANTHROPIC"):
            return t.split("=", 1)[1].strip().strip('"').strip("'")
        return t
    return ""


def _call(prompt, max_tokens=900):
    if os.environ.get("RESOLVER_DRY"):
        return None
    key = _key()
    if not key:
        return None
    body = json.dumps({"model": MODEL, "max_tokens": max_tokens,
                       "messages": [{"role": "user", "content": prompt}]}).encode("utf-8")
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, method="POST",
        headers={"content-type": "application/json", "x-api-key": key, "anthropic-version": "2023-06-01"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.loads(r.read().decode("utf-8"))
        return "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text").strip()
    except urllib.error.HTTPError as e:
        return "[API ERROR %s] %s" % (e.code, e.read().decode("utf-8")[:200])


def _field(text, label):
    up = label.upper() + ":"
    for line in (text or "").splitlines():
        s = line.strip().lstrip("-*# ").strip()
        if s.upper().startswith(up):
            return s.split(":", 1)[1].strip().strip("*").strip()
    return ""


def _voice(block, walk):
    return spark.voice(spark.descend(block, walk)) if block else ""


def _children(block, walk):
    node = spark.descend(block, walk) if block else None
    out = []
    if isinstance(node, dict):
        for d in "123456789":
            if d in node:
                v = node[d] if isinstance(node[d], str) else spark.voice(node[d])
                if v:
                    out.append(v)
    return out


def _next_digit(block):
    for d in "123456789":
        if d not in block:
            return d
    inner = {k: block.pop(k) for k in list(block) if k != "0"}   # ring full -> supernest
    block["1"] = inner
    return "2"


def gather_acts(store, scope):
    """The committed acts at a scope — each player's liquid block."""
    acts = []
    for name in store.list_blocks():
        if name.startswith("liquid-"):
            blk = store.load_block(name)
            if blk and blk.get("1") == scope and blk.get("2"):
                who = (blk.get("0") or "").split(" — ")[0] or name[len("liquid-"):]
                acts.append((who, blk["2"], name))
    return acts


def field_text(store, recipe, walk):
    """The omniscient field for the arbiter — the place and its now, every who
    present, the objects in reach, and what already happened (the scene record)."""
    regs = recipe.get("1", {})
    nm = lambda d, default: ((regs.get(d) or {}).get("1")) or default
    S = store.load_block(nm("1", "upperton-space"))
    T = store.load_block(nm("2", "upperton-time"))
    I = store.load_block(nm("3", "upperton-identity"))
    scenes = store.load_block("scenes") or {}
    recent = [scenes[d] for d in "123456789" if isinstance(scenes.get(d), str)][-3:]
    return ("PLACE: %s\nNOW: %s\nWHOS PRESENT:\n- %s\nOBJECTS IN REACH: %s\nALREADY HAPPENED:\n- %s"
            % (_voice(S, walk) or "here", _voice(T, walk) or "(still)",
               "\n- ".join(_children(I, walk)) or "(none named)",
               "; ".join(_children(S, walk)) or "(none)",
               "\n- ".join(recent) or "(nothing yet)"))


def compose_prompt(mechanic, acts, field):
    """The arbiter's prompt = the rule (READ from the block, branch 3) + the
    acts + the field. The rule is not written in this file."""
    rule = mechanic.get("3") or "Resolve what actually happens; the more grounded reading is authoritative."
    actlines = "\n".join('- the %s: "%s"' % (n, a) for n, a, _ in acts)
    return ("%s\n\nTHE ACTS:\n%s\n\nTHE FULL FIELD (true beyond any one view):\n%s\n\n"
            "Respond EXACTLY:\nSCENE: <3-4 sentences, the canonical public moment, for the world's scene record>\n"
            "PREVAILED: <one phrase — who, and why>" % (rule, actlines, field))


def resolve(root):
    store = FsStore(os.path.join(root, "blocks"))
    mechanic = store.load_block("mechanic") or {}
    recipe = store.load_block("frame") or {}
    walk = str(recipe.get("2", "1,1,2,1")).split(",")
    scope = ",".join(walk)
    acts = gather_acts(store, scope)
    if not acts:
        print("resolver: no committed acts at", scope)
        return None
    out = _call(compose_prompt(mechanic, acts, field_text(store, recipe, walk)))
    minded = bool(out) and not out.startswith("[API ERROR")
    if minded:
        scene, prevailed = _field(out, "SCENE") or out, _field(out, "PREVAILED")
    else:                                                  # the witness — no mind present
        if out:
            print("resolver:", out)                        # surface an API error
        place = _voice(store.load_block((recipe.get("1", {}).get("1") or {}).get("1") or "upperton-space"), walk) or "here"
        scene = place + " — " + "; ".join("%s: %s" % (n, a) for n, a, _ in acts) + ".  (witnessed — no mind resolved this)"
        prevailed = ""
    scenes = store.load_block("scenes") or {"0": "Scenes — moments settled in play, deposited at the world's here/now."}
    d = _next_digit(scenes)
    scenes[d] = scene + (("  ▸ " + prevailed) if prevailed else "")
    store.save_block("scenes", scenes)
    for n, a, name in acts:                                # the acts are spent
        store.save_block(name, {"0": n + " — settled", "1": "", "2": ""})
    print("resolver: %d act(s) -> scenes %s%s" % (len(acts), d, "" if minded else "  (witness)"))
    print(" ", scenes[d])
    return scenes[d]


def watch(root, interval=2.0):
    """Resolve on commit, never on submit. The page's commit button writes a
    `resolve` signal; each tick, if it is set, synthesise the submitted acts and
    clear the signal. Submitting to liquid stages an intention and triggers
    nothing — only an explicit commit calls the medium (the VLS two-step)."""
    import time
    store = FsStore(os.path.join(root, "blocks"))
    print("resolver: watching %s — commit (the button) settles the table" % root)
    while True:
        try:
            sig = store.load_block("resolve")
            if sig and sig.get("0"):
                resolve(root)
                store.save_block("resolve", {"0": ""})
        except Exception as e:
            print("resolver: tick error:", e)
        time.sleep(interval)


if __name__ == "__main__":
    argv = sys.argv[1:]
    root = next((a for a in argv if not a.startswith("--")), None) or os.environ.get("BIOME_ROOT") or os.getcwd()
    (watch if "--watch" in argv else resolve)(root)
