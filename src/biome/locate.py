"""locate -- the real-world spatial support layer over spark.

The real world is ONE pscale address space (one cosmology), too large for one
block, so it is a PATCHWORK: a thin scaffold (sol -> Earth -> continents) that
DELEGATES each country/region to its own block by a plain-name leaf, resolved by
a loader that may reach across servers. Spark already carries the two primitives
this needs -- `parse` (a bare suffix re-pins to a floor) and `parse_reference`
(a name[:address[:attention]] leaf points into another block). This module adds
only the layer above them:

  * walk(address)        -- descend the patchwork from Sol, hopping block to
                            block at each delegating leaf; pscale = 11 - depth.
  * find_prefix(block)   -- the convention spindle from Sol down to a block.
  * lock(place)          -- "I am in Ceidio": find a place and return its prefix
                            and pscale, so the inhabitant can address in suffix.
  * absolute(lock, tail) -- concatenate: a locked prefix + a local suffix.
  * localise(addr, lock) -- truncate: strip the locked prefix off an absolute
                            address, leaving the suffix.

The room is the magnitude point, pscale 0 (standard pscale-spine). Sol is +11.
So a node's pscale is just 11 minus how many digits were walked to reach it --
the spine prefix is exactly the part that is "locked as convention" and dropped.
Real vs fantasy is a +/- SIGN the reader applies to the spindle, never stored --
so this module is sign-agnostic; pscale is rough/semantic (size x population),
not physical. The forward walk below is only sugar over spark's own
parse_reference + loader + star; the one new step (find_prefix) is, at scale,
itself a pscale block (a gazetteer), not new machinery.

  python3 locate.py            # the demonstration (walks to all four homes)
  python3 locate.py 10006111111   # walk one absolute address, narrated
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spark"))
sys.path.insert(0, HERE)
import spark
import rules

EARTH = os.path.join(HERE, "world", "earth")
ROOT = rules.ROOT                # the cosmology root block (policy -- read from `spine`)
ROOT_PSCALE = rules.ROOT_PSCALE  # the root's pscale (the solar system, +11 by default)
FLOOR_PSCALE = 0        # the room -- the magnitude point


# --- the loader: name -> block (the seam a server widens) -------------------

def fs_loader(directory=EARTH):
    """A loader over a directory of <name>.json blocks. The ONLY thing that
    changes to span servers: a loader that, on a miss, fetches
    <host>/.well-known/biome-beach?block=<name>. Addressing never changes."""
    cache = {}

    def load(name):
        if name in cache:
            return cache[name]
        path = os.path.join(directory, name + ".json")
        block = spark.load(path) if os.path.isfile(path) else None
        cache[name] = block
        return block
    return load


def _digits(address):
    """An address (dotted) or a walk (commas) or a list -> a list of digits."""
    if isinstance(address, (list, tuple)):
        return [str(d) for d in address]
    s = str(address).strip()
    if "," in s:
        return [d for d in s.split(",") if d != ""]
    return [c for c in s if c != "."]


# --- walk: descend the patchwork, hopping at delegating leaves --------------

def walk(address, loader=None, root=ROOT):
    """Walk an absolute (Sol-rooted) address across the block patchwork.
    Returns a list of steps, one per digit:
      {digit, depth, pscale, block, voice, hop}  (hop = block jumped into, or None)
    plus a trailing summary. pscale = ROOT_PSCALE - depth, so the room is 0."""
    loader = loader or fs_loader()
    block = loader(root)
    if block is None:
        return {"ok": False, "error": "root block %r not found" % root, "steps": []}
    node, name, steps = block, root, []
    for i, d in enumerate(_digits(address)):
        if not isinstance(node, dict) or d not in node:
            steps.append({"digit": d, "depth": i + 1, "block": name,
                          "voice": None, "hop": None, "off_tree": True})
            return {"ok": False, "steps": steps, "node": None,
                    "pscale": ROOT_PSCALE - (i + 1), "voice": None,
                    "error": "off-tree at digit %d (%r) in block %r -- a headless "
                             "or unwritten slot" % (i + 1, d, name)}
        node = node[d]
        depth = i + 1
        hop = None
        if isinstance(node, str):
            ref = spark.parse_reference(node)
            if ref is not None and loader(ref[0]) is not None:
                name, child = ref[0], loader(ref[0])
                # a ref MAY carry its own descent (name:addr); bare leaves don't
                if ref[1]:
                    inner = spark.descend(child, spark.parse(ref[1], spark.floor(child)))
                    node = inner if inner is not None else child
                else:
                    node = child
                hop = name
        v = node if isinstance(node, str) else spark.voice(node)
        steps.append({"digit": d, "depth": depth, "pscale": ROOT_PSCALE - depth,
                      "block": name, "voice": v, "hop": hop, "off_tree": False})
    last = steps[-1] if steps else {"pscale": ROOT_PSCALE}
    return {"ok": True, "steps": steps, "node": node,
            "pscale": last["pscale"], "voice": last.get("voice")}


# --- find_prefix: the convention spindle from Sol to a block ----------------

def find_prefix(target, loader=None, root=ROOT):
    """DFS the scaffold (numbered children, the 0-spine, and delegating leaves)
    for the digit path from Sol to the block named `target`. This is the spindle
    that gets 'locked as convention'. At scale it is an index, not a search."""
    loader = loader or fs_loader()

    def search(name, node, prefix, seen):
        if name == target:
            return prefix
        if not isinstance(node, dict):
            return None
        for d in spark.DIGITS:                      # "1".."9": content & leaves
            if d in node:
                child = node[d]
                if isinstance(child, str):
                    ref = spark.parse_reference(child)
                    if ref and ref[0] == target:
                        return prefix + [d]
                    if ref and ref[0] not in seen and loader(ref[0]) is not None:
                        got = search(ref[0], loader(ref[0]), prefix + [d], seen | {ref[0]})
                        if got is not None:
                            return got
                elif isinstance(child, dict):
                    got = search(name, child, prefix + [d], seen)
                    if got is not None:
                        return got
        if "0" in node and isinstance(node["0"], dict):   # the structural 0-spine
            got = search(name, node["0"], prefix + ["0"], seen)
            if got is not None:
                return got
        return None

    return search(root, loader(root), [], {root})


def _skip_zeros(node):
    """Descend a node's structural 0-rungs (skipped scales) to the node that holds
    its numbered children. Returns (host, zero_digits)."""
    z = []
    while (isinstance(node, dict) and not any(d in node for d in spark.DIGITS)
           and isinstance(node.get("0"), dict)):
        node, z = node["0"], z + ["0"]
    return node, z


def floor_path(block, loader=None):
    """The in-block digit path from a block's root DOWN to its floor (the room),
    descending structural 0-rungs and following the primary child chain. Appended
    after find_prefix(block), it makes walk land on pscale 0 -- which is why the
    descent must be DERIVED, not assumed flat: a block's 0-rung depth varies with
    how many scales each step skips (spark.floor differs block to block)."""
    loader = loader or fs_loader()
    node, path = loader(block), []
    while isinstance(node, dict):
        host, z = _skip_zeros(node)
        path += z
        kids = [d for d in spark.DIGITS if d in host]
        if not kids:
            break                       # a voicing with no numbered child -- the floor
        path.append(kids[0])
        node = host[kids[0]]
    return path


# --- lock / absolute / localise: convention prefix <-> local suffix ---------

def lock(place, loader=None, root=ROOT):
    """"I am in <place>." Find the first node whose voicing names <place> and
    return the convention to lock: its prefix (digits from Sol), its pscale, and
    its voicing. Below it the inhabitant addresses in suffix only."""
    loader = loader or fs_loader()
    term = str(place).strip().lower()
    found = {}

    def search(name, node, prefix, seen):
        if found:
            return
        if isinstance(node, dict):
            v = spark.voice(node)
            if v and term in v.lower():
                found.update(prefix=prefix, pscale=ROOT_PSCALE - len(prefix),
                             block=name, voice=v)
                return
            for d in spark.DIGITS:
                if d in node:
                    child = node[d]
                    if isinstance(child, str):
                        v2 = child
                        ref = spark.parse_reference(child)
                        if ref and ref[0] not in seen and loader(ref[0]) is not None:
                            search(ref[0], loader(ref[0]), prefix + [d], seen | {ref[0]})
                        elif v2 and term in v2.lower():
                            found.update(prefix=prefix + [d],
                                         pscale=ROOT_PSCALE - len(prefix) - 1,
                                         block=name, voice=v2)
                    else:
                        search(name, child, prefix + [d], seen)
            if "0" in node and isinstance(node["0"], dict):
                search(name, node["0"], prefix + ["0"], seen)

    search(root, loader(root), [], {root})
    return found or None


def absolute(locked, tail):
    """Concatenate a locked prefix with a local suffix. `tail` may be a walk
    ('3,4'), a dotted address ('34'), or a list. A suffix of length == the
    lock's pscale lands exactly on the floor (the room)."""
    prefix = locked["prefix"] if isinstance(locked, dict) else _digits(locked)
    return prefix + _digits(tail)


