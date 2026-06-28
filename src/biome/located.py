"""located -- the carried self-position (docs/located-block-spec.md).

A per-handle now-snapshot of where a reader stands across the four layers --
L0 infra, L1 island, L2 world, L3 present -- plus who and face. The thin end of
the spectrum whose rich end is the mobius reflexive current; the persisted form
of the /relay {frame, handle, vapour, face} heartbeat (the vapour stays
ephemeral on the relay, the standing persists here).

  located-<handle> = {
    0 line | 1 who | 2 world | 3 face | 4 where | 5 island | 6 infra | 7 present
    8: { 0 summary | 1..9 the OTHER worlds I also stand in (the concurrent ring) }
  }

0..7 is the ACTIVE standing -- the world the handle is currently acting in; the
membrane reads field 3 (face) for the CADO write-aperture, capped at the shell's
grant (located may NARROW the held aperture, never widen it past the grant).
8 is the concurrent ring: a handle present in two worlds at once keeps both --
the active flat, the rest under 8 (each a 0..7 standing), until it departs one.
Biome-world: hyphenated name (never a colon), digit keys.
"""

_F = "01234567"          # the active standing's fields


def name(handle):
    return "located-" + handle


def standing(handle, kind="visitor", world="", face="observer", where="",
             island="", infra="", present=""):
    """One world-standing -- the flat 0..7 shape (no ring). semantic-at-0:
    position 0 is the one-line situated voicing a call re-reads to orient."""
    line = "I am %s (%s)" % (handle, kind)
    if world:
        line += ", present in %s" % world
    if where:
        line += " at %s" % where
    line += ", as %s, now." % (face or "observer")
    return {"0": line, "1": "%s -- %s" % (handle, kind), "2": world or "",
            "3": face or "observer", "4": where or "", "5": island or "",
            "6": infra or "", "7": present or ""}


def read(store, handle):
    return store.load_block(name(handle))


def _world_of(s):
    return s.get("2", "") if isinstance(s, dict) else ""


def _active(blk):
    """The active standing (0..7) of a located block, without its ring."""
    return {k: blk[k] for k in _F if isinstance(blk, dict) and k in blk}


def _ring(blk):
    """The OTHER-world standings (8.1..8.9) as {world: standing}."""
    r = blk.get("8") if isinstance(blk, dict) else None
    out = {}
    if isinstance(r, dict):
        for k in "123456789":
            s = r.get(k)
            if isinstance(s, dict) and _world_of(s):
                out[_world_of(s)] = s
    return out


def _compose(active, others):
    """The located block: the active standing (0..7) + the concurrent ring at 8
    (others I also stand in), summarised at 8.0."""
    blk = dict(active)
    others = [s for s in others if isinstance(s, dict) and _world_of(s)]
    if others:
        ring = {"0": "Also standing in: " + ", ".join(_world_of(s) for s in others)}
        for i, s in enumerate(others[:9], start=1):
            ring[str(i)] = s
        blk["8"] = ring
    return blk


def worlds(store, handle):
    """Every world the handle stands in -- the active first, then the ring."""
    blk = read(store, handle)
    if not isinstance(blk, dict):
        return []
    out = [_world_of(blk)] if _world_of(blk) else []
    for w in _ring(blk):
        if w not in out:
            out.append(w)
    return out


def face_of(store, handle, world=None):
    """The aperture held in `world` (default: the active world), or None when the
    handle has no standing there -- the membrane then falls back to the shell."""
    blk = read(store, handle)
    if not isinstance(blk, dict):
        return None
    if world is None or world == _world_of(blk):
        f = blk.get("3")
    else:
        f = next((s.get("3") for w, s in _ring(blk).items() if w == world), None)
    return f.strip().lower() if isinstance(f, str) and f.strip() else None


def situate(store, handle, world="", **fields):
    """Make `world` the active standing; preserve any OTHER world the handle was
    active in into the concurrent ring (it still stands there until it departs).
    Idempotent -- writes only when the standing changed. Returns True if it wrote."""
    existing = read(store, handle)
    existing = existing if isinstance(existing, dict) else {}
    ring = _ring(existing)
    old = _world_of(existing)
    if old and old != world:                         # the handle still stands in its old world
        ring[old] = _active(existing)
    ring.pop(world, None)                            # `world` is now active, not in the ring
    blk = _compose(standing(handle, world=world, **fields), list(ring.values()))
    if blk != existing:
        store.save_block(name(handle), blk)
        return True
    return False


def depart(store, handle, world=None):
    """Leave a world (or, world=None, all). Leaving the active world promotes a
    ring world to active; leaving a ring world drops it. Returns True if it wrote."""
    existing = read(store, handle)
    if not isinstance(existing, dict):
        return False
    if world is None:
        blk = standing(handle)                       # neutral: observer, no world
    else:
        ring = _ring(existing)
        if world == _world_of(existing):
            if ring:
                w = next(iter(ring))
                blk = _compose(ring.pop(w), list(ring.values()))
            else:
                blk = standing(handle)
        elif world in ring:
            ring.pop(world)
            blk = _compose(_active(existing), list(ring.values()))
        else:
            return False                             # not standing there
    if blk != existing:
        store.save_block(name(handle), blk)
        return True
    return False
