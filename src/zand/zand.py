#!/usr/bin/env python3
"""
zand.py — the ztone operational primitive (pure-digit pscale).

A ztone block is a JSON tree where every key is a single digit "0"-"9".
Digit "0" carries voicing — the zero-position semantic that makes its
sibling digits "1"-"9" cohere. There is no special character; "0" is a
digit like any other.

Signature
---------
    zand(block, number=None, attention=None, content=None,
         star=False, block_loader=None)

block        — dict, the JSON block to walk
number       — pscale address (str or numeric), at most one decimal point
attention    — pscale integer or None
content      — payload for write; omit for read
star         — when True, leaf strings matching `blockname:address` are
               resolved recursively via block_loader
block_loader — callable name -> dict, required if star=True

Walk semantics
--------------
The walk NEVER halts on missing structure. It walks every digit of the
canonical address. Each step produces a spindle entry tagged with status:

    voiced   — position carries a string at its 0-position
    headless — position exists as an object but has no zero-text
    absent   — no JSON node at this position

`len(walk_digits)` and the chain's traversed depth always agree by
construction, so terminus_pscale = floor - len(walk_digits) is exact.

Address canonicalisation
------------------------
The floor is ALWAYS checked first by descending the root zero-spine.
Every input address gets canonicalised to a single-decimal form pinned
to the floor:

    Dotted (e.g. '30.5'): left-of-decimal padded with zeros to match floor
        if shorter; rejected if longer than floor.
    Bare (e.g. '305'): pinned to floor. If len(digits) >= floor, first
        `floor` digits go left of decimal, rest go right. If shorter,
        padded with leading zeros to reach floor.

Bare addresses do NOT survive supernesting (they re-pin to each new
floor); dotted addresses DO (left-padding preserves the original
semantic position across growth).

Star (reference following)
--------------------------
By default leaf strings are returned verbatim. When star=True, leaves
matching `blockname` or `blockname:address` are resolved by recursive
zand calls via block_loader. Cross-block composition is by reference.

Write
-----
When content is provided, zand writes at the shape implied by
(number, attention). Lenient by default: missing intermediate dicts are
auto-created as headless objects. When an intermediate position is
currently a string, it is preserved as the new object's "0" voicing —
so a deep write to `1,2,3,4` against `{1: "branch one"}` yields
`{1: {0: "branch one", 2: {3: {4: <content>}}}}` (string preserved as
voicing, positions 2 and 3 created headless).

Notation
--------
Addresses use a single decimal: '30.5'. Walks (digit sequences) are
written with commas: 3,0,5. Multi-dot addresses are forbidden.
"""

import json
import os
import re
import sys


__version__ = "zand-alpha-1"
__author__ = "claude/canonical"
__spec__ = "ztone (sunztone + whetztone)"


class InvalidAddressError(ValueError):
    """Raised when a pscale address violates canonical form."""


# ---- Zero-spine helpers ---------------------------------------------------

def collect_zero_text(node):
    """Walk node's zero-spine to a terminal string; return None if headless."""
    if not isinstance(node, dict) or "0" not in node:
        return None
    val = node["0"]
    if isinstance(val, str):
        return val
    if isinstance(val, dict):
        return collect_zero_text(val)
    return None


def floor_depth(block):
    """Return the depth of the block's root zero-spine.

    Floor 1: block['0'] is a string.
    Floor 2: block['0']['0'] is a string.
    Floor N: walking '0' N times from root reaches a string.
    Floor 0: block has no '0' key at root (unanchored block).
    """
    node = block
    depth = 0
    while isinstance(node, dict) and "0" in node:
        depth += 1
        node = node["0"]
        if isinstance(node, str):
            return depth
    return depth


# ---- Address parsing ------------------------------------------------------

def parse_address(s):
    """Split an input address into (left_digits, right_digits, had_dot).

    Accepts string, int, or float. Raises InvalidAddressError on multi-dot
    addresses or non-digit characters.
    """
    if isinstance(s, bool):
        raise InvalidAddressError(
            f"address must be number or string, got bool {s!r}"
        )
    if isinstance(s, int):
        return list(str(s)), [], False
    if isinstance(s, float):
        formatted = f"{s:.10f}".rstrip("0").rstrip(".")
        if "." in formatted:
            left, right = formatted.split(".")
            return list(left), list(right), True
        return list(formatted), [], False

    text = str(s)
    dot_count = text.count(".")
    if dot_count > 1:
        raise InvalidAddressError(
            f'"{text}" has {dot_count} decimal points; '
            f"pscale addresses carry exactly one"
        )
    if dot_count == 1:
        left, right = text.split(".")
    else:
        left, right = text, ""
    for ch in left + right:
        if not ch.isdigit():
            raise InvalidAddressError(
                f'"{text}" contains non-digit character "{ch}"'
            )
    return list(left), list(right), dot_count == 1