def localise(address, locked):
    """Truncate: strip the locked prefix off an absolute address, leaving the
    suffix the inhabitant would actually type. Inverse of absolute()."""
    prefix = locked["prefix"] if isinstance(locked, dict) else _digits(locked)
    digs = _digits(address)
    if digs[:len(prefix)] != prefix:
        raise ValueError("address %r is not under the locked prefix %r"
                         % (address, "".join(prefix)))
    return digs[len(prefix):]


def to_address(digits, sol_pscale=ROOT_PSCALE):
    """Digits -> the one-decimal address form (decimal pinned to the floor)."""
    digs = _digits(digits)
    floor_len = sol_pscale - FLOOR_PSCALE        # integer digits down to the room
    s = "".join(digs)
    return s if len(digs) <= floor_len else s[:floor_len] + "." + s[floor_len:]


def to_walk(digits):
    return ",".join(_digits(digits))


# --- demonstration ----------------------------------------------------------

HOMES = [
    ("wales",           "Ceidio, North Wales"),
    ("west-midlands",   "33 Birbarn Close, Sutton Coldfield"),
    ("south-yorkshire", "Coach House, 9 Machon Bank, Sheffield"),
    ("montenegro",      "Apartments Milic, Ulcinj"),
]


def _narrate(address, loader):
    res = walk(address, loader)
    print("  %-16s  %s" % ("address", to_address(address)))
    print("  %-16s  %s" % ("walk", to_walk(address)))
    if not res["ok"]:
        print("  !! ", res["error"])
        return res
    for s in res["steps"]:
        tag = ("  -> into block '%s'" % s["hop"]) if s["hop"] else ""
        v = (s["voice"] or "(headless)").split(" -- ")[0].split(". ")[0][:54]
        print("    p%+d  [%s]  %s%s" % (s["pscale"], s["block"][:3], v, tag))
    print("  %-16s  pscale %+d  %s" %
          ("LANDS", res["pscale"], "<= the floor (room)" if res["pscale"] == 0 else ""))
    return res


