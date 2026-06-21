"""federate -- make the patchwork walk across biomes (opt-in via BIOME_PEERS).

A biome that lists peer doors resolves a block it lacks by asking each peer in
turn, so a walk follows ref leaves seamlessly from one machine to the next: the
real-world map is ONE island spread over many hosts, not many islands. The
address never changes; only which host happens to hold a block does.

  BIOME_PEERS="https://biome-commons-production.up.railway.app,http://192.168.1.9:3210"

No peers set -> the loader is purely local, so a lone biome (and the live commons)
behaves exactly as before. Peer fetches hit a peer's read-only door (GET), which
serves only its own blocks -- so there is no recursion and no loop.
"""
import os
import json
import urllib.request
import urllib.parse

DOOR = "/.well-known/biome-beach"


def peers():
    return [p.strip().rstrip("/") for p in os.environ.get("BIOME_PEERS", "").split(",") if p.strip()]


def fetch(peer, name, timeout=8):
    """One block from one peer's door, or None."""
    url = "%s%s?block=%s" % (peer, DOOR, name)
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception:
        return None
    if isinstance(data, dict) and "absent" not in data and "blocks" not in data:
        return data
    return None


def fetch_any(name, ps=None):
    for p in (ps if ps is not None else peers()):
        b = fetch(p, name)
        if b is not None:
            return b
    return None


def loader(store, cache=None):
    """A spark loader: local store first, then peers on a miss (cached per read)."""
    cache = {} if cache is None else cache
    ps = peers()

    def load(n):
        if n in cache:
            return cache[n]
        b = store.load_block(n)
        if b is None and ps:
            b = fetch_any(n, ps)
        cache[n] = b
        return b
    return load


# --- resolve delegation: ask peers' own resolvers (DNS-style) ----------------
#
# loader() above spreads ONE island across hosts (a walk fetches a block it lacks
# from a peer's door). This is different: a name that lives in ANOTHER island --
# unreachable from this biome's own root -- is resolved by asking the peer's
# /resolve, which is authoritative for its own names. The query is NON-recursive
# (&delegate=0): the peer answers from its own index and does not re-delegate, so
# there is no loop. Each island stays authoritative for its own names.

def ask_resolve(peer, name, timeout=8):
    """Ask ONE peer's resolver for a name, non-recursively. Returns its match list
    (each match's url already points at the peer's own host), tagged with `via`, or []."""
    url = "%s/resolve?name=%s&delegate=0" % (peer, urllib.parse.quote(name))
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception:
        return []
    matches = data.get("matches", []) if isinstance(data, dict) else []
    for m in matches:
        if isinstance(m, dict):
            m.setdefault("via", peer)
    return matches


def resolve_peers(name, ps=None):
    """Aggregate non-recursive resolutions from all peers. Flat list of match
    entries; empty when no peers are set, so a lone biome is unchanged."""
    out = []
    for p in (ps if ps is not None else peers()):
        out.extend(ask_resolve(p, name))
    return out