def canonicalise(s, floor):
    """Return (walk_digits, canonical_address_string).

    The core rule: every address is pinned to the floor via a decimal
    point — EXPLICIT (dotted) or IMPLICIT (bare). The decimal placement
    IS the floor boundary, always.

    DOTTED addresses anchor at the floor the author wrote them for. If
    the current floor is deeper than the address's floor (post-supernest),
    the parser left-pads with zeros to match — preserving the semantic
    position across growth. Left-of-decimal exceeding the current floor
    is rejected.

    BARE addresses anchor at the current floor at read-time. The implicit
    decimal sits at the floor position: split-at-floor for equal-or-longer
    inputs, pad-left for shorter. Bare re-pins each read — use dotted for
    references that must survive supernesting.

    The canonical address string is the display form derived against the
    current floor: leading zeros above the floor are stripped (the parser
    re-pads on re-read).
    """
    if s is None or s == "":
        return [], ""

    left, right, had_dot = parse_address(s)

    if had_dot:
        if floor >= 1 and len(left) > floor:
            raise InvalidAddressError(
                f'address "{s}" has {len(left)} digits left of decimal '
                f"but block floor is {floor}; "
                f"left-of-decimal cannot exceed floor"
            )
        if floor >= 1 and len(left) < floor:
            left = ["0"] * (floor - len(left)) + left
    else:
        # Bare: implicit decimal pinned to the current floor. Split at the
        # floor boundary when length >= floor; pad-left to floor when shorter.
        if floor >= 1:
            if len(left) >= floor:
                left, right = left[:floor], left[floor:]
            else:
                left = ["0"] * (floor - len(left)) + left

    digits = left + right
    return digits, format_address(digits, floor)


def format_address(digits, floor):
    """Format walk digits as the canonical address string for this floor."""
    if not digits:
        return ""
    if floor < 1:
        return "".join(digits)
    if len(digits) <= floor:
        # All at or above floor; no fractional part
        left = list(digits)
        right = []
    else:
        left = digits[:floor]
        right = digits[floor:]
    # Strip leading zeros for display (parser repads from floor when reading)
    while len(left) > 1 and left[0] == "0":
        left = left[1:]
    if right:
        return "".join(left) + "." + "".join(right)
    return "".join(left)


# ---- Walk -----------------------------------------------------------------

def _make_entry(value, depth, floor):
    """Build a spindle entry: {pscale, text, status}.

    voiced: position carries a string (directly or via zero-spine descent)
    headless: position is an object with no terminal zero-text
    absent: no JSON node at this position
    """
    pscale = floor - depth
    if isinstance(value, str):
        return {"pscale": pscale, "text": value, "status": "voiced"}
    if isinstance(value, dict):
        text = collect_zero_text(value)
        if text is None:
            return {"pscale": pscale, "text": None, "status": "headless"}
        return {"pscale": pscale, "text": text, "status": "voiced"}
    return {"pscale": pscale, "text": None, "status": "absent"}


def walk_block(block, digits, floor):
    """Walk the block by digits, producing a spindle chain that never halts.

    Returns (chain, terminal_value, parent, last_key) where:
        chain          — list of {pscale, text, status} entries
        terminal_value — value at the terminus, or None if absent
        parent         — dict containing the final walked key, or None
        last_key       — final digit walked, or None

    The chain length is always len(digits) + 1. Missing structure produces
    'absent' entries from the failure point onward; headless entries are
    first-class and the walk continues through them.
    """
    chain = [_make_entry(block, 0, floor)]
    node = block
    parent = None
    last_key = None

    for i, d in enumerate(digits, start=1):
        if not isinstance(node, dict) or d not in node:
            for j in range(i, len(digits) + 1):
                chain.append({
                    "pscale": floor - j,
                    "text": None,
                    "status": "absent",
                })
            return chain, None, parent, last_key
        parent = node
        last_key = d
        node = node[d]
        chain.append(_make_entry(node, i, floor))

    return chain, node, parent, last_key


