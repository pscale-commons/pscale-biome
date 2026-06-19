"""discover — the gazetteer grown up: a name -> URL resolver derived from a
biome's own blocks, so the island is resolvable from anywhere.

Reading is free (a plain fetch + the spark function + a URL). The remaining
problem is DISCOVERY: name -> where to fetch it. This walks the patchwork from a
root, records each named place's block + in-block walk, and composes the door
URL, so a caller learns the fetchable URL for any place. It is DERIVED from the
structure (the blocks are the truth) and rebuilt on demand -- a cache, never a
source of truth. One island deep here; the loader can be peer-aware (federation),
and delegating to peers' own /resolve is the next step toward the whole web.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "spark"))
import spark

ROOT_PSCALE = 11


def _norm(s):
    return re.sub(r"\s+", " ", str(s).strip().lower())


def _disp(v):
    """The display name at the head of a voicing ('Wales / Cymru -- ...' -> 'Wales')."""
    if not isinstance(v, str):
        return ""
    return v.split(" -- ")[0].split(" / ")[0].strip()


def index(load, root="real-world-original", base=""):
    """Walk the patchwork from `root` (load(name) -> block or None) and return
    {norm_name: [entry]}, entry = {name, block, walk (in-block), pscale, url}.
    `url` is the door URL to FETCH the block; `walk` descends within it to the place."""
    door = (base.rstrip("/") if base else "") + "/.well-known/biome-beach"
    gaz, seen = {}, {root}

    def add(name, block, in_walk, spindle):
        if not name or name.startswith("("):            # skip headless "(... to be mapped)" slots
            return
        entry = {"name": name, "block": block, "walk": ",".join(in_walk),
                 "pscale": ROOT_PSCALE - len(spindle), "url": door + "?block=" + block}
        bucket = gaz.setdefault(_norm(name), [])
        if entry not in bucket:
            bucket.append(entry)

    def walk(block, node, in_walk, spindle, numbered):
        if not isinstance(node, dict):
            return
        if numbered:
            add(_disp(spark.voice(node)), block, in_walk, spindle)
        for d in spark.DIGITS:
            if d not in node:
                continue
            child = node[d]
            if isinstance(child, str):
                ref = spark.parse_reference(child)
                if ref and ref[0] not in seen and load(ref[0]) is not None:
                    seen.add(ref[0])
                    walk(ref[0], load(ref[0]), [], spindle + [d], True)   # hop: in-block walk resets
                else:
                    add(_disp(child), block, in_walk + [d], spindle + [d])
            else:
                walk(block, child, in_walk + [d], spindle + [d], True)
        if isinstance(node.get("0"), dict):                               # traverse the structural 0-rungs
            walk(block, node["0"], in_walk + ["0"], spindle + ["0"], False)

    root_block = load(root)
    if root_block is None:
        return gaz
    add(_disp(spark.voice(root_block)), root, [], [])                     # the root itself
    walk(root, root_block, [], [], False)
    return gaz


def resolve(load, name, root="real-world-original", base=""):
    """name -> [entry]; each entry's `url` fetches the block, `walk` finds the place in it."""
    return index(load, root, base).get(_norm(name), [])
