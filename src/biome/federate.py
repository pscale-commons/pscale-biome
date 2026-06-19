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
