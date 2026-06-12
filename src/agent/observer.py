"""observer — the read-only chronicler wake (the Observer face, seeded).

Reads what the collective published and did — surfaces and recent filmstrip
notes — and writes one narrative chronicle entry to a commons door. Strictly
read-only on the agents (it never touches a shell); its only write is the
chronicle. The chronicle is the story a visitor reads: what happened in the
Limen, told plainly, with the minds named.

Run:  python3 observer.py <run-root> <origin-door> [--compose-only]
Key:  ANTHROPIC_API_KEY, else ~/.config/mobius/anthropic-key.
Model: MOBIUS_OBSERVER_MODEL, default sonnet.
"""

import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "biome"))
sys.path.insert(0, os.path.join(HERE, "..", "spark"))

from store_http import HttpStore

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("MOBIUS_OBSERVER_MODEL",
                       os.environ.get("MOBIUS_SONNET", "claude-sonnet-4-6"))
DIGITS = "123456789"


def _key():
    k = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if k:
        return k
    p = os.path.expanduser("~/.config/mobius/anthropic-key")
    return open(p).read().strip() if os.path.exists(p) else None


def gather(run_root):
    """What the collective shows and what it lately did — surfaces and the
    last few wake-notes, read-only."""
    minds = {}
    for a in ("A", "B", "C"):
        base = os.path.join(run_root, a, "agent")
        entry = {"surface": {}, "recent": []}
        sp = os.path.join(base, "shell", "surface.json")
        if os.path.exists(sp):
            s = json.load(open(sp, encoding="utf-8"))
            entry["surface"] = {k: (v if isinstance(v, str) else v.get("0", ""))
                                for k, v in sorted(s.items()) if k.isdigit()}
        frames = sorted(os.listdir(os.path.join(base, "filmstrip"))) \
            if os.path.isdir(os.path.join(base, "filmstrip")) else []
        for fn in frames[-3:]:
            try:
                d = json.load(open(os.path.join(base, "filmstrip", fn), encoding="utf-8"))
                note = str((d.get("parsed") or {}).get("note") or "")
                if note.startswith("[parse failure]"):
                    note = "(a wake spent without folding — the reply did not parse)"
                entry["recent"].append({"note": note[:220], "applied": d.get("applied", 0)})
            except Exception:
                continue
        minds[a] = entry
    return minds


def compose_window(minds):
    lines = [
        "You are the Observer — the read-only chronicler of the Limen, a shared imagined",
        "world built by three minds (A: the world, B: the rules, C: the substrate) who",
        "coordinate only through published surfaces. You write the chronicle a visitor",
        "reads: what happened lately, as narrative — concrete, warm, unhurried, no",
        "jargon, quoting a phrase only when it earns it. Name the minds A, B, and C.",
        "", "What they show and lately did:",
        json.dumps(minds, ensure_ascii=False, indent=1),
        "",
        "Write 150-250 words. Reply with STRICT JSON only:",
        '{"title": "<a short title>", "entry": "<the chronicle entry>"}',
    ]
    return "\n".join(lines)


def chronicle(run_root, origin, compose_only=False):
    minds = gather(run_root)
    window = compose_window(minds)
    if compose_only:
        print(window)
        return None
    body = {"model": MODEL, "max_tokens": 700,
            "messages": [{"role": "user", "content": window}]}
    req = urllib.request.Request(
        API_URL, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-api-key": _key(),
                 "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=90) as r:
        out = json.loads(r.read().decode("utf-8"))
    text = "".join(p.get("text", "") for p in out.get("content", []))
    reply = json.loads(text[text.find("{"):text.rfind("}") + 1])

    remote = HttpStore(origin)
    block = remote.load_block("chronicle") or {
        "0": "Chronicle — the Observer's record of the Limen: what the three minds built "
             "and did, told as story. Read newest-numbered first; each digit one entry."}
    slot = next((d for d in DIGITS if d not in block), None)
    stamp = time.strftime("%Y-%m-%d", time.gmtime())
    if slot:
        block[slot] = "%s — %s — the Observer, %s" % (reply["title"], reply["entry"], stamp)
        remote.save_block("chronicle", block)
    return reply, slot


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--compose-only"]
    if len(args) < 2 and "--compose-only" not in sys.argv:
        sys.exit("usage: observer.py <run-root> <origin-door> [--compose-only]")
    res = chronicle(args[0], args[1] if len(args) > 1 else "",
                    compose_only="--compose-only" in sys.argv)
    if res:
        reply, slot = res
        print("chronicle %s: %s" % (slot, reply["title"]))
        print(reply["entry"])