# ---- Star: reference recognition and resolution ---------------------------

# A reference is a leaf string of the form:
#   blockname
#   blockname:address
#   blockname:address:attention
# Block names may be namespaced with colons (e.g. 'sed:commons').
# Address is a pscale address (digits with optional one decimal).
# Attention is an integer (optionally negative).
_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_\-]*(?::[A-Za-z][A-Za-z0-9_\-]*)*$")
_REF_RE = re.compile(
    r"^(?P<name>[A-Za-z][A-Za-z0-9_\-]*(?::[A-Za-z][A-Za-z0-9_\-]*)*)"
    r"(?::(?P<addr>[0-9]+(?:\.[0-9]+)?)"
    r"(?::(?P<attn>-?[0-9]+))?)?$"
)


def parse_reference(s):
    """If s parses as a block reference, return (name, address, attention);
    else return None.

    Forms:
      'blockname'                       → (name, None, None)
      'blockname:address'               → (name, address, None)
      'blockname:address:attention'     → (name, address, int(attention))

    Block names may be colon-namespaced (e.g. 'sed:commons'). Address is a
    pscale number with optional one decimal. Attention is a signed integer.
    """
    if not isinstance(s, str):
        return None
    s = s.strip()
    if not s:
        return None
    m = _REF_RE.match(s)
    if not m:
        return None
    name = m.group("name")
    addr = m.group("addr")
    attn_str = m.group("attn")
    attn = int(attn_str) if attn_str is not None else None
    return name, addr, attn


def resolve_with_star(value, block_loader):
    """If value is a recognised reference, resolve via block_loader.

    The reference is treated as a deferred zand call. Whatever coordinates
    the reference carries are passed to the recursive call: the shape
    derives normally from (address, attention) against the target block's
    floor. With no address, the whole target block is returned. With
    address but no attention, the recursive call defaults to a spindle
    (zand's own default).
    """
    ref = parse_reference(value) if isinstance(value, str) else None
    if ref is None:
        return value
    name, address, attention = ref
    target_block = block_loader(name) if block_loader else None
    if target_block is None:
        return value
    return zand(target_block, number=address, attention=attention)


# ---- ZAND -----------------------------------------------------------------

def zand(block, number=None, attention=None, content=None, star=False,
         block_loader=None):
    """The ztone operational primitive — see module docstring."""
    floor = floor_depth(block)

    # Whole block
    if number is None and attention is None and content is None:
        return {"mode": "whole", "block": block, "floor": floor}

    # Disc read (no number, attention set)
    if (number is None or number == "") and attention is not None \
            and content is None:
        return _disc_read(block, attention, floor, star, block_loader)

    # Disc write
    if (number is None or number == "") and attention is not None \
            and content is not None:
        return _disc_write(block, attention, floor, content)

    # Parse and canonicalise the address
    digits, canonical = canonicalise(number, floor)
    chain, terminal, parent, last_key = walk_block(block, digits, floor)
    terminus_pscale = floor - len(digits)

    # Write
    if content is not None:
        return _zand_write(block, digits, attention, terminus_pscale,
                           content, floor)

    # Spindle (default when only number is given)
    if attention is None:
        if star:
            chain = [
                {
                    **e,
                    "text": (
                        resolve_with_star(e["text"], block_loader)
                        if e["status"] == "voiced" and isinstance(e["text"], str)
                        else e["text"]
                    ),
                }
                for e in chain
            ]
        return {
            "mode": "spindle",
            "address": canonical,
            "floor": floor,
            "entries": chain,
        }

    # Point / ring / directory based on attention vs terminus
    if attention == terminus_pscale:
        return _point_read(chain, terminus_pscale, star, block_loader)
    if attention > terminus_pscale:
        # Ring at attention's level (shallower than terminus). Walk to the
        # parent at depth (attention_depth - 1) to enumerate its children.
        return _ring_read_at(block, digits, attention, floor,
                             star, block_loader)
    # attention < terminus_pscale → directory rooted at terminus
    target_depth = floor - attention
    return _dir_read(terminal, len(digits), target_depth, floor,
                     star, block_loader)


# ---- Shape readers --------------------------------------------------------

