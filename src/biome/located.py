"""located -- the carried self-position (docs/located-block-spec.md).

A per-handle now-snapshot of where a reader stands across the four layers --
L0 infra, L1 island, L2 world, L3 present -- plus who and face. The thin end of
the spectrum whose rich end is the mobius reflexive current; the persisted form
of the /relay {frame, handle, vapour, face} heartbeat (the vapour stays
ephemeral on the relay, the standing persists here).

  located-<handle> = {
    0 situated line | 1 who | 2 world | 3 face | 4 where | 5 island | 6 infra | 7 present
  }

The membrane reads field 3 (face) for the CADO write-aperture, capped at the
shell's grant -- located may NARROW the aperture you hold, never widen it past
what your shell was granted. v1 holds the current standing with the world
explicit; a handle standing in two worlds at once extends to per-world standings
(noted, not built). Biome-world: hyphenated name (never a colon), digit keys.
"""


def name(handle):
    return "located-" + handle


def build(handle, kind="visitor", world="", face="observer", where="",
          island="", infra="", present=""):
    """The located block shape from a standing. semantic-at-0: position 0 is the
    one-line situated voicing a call re-reads to orient."""
    line = "I am %s (%s)" % (handle, kind)
    if world:
        line += ", present in %s" % world
    if where:
        line += " at %s" % where
    line += ", as %s, now." % (face or "observer")
    return {"0": line, "1": "%s -- %s" % (handle, kind), "2": world or "",
            "3": (face or "observer"), "4": where or "", "5": island or "",
            "6": infra or "", "7": present or ""}


def read(store, handle):
    return store.load_block(name(handle))


def face_of(store, handle):
    """The aperture the handle currently holds (located field 3), or None when it
    has no located block yet -- the membrane then falls back to the shell's grant."""
    b = read(store, handle)
    f = b.get("3") if isinstance(b, dict) else None
    return f.strip().lower() if isinstance(f, str) and f.strip() else None


def situate(store, handle, **fields):
    """Write/refresh located-<handle> from the current standing. Idempotent: only
    writes when the standing changed, so frequent heartbeats stay cheap. Returns
    True if it wrote."""
    blk = build(handle, **fields)
    if store.load_block(name(handle)) != blk:
        store.save_block(name(handle), blk)
        return True
    return False