def demo():
    loader = fs_loader()
    print("=" * 72)
    print("FLOORS (spark.floor of each block -- the zero-spine depth)")
    for nm in ["real-world-original", "united-kingdom", "wales", "west-midlands",
               "south-yorkshire", "montenegro"]:
        b = loader(nm)
        print("  %-18s floor %d" % (nm, spark.floor(b) if b else -1))

    print("=" * 72)
    print("WALK FROM SOL TO EACH HOME (one address space, blocks stitched by leaves)")
    for block, label in HOMES:
        print("\n%s" % label)
        addr = find_prefix(block, loader) + floor_path(block, loader)
        res = _narrate(addr, loader)
        assert res["ok"] and res["pscale"] == 0, "room did not land on the floor!"

    print("\n" + "=" * 72)
    print("LOCK & SUFFIX  ('I am in Ceidio' -- the spine becomes convention)")
    L = lock("Ceidio", loader)
    print("  locked:  %s  (prefix %s, pscale %+d)"
          % (L["voice"].split(" -- ")[0], to_address(L["prefix"]), L["pscale"]))
    print("  Now a 2-digit suffix reaches the floor (building, room):")
    for tail, gloss in [("11", "the house, room 1"), ("12", "the house, room 2"),
                        ("1", "the house (stops at pscale +1)")]:
        full = absolute(L, tail)
        res = walk(full, loader)
        where = (res.get("voice") or "(headless slot)").split(" -- ")[0]
        print("    suffix %-3s (%s)  ->  %-13s  p%+d  %s"
              % (tail, gloss, to_address(full), res["pscale"], where))

    print("\n  TRUNCATE (the inverse): an absolute address, seen from the lock --")
    room_addr = find_prefix("wales", loader) + floor_path("wales", loader)
    print("    absolute %s  ->  local suffix '%s'  under Ceidio"
          % (to_address(room_addr), to_walk(localise(room_addr, L))))
    print("=" * 72)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if args:
        _narrate(args[0], fs_loader())
    else:
        demo()