def _point_read(chain, pscale, star, block_loader):
    """Read the terminus as a single point."""
    last = chain[-1]
    text = last["text"]
    if star and last["status"] == "voiced" and isinstance(text, str):
        text = resolve_with_star(text, block_loader)
    return {
        "mode": "point",
        "pscale": pscale,
        "text": text,
        "status": last["status"],
    }


def _ring_read_at(block, digits, attention, floor, star, block_loader):
    """Read the ring at attention's level along the spindle.

    The ring's depth = floor - attention. Its parent is at depth
    (attention_depth - 1), reached by walking the first (attention_depth - 1)
    digits of the spindle. The siblings are the parent's digit children at
    attention's level. The digit at digits[attention_depth - 1] (if the
    spindle reached that far) is the walked sibling.
    """
    attention_depth = floor - attention
    parent_depth = attention_depth - 1
    if parent_depth < 0:
        # Asking for ring at or above the root — no parent to enumerate
        return {"mode": "ring", "pscale": attention, "siblings": []}

    # Walk to parent_depth from root
    parent = block
    for d in digits[:parent_depth]:
        if not isinstance(parent, dict) or d not in parent:
            return {"mode": "ring", "pscale": attention, "siblings": []}
        parent = parent[d]
    if not isinstance(parent, dict):
        return {"mode": "ring", "pscale": attention, "siblings": []}

    # The walked sibling at attention_depth (if the spindle reached it)
    last_key = digits[parent_depth] if parent_depth < len(digits) else None

    siblings = []
    for d in "0123456789":
        if d not in parent:
            continue
        v = parent[d]
        if isinstance(v, str):
            text, status, is_branch = v, "voiced", False
        elif isinstance(v, dict):
            zt = collect_zero_text(v)
            if zt is None:
                text, status, is_branch = None, "headless", True
            else:
                text, status, is_branch = zt, "voiced", True
        else:
            text, status, is_branch = None, "absent", False
        if star and status == "voiced" and isinstance(text, str):
            text = resolve_with_star(text, block_loader)
        siblings.append({
            "digit": d,
            "text": text,
            "status": status,
            "is_branch": is_branch,
            "is_walked": d == last_key,
        })
    return {"mode": "ring", "pscale": attention, "siblings": siblings}


def _dir_read(terminal, terminus_depth, target_depth, floor,
              star, block_loader):
    """Read the subtree from terminus down to target_depth."""
    if terminal is None:
        return {"mode": "directory", "subtree": None, "status": "absent"}
    if not isinstance(terminal, dict):
        text = terminal
        if star and isinstance(text, str):
            text = resolve_with_star(text, block_loader)
        return {"mode": "directory", "subtree": text}

    levels = target_depth - terminus_depth
    if levels <= 0:
        zt = collect_zero_text(terminal)
        if star and isinstance(zt, str):
            zt = resolve_with_star(zt, block_loader)
        return {"mode": "directory", "subtree": zt}

    def truncate(node, remaining):
        if not isinstance(node, dict):
            if star and isinstance(node, str):
                return resolve_with_star(node, block_loader)
            return node
        if remaining <= 0:
            zt = collect_zero_text(node)
            if star and isinstance(zt, str):
                zt = resolve_with_star(zt, block_loader)
            return zt
        out = {}
        for k, v in node.items():
            out[k] = truncate(v, remaining - 1)
        return out

    return {"mode": "directory", "subtree": truncate(terminal, levels)}


def _disc_read(block, attention, floor, star, block_loader):
    """Read all positions at attention's depth across the whole block."""
    target_depth = floor - attention
    if target_depth < 0:
        return {"mode": "disc", "pscale": attention, "nodes": []}

    nodes = []

    def collect(node, depth, walked):
        if depth == target_depth:
            entry = _make_entry(node, depth, floor)
            text = entry["text"]
            if star and entry["status"] == "voiced" and isinstance(text, str):
                text = resolve_with_star(text, block_loader)
            address = format_address(walked, floor) if walked else ""
            nodes.append({
                "address": address,
                "text": text,
                "status": entry["status"],
            })
            return
        if not isinstance(node, dict):
            return
        for d in "0123456789":
            if d in node:
                collect(node[d], depth + 1, walked + [d])

    collect(block, 0, [])
    return {"mode": "disc", "pscale": attention, "nodes": nodes}


