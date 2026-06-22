"""grow -- the write side of the real-world map: add places to the patchwork.

One call, `ensure(chain)`, drives both use-cases:
  * a cartographer agent mapping the world overnight, and
  * a person adding their own home when they join the beach.

`chain` is an ordered list of place names from a known anchor down to the leaf,
e.g. ["Earth","Europe","France","Paris","Le Marais","12 Rue de Bretagne","my flat"].
Each item may be a bare name or {"name","voice","block"} -- `block:true` makes that
place its own delegated block (the patchwork hop; default is auto at country
pscale). grow walks as far down as already exists (matching by name), then CREATES
the rest, and keeps the gazetteer (a name->spindle index) current. It is
idempotent: run the same chain twice and the second is a no-op, so many agents on
overlapping ground converge instead of colliding.

pscale is COMPUTED at read time, never stored: ROOT_PSCALE (Sol, +11) minus how
many digits were walked; the room is the floor, pscale 0. It is never written into
a place's voicing -- a baked "pscale +N" goes stale the instant the block
supernests (guarded by test-no-pscale-in-semantics.py). The structural 0-rungs (the
empty scales the spine leaves between named levels) are traversed automatically.

  python3 grow.py reindex                          # rebuild the gazetteer
  python3 grow.py add Earth Europe France Paris     # grow a chain
  python3 grow.py demo                              # the worked demonstration
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spark"))
sys.path.insert(0, HERE)
import spark
import rules

EARTH = os.environ.get("BIOME_EARTH") or os.path.join(HERE, "world", "earth")
# the gazetteer lives BESIDE the blocks dir (never inside it -- it is name-keyed, not a block)
GAZETTEER = os.environ.get("BIOME_GAZETTEER") or os.path.join(os.path.dirname(EARTH), "earth-gazetteer.json")
# the root, its pscale, and the shard scale are POLICY -- read from the editable `spine`
# block (the D of CADO), not constants here. rules.py turns that block into values.
ROOT, ROOT_PSCALE, COUNTRY_PSCALE = rules.ROOT, rules.ROOT_PSCALE, rules.COUNTRY_PSCALE


# --- names ------------------------------------------------------------------

def _norm(name):
    return re.sub(r"\s+", " ", str(name).strip().lower())


def _disp(voice):
    """The display name at the head of a voicing ('Wales / Cymru -- ...' -> 'Wales')."""
    if not isinstance(voice, str):
        return ""
    return voice.split(" -- ")[0].split(" / ")[0].strip()


def _slug(name):
    return re.sub(r"[^a-z0-9]+", "-", _norm(name)).strip("-") or "place"


# --- the patchwork handle ---------------------------------------------------

class Earth:
    """Blocks on disk + the gazetteer, with a write-through cache."""

    def __init__(self, directory=EARTH, gazetteer=GAZETTEER):
        self.dir = directory
        self.gaz_path = gazetteer
        self._blocks = {}
        self.gaz = spark.load(gazetteer) if os.path.isfile(gazetteer) else {}

    def load(self, name):
        if name not in self._blocks:
            p = os.path.join(self.dir, name + ".json")
            self._blocks[name] = spark.load(p) if os.path.isfile(p) else None
        return self._blocks[name]

    def save(self, name, block):
        self._blocks[name] = block
        spark.save(os.path.join(self.dir, name + ".json"), block)

    def exists(self, name):
        return self.load(name) is not None

    def unique_name(self, base):
        name, n = base, 2
        while self.exists(name):
            name, n = "%s-%d" % (base, n), n + 1
        return name

    def register(self, display, block, spindle):
        if not display:
            return
        entry = {"display": display, "block": block, "spindle": ",".join(spindle)}
        bucket = self.gaz.setdefault(_norm(display), [])
        bucket[:] = [e for e in bucket if e["spindle"] != entry["spindle"]] + [entry]

    def flush(self):
        spark.save(self.gaz_path, self.gaz)


# --- geometry helpers -------------------------------------------------------

def _child_host(node):
    """Descend a node's structural 0-rungs to the node that actually holds its
    numbered children. Returns (host, zero_path). Normal nodes return (node, [])."""
    z = []
    while (isinstance(node, dict) and not any(d in node for d in spark.DIGITS)
           and isinstance(node.get("0"), dict)):
        node, z = node["0"], z + ["0"]
    return node, z


def _next_slot(host):
    """A digit path to a fresh child slot of `host`. Fills 1-8 flat; overflows
    into a 9-group (graceful, never raises). Semantic grouping by the agent keeps
    this to one digit in practice."""
    for d in "12345678":
        if d not in host:
            return [d]
    if not isinstance(host.get("9"), dict):
        host["9"] = {"0": host.get("9", "(more)")}
    return ["9"] + _next_slot(host["9"])


def _set_at(host, path, value):
    for d in path[:-1]:
        if not isinstance(host.get(d), dict):
            host[d] = {"0": host[d]} if isinstance(host.get(d), str) else {}
        host = host[d]
    host[path[-1]] = value


def _match(earth, host, name):
    """Find a child of `host` naming `name`. Returns (digit, kind, ref) where kind
    is 'branch' (inline dict), 'ref' (delegating leaf), or 'leaf' (string voicing)."""
    want = _norm(name)
    for d in spark.DIGITS:
        if d not in host:
            continue
        child = host[d]
        if isinstance(child, str):
            ref = spark.parse_reference(child)
            if ref is not None and earth.exists(ref[0]):
                if (_norm(_disp(spark.voice(earth.load(ref[0])))) == want
                        or _norm(ref[0]) == want or _slug(name) == ref[0]):
                    return d, "ref", ref[0]
            elif _norm(_disp(child)) == want:
                return d, "leaf", None
        elif _norm(_disp(spark.voice(child))) == want:
            return d, "branch", None
    return None


def _descend(earth, spindle):
    """Mutable handles at the end of a spindle: (block_name, node)."""
    name, node = ROOT, earth.load(ROOT)
    for d in spindle:
        node = node[d]
        if isinstance(node, str):
            ref = spark.parse_reference(node)
            if ref and earth.exists(ref[0]):
                name, node = ref[0], earth.load(ref[0])
    return name, node


def _item(x):
    if isinstance(x, dict):
        return x.get("name"), x.get("voice"), x.get("block")
    return x, None, None


def _gaz(earth, name):
    """The gazetteer bucket for a name, matching its display form OR its slug
    (so 'North America' finds the 'north-america' delegating leaf)."""
    return earth.gaz.get(_norm(name)) or earth.gaz.get(_slug(name)) or []


# --- the one call -----------------------------------------------------------

def ensure(chain, earth=None):
    """Walk/create a named containment chain. chain[0] is an anchor that must
    already resolve ('Earth', a continent, or any mapped place)."""
    earth = earth or Earth()
    chain = [_item(x) for x in chain]
    bucket = _gaz(earth, chain[0][0])
    if bucket:
        spindle = [s for s in bucket[0]["spindle"].split(",") if s]
    elif _norm(chain[0][0]) in (_norm(ROOT), "the solar system", "earth"):
        spindle = ["3"] if _norm(chain[0][0]) == "earth" else []
    else:
        raise ValueError("anchor %r is not mapped -- reindex, or start from a "
                         "known place" % chain[0][0])
    block_name, node = _descend(earth, spindle)
    if isinstance(node, str):              # anchor is a delegating leaf with no block yet
        ref = spark.parse_reference(node)  # materialise it (e.g. the continent stubs in sol)
        block_name = ref[0] if ref else _slug(node)
        node = {"0": str(chain[0][0])}
        earth.save(block_name, node)
        earth.register(chain[0][0], block_name, spindle)
    dirty, created = set(), []

    for name, voice, want_block in chain[1:]:
        host, zpath = _child_host(node)
        m = _match(earth, host, name)
        if m:
            d, kind, ref = m
            spindle = spindle + zpath + [d]
            if kind == "ref":
                block_name, node = ref, earth.load(ref)
            elif kind == "leaf":
                host[d] = {"0": host[d]}
                node, dirty = host[d], dirty | {block_name}
            else:
                node = host[d]
            continue
        pscale_here = ROOT_PSCALE - (len(spindle) + len(zpath)) - 1
        if voice and _disp(voice) != name:          # keep the NAME at the voicing head,
            voicing = "%s -- %s" % (name, voice)     # so _disp (hence _match) recovers it
        elif voice:
            voicing = voice
        else:
            voicing = name                           # no pscale label: scale is structural,
                                                      # computed at read-time, never stored
        as_block = want_block if want_block is not None else (pscale_here == COUNTRY_PSCALE)
        slot = _next_slot(host)
        spindle = spindle + zpath + slot
        if as_block:
            child = earth.unique_name(_slug(name))
            _set_at(host, slot, child)
            earth.save(block_name, earth.load(block_name))
            block_name, node = child, {"0": voicing}
            earth.save(block_name, node)
        else:
            _set_at(host, slot, {"0": voicing})
            node = _descend(earth, spindle)[1]
            dirty.add(block_name)
        earth.register(name, block_name, spindle)
        created.append(name)

    for b in dirty:
        earth.save(b, earth.load(b))
    earth.flush()
    return {"spindle": spindle, "address": _addr(spindle), "walk": ",".join(spindle),
            "block": block_name, "pscale": ROOT_PSCALE - len(spindle), "created": created}


def add_location(chain, earth=None):
    """A person adds their home. Same engine; the leaf is tagged grown-by-inhabitant."""
    earth = earth or Earth()
    chain = list(chain)
    name, voice, blk = _item(chain[-1])
    chain[-1] = {"name": name, "voice": (voice or name) + "  (added by an inhabitant)",
                 "block": blk}
    return ensure(chain, earth)


# --- index & lookup (the gazetteer the system keeps for itself) -------------

def reindex(earth=None):
    """Rebuild the gazetteer by walking the whole patchwork from Sol. The blocks
    are the truth; this name->spindle index is derived and disposable."""
    earth = earth or Earth()
    earth.gaz = {}

    def walk(block_name, node, spindle, numbered, seen):
        if not isinstance(node, dict):
            return
        if numbered:
            earth.register(_disp(spark.voice(node)), block_name, spindle)
        for d in spark.DIGITS:
            if d not in node:
                continue
            child = node[d]
            if isinstance(child, str):
                ref = spark.parse_reference(child)
                if ref and ref[0] not in seen and earth.exists(ref[0]):
                    walk(ref[0], earth.load(ref[0]), spindle + [d], True, seen | {ref[0]})
                else:
                    earth.register(_disp(child), block_name, spindle + [d])
            else:
                walk(block_name, child, spindle + [d], True, seen)
        if isinstance(node.get("0"), dict):
            walk(block_name, node["0"], spindle + ["0"], False, seen)

    earth.register("Earth", ROOT, ["3"])
    walk(ROOT, earth.load(ROOT), [], False, {ROOT})
    earth.flush()
    return sum(len(v) for v in earth.gaz.values())


def lookup(name, earth=None):
    earth = earth or Earth()
    return [dict(e, pscale=ROOT_PSCALE - len([s for s in e["spindle"].split(",") if s]))
            for e in _gaz(earth, name)]


def lock(place, earth=None, under=None):
    """'I am in <place>' -> the convention prefix to lock and address beneath."""
    hits = lookup(place, earth)
    if under:
        hits = [h for h in hits if _norm(under) in h["display"].lower()] or hits
    if not hits:
        return None
    h = hits[0]
    return {"prefix": [s for s in h["spindle"].split(",") if s], "pscale": h["pscale"],
            "block": h["block"], "display": h["display"]}


def _addr(spindle):
    s = "".join(spindle)
    return s if len(spindle) <= ROOT_PSCALE else s[:ROOT_PSCALE] + "." + s[ROOT_PSCALE:]


# --- cli --------------------------------------------------------------------

def demo():
    earth = Earth()
    print("reindex:", reindex(earth), "named places")
    chains = [
        ["Earth", "Europe",
         {"name": "France", "block": True, "voice": "France -- western Europe."},
         {"name": "Ile-de-France", "voice": "Ile-de-France -- the Paris region."},
         {"name": "Paris", "voice": "Paris -- the capital on the Seine."},
         {"name": "Le Marais", "voice": "Le Marais -- the old quarter."},
         {"name": "12 Rue de Bretagne", "voice": "12 Rue de Bretagne -- a building."},
         {"name": "the apartment", "voice": "the apartment -- the floor."}],
        ["Earth", "Europe", "France", "Ile-de-France", "Paris",
         {"name": "Montmartre", "voice": "Montmartre -- the hill, 18th."}],
    ]
    for chain in chains:
        r = ensure(chain, earth)
        print("  grew %-20s -> %-13s p%+d  [%s]  created %d"
              % (_item(chain[-1])[0], r["address"], r["pscale"], r["block"], len(r["created"])))
    print("  idempotent re-run:", ensure(chains[0], earth)["created"], "(empty = converged)")
    print("lookup 'Paris':", lookup("Paris", earth))
    print("lock 'France':", lock("France", earth))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "reindex":
        print("gazetteer:", reindex(), "places")
    elif a and a[0] == "add" and len(a) > 1:
        print(ensure(a[1:]))
    else:
        demo()
