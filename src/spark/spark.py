"""spark — the coded kernel for pscale blocks (the runtime).

A block is JSON whose keys are single digits "0"-"9". Digit "0" is a node's
voicing (its semantic, as a fact for its parent); "1"-"9" are its elaboration.
The zero-spine (the chain of "0"s from the root) sets the floor: floor is the
depth at which it first reaches a string, and pscale = floor - depth.

spark(block, number, attention, content?) is one call over two coordinates.
With content omitted it reads; with content it writes the same shape. The
shape is derived from (number, attention), never chosen.

This is the efficient runtime — invoked in one move, returning fast and exact.
flint.json is the same function as a block, read through spark for recognition;
slate.json is the external self-description a bare LLM reads to simulate it.
"""

import json
import re

DIGITS = "123456789"


class AddressError(ValueError):
    pass


# --- substrate verbs --------------------------------------------------------

def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, block):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(block, f, indent=2, ensure_ascii=False)
        f.write("\n")


def descend(block, digits):
    """Walk the digit sequence from the root; the node, or None if off-tree."""
    node = block
    for d in digits:
        if isinstance(node, dict) and d in node:
            node = node[d]
        else:
            return None
    return node


def voice(node):
    """A node's voicing: descend "0" to the first string, or None if headless."""
    while isinstance(node, dict):
        if "0" not in node:
            return None
        node = node["0"]
    return node if isinstance(node, str) else None


def floor(block):
    """Floor depth: count "0"-steps from the root to the first string."""
    n, node = 0, block
    while isinstance(node, dict):
        if "0" not in node:
            return n
        node = node["0"]
        n += 1
    return n


def status(node):
    if node is None:
        return "absent"
    if isinstance(node, str):
        return "voiced"
    return "voiced" if voice(node) is not None else "headless"


# --- address ----------------------------------------------------------------

def parse(number, flr):
    """A pscale address to a walk (list of digit strings). Bare re-pins to the
    current floor; dotted left-pads to survive supernesting."""
    s = "" if number is None else str(number)
    if s == "":
        return []
    if any(c not in "0123456789." for c in s):
        raise AddressError("address holds a non-digit: %r" % number)
    if s.count(".") > 1:
        raise AddressError("address has more than one decimal: %r" % number)
    if "." in s:
        left, right = s.split(".")
        if len(left) > flr:
            raise AddressError("left of decimal exceeds floor %d: %r" % (flr, number))
        return list(left.rjust(flr, "0") + right)
    return list(s if len(s) >= flr else s.rjust(flr, "0"))


# --- reference (refer/star) -------------------------------------------------

_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_-]*$")
_ADDR = re.compile(r"\d+(\.\d+)?$")
_ATT = re.compile(r"-?\d+$")


def parse_reference(leaf):
    """A leaf that names another block: name | name:address | name:address:attention.
    Returns (name, address|None, attention|None), or None if the leaf is plain
    content (has a space, is digit-led, or has a malformed tail)."""
    if not isinstance(leaf, str) or leaf == "" or " " in leaf:
        return None
    parts = leaf.split(":")
    i, name_segs = 0, []
    while i < len(parts) and _NAME.match(parts[i]):
        name_segs.append(parts[i])
        i += 1
    if not name_segs:
        return None
    name = ":".join(name_segs)
    address = attention = None
    if i < len(parts):
        if _ADDR.match(parts[i]):
            address = parts[i]
            i += 1
        else:
            return None
    if i < len(parts):
        if _ATT.match(parts[i]):
            attention = int(parts[i])
            i += 1
        else:
            return None
    return (name, address, attention) if i == len(parts) else None


def _resolve(text, loader):
    """If text is a reference and its block loads, read it there with star on.
    Returns the resolved shape, or None to keep the leaf verbatim."""
    if loader is None or not isinstance(text, str):
        return None
    ref = parse_reference(text)
    if ref is None:
        return None
    name, address, attention = ref
    target = loader(name)
    if target is None:
        return None
    return spark(target, address, attention, star=True, loader=loader)


# --- the function -----------------------------------------------------------

def spark(block, number=None, attention=None, content=None, star=False, loader=None):
    flr = floor(block)
    if content is not None:
        return _write(block, number, attention, content, flr)
    if number is None or str(number) == "":
        if attention is None:
            return {"mode": "whole", "floor": flr, "block": block}
        return _disc(block, attention, flr)
    walk = parse(number, flr)
    term = flr - len(walk)
    if attention is None:
        return _spindle(block, walk, flr)
    if attention == term:
        res = _point(block, walk, term)
        if star and res["status"] == "voiced":
            followed = _resolve(res["text"], loader)
            if followed is not None:
                return followed
        return res
    if attention > term:
        return _ring(block, walk, attention, flr)
    return _directory(block, walk, attention, flr)