# ---- Write ----------------------------------------------------------------

def _zand_write(block, digits, attention, terminus_pscale, content, floor):
    """Write at the shape implied by (digits, attention).

    Lenient: missing intermediates are created as headless objects. When an
    intermediate position is currently a string, it is preserved as the new
    object's '0' voicing so the original meaning is not lost.
    """
    if not digits:
        if isinstance(content, dict):
            block.clear()
            block.update(content)
            return {"mode": "whole-write", "ok": True}
        return {"mode": "error", "error": "whole-block write requires a dict"}

    # Navigate to the parent of the terminus, creating intermediates.
    # If we encounter a string on the way, lift it into a new object's '0'
    # voicing so the original semantic is preserved.
    node = block
    for d in digits[:-1]:
        if not isinstance(node, dict):
            return {"mode": "error", "error": "non-dict on walk"}
        if d not in node:
            node[d] = {}
        elif isinstance(node[d], str):
            node[d] = {"0": node[d]}
        elif not isinstance(node[d], dict):
            node[d] = {}
        node = node[d]
    last_d = digits[-1]
    parent = node

    # Point write (attention at terminus or unset)
    if attention is None or attention == terminus_pscale:
        parent[last_d] = content
        return {
            "mode": "point-write",
            "ok": True,
            "address": format_address(digits, floor),
        }

    # Ring write (attention shallower than terminus)
    if attention > terminus_pscale:
        if not isinstance(content, dict):
            return {"mode": "error", "error": "ring-write requires dict"}
        if len(digits) < 2:
            for k in list(block.keys()):
                if k.isdigit():
                    del block[k]
            block.update({k: v for k, v in content.items() if k.isdigit()})
            return {"mode": "ring-write", "ok": True}
        # Re-walk to the grandparent of the terminus
        gp = block
        for d in digits[:-2]:
            if d not in gp:
                gp[d] = {}
            elif isinstance(gp[d], str):
                gp[d] = {"0": gp[d]}
            elif not isinstance(gp[d], dict):
                gp[d] = {}
            gp = gp[d]
        target = digits[-2]
        if target not in gp:
            gp[target] = {}
        elif isinstance(gp[target], str):
            gp[target] = {"0": gp[target]}
        elif not isinstance(gp[target], dict):
            gp[target] = {}
        ring_parent = gp[target]
        for k in list(ring_parent.keys()):
            if k.isdigit():
                del ring_parent[k]
        ring_parent.update({k: v for k, v in content.items() if k.isdigit()})
        return {"mode": "ring-write", "ok": True}

    # Directory write (attention deeper than terminus): replace terminus's value
    parent[last_d] = content
    return {"mode": "directory-write", "ok": True}


def _disc_write(block, attention, floor, content):
    """Disc write — list of {address, text} entries written as points."""
    if not isinstance(content, list):
        return {"mode": "error", "error": "disc-write requires list"}
    for entry in content:
        if not isinstance(entry, dict) or "address" not in entry:
            return {"mode": "error", "error": "disc-write entry malformed"}
        addr = entry["address"]
        text = entry.get("text")
        digits, _ = canonicalise(addr, floor)
        terminus_pscale = floor - len(digits)
        _zand_write(block, digits, terminus_pscale, terminus_pscale,
                    text, floor)
    return {"mode": "disc-write", "ok": True}


# ---- CLI ------------------------------------------------------------------

def _resolve_block_path(name):
    here = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(name):
        return name
    candidates = [
        name,
        os.path.join(here, "..", "sentinel", f"{name}.json"),
        os.path.join(here, "..", "sentinel", name),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: zand <block-name> [number] [attention] [--star]")
        sys.exit(1)
    name = sys.argv[1]
    path = _resolve_block_path(name)
    if path is None:
        print(f"Block not found: {name}")
        sys.exit(1)
    with open(path) as f:
        block = json.load(f)

    args = sys.argv[2:]
    star = "--star" in args
    args = [a for a in args if a != "--star"]

    number = args[0] if len(args) > 0 else None
    attention = None
    if len(args) > 1:
        try:
            attention = int(args[1])
        except ValueError:
            print(f"Attention must be integer, got: {args[1]}")
            sys.exit(1)
    if number in (None, "", "_"):
        number = None

    result = zand(block, number=number, attention=attention, star=star)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
