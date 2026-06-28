# Discovery — the lighthouse, the gazetteer, and why the structure is the directory

A design exploration, prompted by the real-world spatial island (2026-06-19). The
prior realisation: **reading is free** (the spark/bsp function + a plain `fetch` + a
URL reads any pscale block anywhere); **writing is governed** (the door + membrane,
per biome). What remains is the one hard problem — **discovery**: given a web of
pscale blocks at URLs across islands, how does a walker learn the URL for the place
it wants? The lighthouse and the gazetteer are two answers to exactly this.

## Three layers — only one is ground truth

1. **Walking — the ground truth.** Start at a known root URL; descend; at each node
   pick the child — *semantically* (read the ring of voicings, choose the match) for
   an LLM, or *structurally* (the ref is the child) for code. This needs only (a) the
   root URL and (b) refs that resolve to the next URL. It is `O(depth)`, fully
   distributed (every block holds its own children), and needs no central index.
   **The structure IS the directory.**

2. **The lighthouse — orientation.** A per-island curated block: what's notable here,
   where to start. For an *arriving* mind — a front desk, not a catalogue. Small,
   narrated, points at a notable few. It does not, and at scale cannot, list
   everything.

3. **The gazetteer — lookup.** A name → address(→URL) index, for jumping straight to a
   place without walking from the root ("I'm in Sheffield" → its address; "lock the UK
   prefix" → the UK's). An *optimisation* over walking. At scale it is not one file but
   a distributed, delegated, **derived** cache.

## It is DNS

The shape is exactly DNS. Root servers → TLDs → authoritative servers → records ≈
root block → continents → countries → … → place. DNS *resolution* is recursive
delegation; pscale *walking* is following refs — the same move. DNS also caches (the
resolvers); the gazetteer is that cache. So the master pattern is: **delegation
(walking) as truth, caching (the gazetteer) as speed, a well-known root as the entry.**
No central registry of billions — each zone is authoritative for its own subtree.

## The LLM turn — semantic walking *is* discovery

The biome is LLM-native, and that moves the centre of gravity. An LLM needs no name
index: it **walks** — reads the voicings, picks the matching child, descends. So for an
LLM, discovery = **the lighthouse (orientation) + semantic walking.** The gazetteer is
a crutch only for what an LLM-walk doesn't cover: deterministic or fast jumps,
non-LLM clients, the "lock the prefix" convention. So your original instinct — the
**lighthouse** — was the *more native* of the two; the gazetteer is the optimisation
beside it, not its replacement.

## Refs: names, with a resolver (keep blocks portable)

Two ways to make a ref resolve to a URL:

- **URL-refs** — the ref *is* the URL. Universal (any fetcher follows it), but brittle:
  blocks hardcode infrastructure that moves, and that breaks portability.
- **Name-refs + a resolver** — refs stay plain names (biome-native, portable); a
  resolver maps name → URL. The resolver is itself distributed/delegated: each island
  resolves the names it owns; the parent knows where a child's island lives.

**Recommendation: name-refs + a distributed resolver**, optionally a readable `name@url`
hint form (the name for readability and durable fallback, a URL hint for a direct hop).
Blocks stay portable; *resolution* is the discovery layer; **the gazetteer is that
resolver's cache.**

## The unification — and it fixes the lighthouse's standing problem

The lighthouse and the gazetteer are the same instinct at two grains: the lighthouse is
the **curated, notable few**; the gazetteer is the **exhaustive all**. Both are
**derived** from the structure (walk it, record name → address → URL). So:

- **gazetteer** = the full derived index — rebuildable, sharded per island, a cache.
- **lighthouse** = the curated top of that index — the notable/recent, derived and
  lightly curated.

This also dissolves the standing complaint that the live lighthouse is a hand-placed
"cheating-prop": a **derived** lighthouse (the notable slice of the walked structure) is
*grown*, not placed. One derivation, two completeness levels, neither the source of
truth — the structure is.

## Recommendation

- **Ground truth: the structure.** Refs as names; one well-known root URL per cosmology;
  walking (semantic, for LLMs) is the primary discovery. No central registry.
- **Resolver: a distributed gazetteer** (name → URL), delegated like DNS, derived from
  the structure, per-island authoritative, cached. A cache, never a source of truth.
- **Lighthouse: the curated top of the gazetteer**, derived — which also makes it grown,
  not hand-placed.
- **The seed — BUILT & LIVE (2026-06-19).** Rather than a stored gazetteer file, the
  resolver is a *served, derived* surface: `src/biome/discover.py` walks the island's
  blocks from the root and returns `name → {block, in-block walk, pscale, URL}`, with the
  URL composed from the request's own host. `serve.py` exposes it at **`GET /resolve?name=…`**
  and **`GET /gazetteer`** (CORS-open, derived live, never a stale file). Verified on the
  live island: a cold reader knowing only `https://realworld-biome-production.up.railway.app`
  calls `/resolve?name=Ulcinj`, gets a URL, and a plain `fetch` of it returns the block —
  no MCP. **Now federated (2026-06-21): a biome also asks its peers' own `/resolve`
  non-recursively (`&delegate=0`, so peers answer from their own index and don't
  re-delegate — loop-safe) and merges the matches** — each island authoritative for its
  own names, like DNS, no central registry (`federate.resolve_peers`; `serve.py /resolve`).
  Verified across two local biomes: one lacking the Montenegro branch entirely (no ref to
  follow) resolves Ulcinj *only* by delegating to its peer, and returns the peer's URL.
- **A genome current, not a real-world feature (2026-06-21).** The resolver no longer roots
  at the real world: `serve.py` senses the cosmology root(s) from the biome's **own store**
  — a `roots` block (plain-name leaves) if it declares one, else the spine root it carries,
  else none — and `discover.index/resolve` take that list. So discovery is the constitution's
  **(3,6) relation axis** (the resolver *endpoint* a biome exposes + *federation* delegation
  to peers) unfolded by **every** biome over whatever world it holds — not a new current.
  Demonstrated across distinct cosmologies: an earth biome and an invented "Rivertown Vale"
  biome each resolve their own world, and the earth biome resolves Rivertown *only* by
  delegating to its peer.

## Where this leaves the lighthouse vs gazetteer question

Not rivals. The gazetteer is the better *discovery* mechanism at scale (exhaustive,
distributed, derived). The lighthouse is the better *arrival* mechanism (curated, human,
"start here"). And the real point underneath both: neither is primary — **the refs from
a root are the self-describing directory**, and both lighthouse and gazetteer are derived
views over it (a summary and a full cache). That is the same discipline as everywhere
else in the biome: the blocks are the truth; indexes are derived and disposable.