def _spindle(block, walk, flr):
    entries, node, off = [], block, False
    for i, d in enumerate(walk):
        node = node[d] if (not off and isinstance(node, dict) and d in node) else None
        if node is None:
            off = True
        entries.append({"depth": i + 1, "pscale": flr - (i + 1),
                        "text": None if off else voice(node), "status": status(node)})
    return {"mode": "spindle", "floor": flr, "entries": entries}


def _point(block, walk, term):
    node = descend(block, walk)
    return {"mode": "point", "pscale": term,
            "text": voice(node) if node is not None else None, "status": status(node)}


def _ring(block, walk, attention, flr):
    depth = flr - attention            # the ring sits at this depth
    if depth < 1:
        return {"mode": "ring", "pscale": attention, "head": voice(block), "siblings": []}
    parent = descend(block, walk[:depth - 1])
    walked = walk[depth - 1] if depth - 1 < len(walk) else None
    sibs = []
    if isinstance(parent, dict):
        for d in DIGITS:
            if d in parent:
                ch = parent[d]
                sibs.append({"digit": d, "text": voice(ch) if isinstance(ch, dict) else ch,
                             "status": status(ch), "is_branch": isinstance(ch, dict),
                             "is_walked": d == walked})
    return {"mode": "ring", "pscale": attention,
            "head": voice(parent) if parent is not None else None, "siblings": sibs}


def _directory(block, walk, attention, flr):
    node = descend(block, walk)
    remaining = (flr - attention) - len(walk)

    def build(n, depth_left):
        if not isinstance(n, dict):
            return n
        if depth_left <= 0:
            return voice(n)
        out = {}
        if "0" in n:
            out["0"] = voice(n)                       # the head: collapse the 0-chain
        for d in DIGITS:
            if d in n:
                out[d] = build(n[d], depth_left - 1)
        return out

    return {"mode": "directory", "pscale": attention,
            "subtree": build(node, remaining) if isinstance(node, dict) else node}


def _disc(block, attention, flr):
    target = flr - attention
    nodes = []

    def rec(n, depth, addr):
        if depth == target:
            nodes.append({"address": addr, "text": voice(n) if isinstance(n, dict) else n,
                          "status": status(n)})
            return
        if isinstance(n, dict):
            for d in ["0"] + list(DIGITS):
                if d in n:
                    rec(n[d], depth + 1, addr + d)

    rec(block, 0, "")
    return {"mode": "disc", "pscale": attention, "nodes": nodes}


# --- write (conjugate of read) ----------------------------------------------

def _ensure(block, digits):
    """Walk to a node, creating missing intermediates as headless objects and
    lifting any string passed through into the new object's 0."""
    node = block
    for d in digits:
        if d not in node:
            node[d] = {}
        elif isinstance(node[d], str):
            node[d] = {"0": node[d]}                   # lift
        node = node[d]
    return node


def _write(block, number, attention, content, flr):
    if number is None or str(number) == "":
        if attention is None and isinstance(content, dict):
            block.clear()
            block.update(content)
            return {"mode": "whole-write", "ok": True}
        raise AddressError("a write with no number needs a whole-block object")
    walk = parse(number, flr)
    term = flr - len(walk)
    if attention is None or attention == term:           # point write, with lift
        parent = _ensure(block, walk[:-1])
        parent[walk[-1]] = content
        return {"mode": "point-write", "ok": True}
    if attention > term:                                  # ring write
        if not isinstance(content, dict):
            raise AddressError(
                "a ring write replaces the digit children — content must be an "
                "object of digit keys (note: an empty block has floor 0, so every "
                "term is negative; create a new block with a whole-block write — "
                "no number, object content)")
        depth = flr - attention
        parent = _ensure(block, walk[:depth - 1])
        for d in DIGITS:
            parent.pop(d, None)
        for k, v in content.items():
            parent[k] = v
        return {"mode": "ring-write", "ok": True}
    parent = _ensure(block, walk[:-1])                    # directory write
    parent[walk[-1]] = content
    return {"mode": "directory-write", "ok": True}


# --- fold (the companion: lay N blocks against the shared floor) -------------

def fold(blocks, attention):
    """Lay N blocks against their shared floor at one pscale: each block's
    positions at that pscale, aligned for the caller to read across. Aligned by
    pscale (floor - depth), never by walk-depth."""
    rows = [{"block": i, "nodes": _disc(b, attention, floor(b))["nodes"]}
            for i, b in enumerate(blocks)]
    return {"mode": "fold", "pscale": attention, "blocks": rows}
