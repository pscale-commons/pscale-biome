"""cartographer -- map the real world overnight.

A self-clocking crawler: from a root place it asks an LLM to name the major
sub-places one scale down (grouped so a ring stays <=8), grows each into the
patchwork via grow.ensure, and descends breadth-first to a target depth. grow is
idempotent and writes as it goes, so a run is **resumable and crash-safe** -- stop
it, re-run, and it continues; many runs over overlapping ground converge. This is
the "set a bunch of agents going before bed" engine; each LLM call is one agent's
turn at one place.

Keyed like resolver.py (the cognition current): the LLM key at
~/.config/mobius/anthropic-key, or ANTHROPIC_API_KEY. No key -> nothing to enumerate.

  python3 cartographer.py --root Europe --depth 3 --limit 400
  python3 cartographer.py --root "United Kingdom" --depth 4
  CARTOGRAPHER_MODEL=claude-haiku-4-5-20251001 python3 cartographer.py --root Asia --depth 2
"""
import os
import sys
import json
import re
import argparse
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spark"))
sys.path.insert(0, HERE)
import grow

MODEL = os.environ.get("CARTOGRAPHER_MODEL", "claude-sonnet-4-6")


def _key():
    k = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if k:
        return k
    p = os.path.expanduser("~/.config/mobius/anthropic-key")
    if os.path.isfile(p):
        t = open(p, encoding="utf-8").read().strip()
        return t.split("=", 1)[1].strip().strip('"').strip("'") if t.startswith("ANTHROPIC") else t
    return ""


def _call(prompt, max_tokens=1100):
    key = _key()
    if not key:
        return None
    body = json.dumps({"model": MODEL, "max_tokens": max_tokens,
                       "messages": [{"role": "user", "content": prompt}]}).encode("utf-8")
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, method="POST",
        headers={"content-type": "application/json", "x-api-key": key,
                 "anthropic-version": "2023-06-01"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.loads(r.read().decode("utf-8"))
        return "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text")
    except urllib.error.HTTPError as e:
        print("  ! api %s: %s" % (e.code, e.read().decode("utf-8")[:160]))
        return None
    except Exception as e:
        print("  ! call:", e)
        return None


PROMPT = """You are mapping the real world as a navigable containment hierarchy.

Place: {place}
Path from above: {path}

List the major sub-places ONE scale down INSIDE "{place}" -- the kind of place a
person would name to say where they are. Group SEMANTICALLY so there are AT MOST 8:
if there would be more, introduce natural sub-groupings (regions, boroughs,
districts) and list those instead. NEVER list more than 8.

For each, give:
  - "name": its common name
  - "voice": one short descriptive line, ending with " pscale +N" where N is the scale
     by SIZE and POPULATION (10^N people, roughly): room/1-person 0, building/10 +1,
     street-or-village/100 +2, town/1k +3, large-town-or-valley/10k +4, smaller-city/100k +5,
     city/1m +6, region-or-megacity/10m +7, country/100m +8, continent/1b +9, Earth +10.
     Pick the nearest scale to the place's real size; consecutive places may skip scales.
  - "block": true only if it deserves its own map block (a country, or a very large
     city or region); otherwise false

Reply with ONLY a JSON object: {{"children":[{{"name":"..","voice":"..","block":false}}]}}
If "{place}" is itself a single building or room with nothing meaningful to map
inside, reply {{"children":[]}}."""


def enumerate_children(chain):
    out = _call(PROMPT.format(place=chain[-1], path=" > ".join(chain)))
    if not out:
        return []
    m = re.search(r"\{.*\}", out, re.S)
    if not m:
        return []
    try:
        data = json.loads(m.group(0))
    except Exception:
        return []
    kids = data.get("children", []) if isinstance(data, dict) else []
    clean = []
    for k in kids[:8]:
        if isinstance(k, dict) and k.get("name"):
            clean.append({"name": str(k["name"]).strip(),
                          "voice": str(k.get("voice", "")).strip() or None,
                          "block": bool(k.get("block"))})
    return clean


def run(root, depth, limit):
    earth = grow.Earth()
    print("cartographer: reindex", grow.reindex(earth), "places; root=%r depth=%d limit=%d model=%s"
          % (root, depth, limit, MODEL))
    if grow.lock(root, earth) is None and grow._norm(root) not in ("earth",):
        print("  ! root %r is not on the map yet -- map its parent first, or seed it." % root)
        return
    queue, calls, grown = [([root], depth)], 0, 0
    while queue and calls < limit:
        chain, d = queue.pop(0)
        kids = enumerate_children(chain)
        calls += 1
        made = 0
        for k in kids:
            try:
                r = grow.ensure(chain + [k], earth)
                made += len(r["created"])
                if d > 1:
                    queue.append((chain + [k["name"]], d - 1))
            except Exception as e:
                print("  ! grow %s/%s: %s" % (" > ".join(chain), k.get("name"), e))
        grown += made
        print("  [%3d/%d] %-48s +%d (%d named total, queue %d)"
              % (calls, limit, (" > ".join(chain))[:48], made,
                 sum(len(v) for v in earth.gaz.values()), len(queue)))
    print("cartographer: done. %d calls, %d places grown, %d named on the map."
          % (calls, grown, sum(len(v) for v in earth.gaz.values())))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="Europe")
    ap.add_argument("--depth", type=int, default=3)
    ap.add_argument("--limit", type=int, default=400)
    a = ap.parse_args()
    run(a.root, a.depth, a.limit)
