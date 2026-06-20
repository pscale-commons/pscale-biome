# The gazetteer is the connector — what the real-world island yielded, and where it goes

> **Trajectory analysis, 2026-06-20.** A forward-path note written before opening a build
> front, so the reasoning is on record. Sits beside the founding
> [real-world-spatial-spec.md](real-world-spatial-spec.md) (the block) and
> [discovery-lighthouse-gazetteer.md](discovery-lighthouse-gazetteer.md) (the discovery
> design). This one steps back: what the real-world island *actually produced* that isn't
> about the real world, why the gazetteer is the architecturally load-bearing piece, and
> the three trajectories available from here. Memory: `project_real_world_spatial`.

## The reframe — three general primitives, not one spatial block

The island set out to be "a spatial block like any other, only it maps to the real world
rather than a fantasy one." But the real world has one property fantasy never *forces*:
it is too big for any one block, and nobody owns the whole of it. That single constraint
pushed three pieces of **general** infrastructure into existence — and none of them are
really about the real world:

1. **The patchwork walk** — [`locate.walk`](../src/biome/locate.py) crossing block→block
   through ref-leaves, accumulating *global* pscale across each seam, and
   [`federate.py`](../src/biome/federate.py) letting that walk cross *hosts*. This is "a
   block bigger than a block" — the federation primitive made concrete and walkable.
2. **The grow engine** — [`grow.ensure`](../src/biome/grow.py): idempotent, auto-sharding
   at country scale, gazetteer-keeping. This is "many hands authoring overlapping
   structure and *converging* instead of colliding."
3. **The gazetteer / resolver** — [`discover.py`](../src/biome/discover.py): a *derived*
   name→address→URL index served live at `/resolve` and `/gazetteer`. This is
   **discovery**.

The real world was the **forcing function**. The yield is general: any biome whose
content outgrows one block, or spreads across hosts, or wants to be reachable by name,
needs exactly these three. They were discovered here because the real world made them
unavoidable.

## The connector thesis — discovery is what makes N biomes one web

Reading was *already* free before any of this: a plain `fetch` + the spark function + a
URL reads any block anywhere, with no MCP, no key, no account. So **transport was never
the problem.** The one genuinely unsolved problem in a distributed biome web is the
inverse: **finding the URL.** Given blocks scattered across islands and hosts, how does a
walker reach the one it wants?

The gazetteer is that answer, and it is exactly **DNS-shaped**:

- **delegation is the truth** — each block holds its own children; walking *is*
  resolution; the structure is the directory. No central registry of billions.
- **the index is a cache** — the gazetteer is *derived* from the walk and rebuildable at
  any time (`grow.reindex`); it is never a source of truth, only speed.
- **a well-known root is the entry** — one root URL per cosmology, and `O(depth)` hops to
  anything.

Discovery is precisely the thing that turns *N isolated biomes* into *one walkable web*.
That is why the gazetteer — not the map it happens to index — is the architecturally
important piece. **The real world was the forcing function; the gazetteer is the
connector.**

## Where it actually stands today (2026-06-20)

Honest grounding, so the trajectories aren't wishful. Walked live via the island's MCP
and its door.

- **Live island** (`realworld-biome-production.up.railway.app`) carries **8 scaffold
  blocks**; `/gazetteer` returns **31 named places** — the solar system, the planets, the
  Europe→UK/Montenegro spine, and the four homes' chains. The **"143 places across all
  continents"** from the cartographer was a *local* run that was **never committed or
  deployed**.
- **No durable volume.** The store re-seeds from the Docker image on each deploy
  (`BIOME_ROOT=/data`, nothing mounted), so a grown world does not survive a redeploy.
  Persistence was deliberately **deferred as author-proper** (how grown-vs-seeded content
  persists is a design decision, not a bolt-on). This is the gate under Trajectory A.
- **Reading is fully native and free.** Walk, `/resolve`, `/gazetteer`, the door, `/world`,
  the spark MCP — all live, all CORS-open. Block-fetch *during* a resolve is already
  peer-aware: `/resolve` and `/gazetteer` walk with `federate.loader(self.store)`, so with
  `BIOME_PEERS` set, a walk that needs a block this host lacks fetches it from a peer.
  *One island already spreads across hosts.*
- **Growing is not on the live surface.** [`serve.py`](../src/biome/serve.py) imports
  `discover` but **not** `grow`. The door `POST` and the `/mcp` spark tool both do *raw
  single-block writes* (`run_spark`). The chain-intelligence in
  [`grow.ensure`](../src/biome/grow.py)/`add_location` (walk names, create what's missing,
  auto-shard, keep the gazetteer current) lives **only in the CLI**. So the headline
  use-case — *a person adds their own room* — is **not wired** to the live island.
- **`spark.fold` exists** ([`spark.py`](../src/spark/spark.py)) — the floor-aligned
  cross-block primitive. It is the hook for laying time and identity against this spatial
  floor (Trajectory C, the STI move), and it is unused by the island today.
- **Inter-island resolve-delegation is unbuilt.** `discover` only ever indexes from *its
  own* root (`real-world-original`). A biome asking a *foreign* island's `/resolve` for a
  name it can't reach from its own root — true biome-DNS — is the next step the discovery
  doc names but nothing yet does.

## Trajectory A — growth, and the overnight cartographer

The machinery is built and proven. [`cartographer.py`](../src/biome/cartographer.py) is a
resumable, crash-safe BFS that asks an LLM to name ≤8 sub-places per node and grows each
through the idempotent engine; disjoint roots run in parallel without collision. What is
missing is not the engine — it is the **floor under it**.

- **The gate is persistence.** "Set agents mapping overnight" only matters if the result
  survives. That is the author-proper decision already deferred: the convention scaffold
  (`real-world-original` → continents) is genome-carried and committed at source, but
  grown places need durable storage, and *how* grown-vs-seeded persists is the design
  question. Settle that and the cartographer becomes a scheduled cloud routine that simply
  runs.
- **A quality fork worth naming now.** The cartographer currently trusts the LLM to
  *enumerate* geography, which hallucinates at the long tail. The more rigorous shape is
  **LLM-for-voicing, dataset-for-structure**: anchor the containment tree to real
  gazetteer data (GeoNames-class) and let the LLM do only what it is good at — the human
  voicing of each place. True at scale, alive in prose.

## Trajectory B — the gazetteer into the genome (island & linked islands)

The architecturally valuable one. Today `discover.py` and `grow.py` hardcode
`real-world-original` as the root — but the *mechanism* is world-agnostic. Lifting it has
three moves, in increasing reach:

1. **Make discovery a genome current.** Every biome should serve `/resolve` + `/gazetteer`
   derived live over *its own* blocks — sensed-and-unfolded the way federation is, not
   bolted to `serve.py` for earth specifically. A biome with blocks and a door *grows* a
   resolver; that is a condition, not a configuration. (Map it to a current in the live
   shell `src/biome/constitution/biome.json` before building — per the project's "don't
   add what the shell doesn't describe" rule.)
2. **Delegate on a miss.** `federate.loader` already crosses hosts to *fetch a block*; the
   unbuilt step is a resolver that, on a name it cannot reach from its own root, asks its
   **peers' `/resolve`**. That single addition is what makes biome-DNS: each island
   authoritative for its own names, resolution by recursive delegation, no central
   registry.
3. **The lighthouse becomes derived.** Once the gazetteer is genome-level, the lighthouse
   is simply its curated top — which dissolves the standing "hand-placed cheating-prop"
   complaint *everywhere*, not just here. Every biome's front desk becomes grown, not
   placed.

This is where **"linked islands"** gets its mechanism. An island is **relational, not
locational** — forms that relate are one island though they sit on three machines
(biome-definition 3.0). The resolver-delegation graph *is* that relation made walkable.
Linking *distinct* islands (real-world ↔ the RPG commons) is then cross-island resolve
treated as labelled-foreign kin — which, note, is exactly what the STI fold needs in
Trajectory C.

## Trajectory C — engagement via mcp/spark

**Reading is already fully native.** An LLM holding the island's spark MCP can semantically
walk the world *right now* — read the ring of voicings, pick the matching child, descend;
`/resolve` gives it deterministic jumps; the door gives raw blocks; everything is free.
That half is done, and it is elegant. The work is on the other two halves.

- **The growing gap.** Because `serve.py` carries `discover` but not `grow`, the
  chain-intelligence never reaches the surface. The fork: expose `add_location` as a thin
  **door verb** (or a second mode of the spark tool) so the index-keeping stays
  **server-side and correct**, versus letting the LLM do raw multi-writes itself (more
  native, but the gazetteer rots and the guest must already know the address). Take the
  door verb — it is the one piece of wiring the spec itself flagged as remaining, and it
  is what makes "voice your own room into the shared world" real.
- **The deeper move — the room as the S-floor of the STI fold.** Locate an agent, a
  character, or a human, and [`spark.fold`](../src/spark/spark.py) lays **T** (scenes/time)
  and **I** (identity) against a *real* spatial floor (see `project_sti_frame_model`). Two
  agents who lock the same town now share a frame, and co-location becomes a
  **pscale-distance** — precisely the substrate the phase-coupling and resonance work has
  been reaching for (agents at nearby addresses couple; see `project_phase_coupling`). This
  is the bridge from "real-world island" to the agent architecture: the spatial spine STI
  has been laid against *fantasy* is now available as **ground truth**.

## The dependency order

The three are separable fronts, but they are not independent:

- **Persistence (A's gate) is small and gates the rest** — there is little point mapping
  overnight, or growing rooms through the door, into a store that resets on redeploy.
- **B is the architecturally valuable core** — the connector, lifted off the real-world
  root into a capability every biome unfolds, with peer-delegation making the web one
  namespace.
- **C proves B** — a guest adding a room (C's door verb) is the first real consumer that
  forces the resolver to answer for grown, not just seeded, content; and the STI fold is
  the payoff that makes the spatial substrate matter beyond a map.

So the honest spine is: **settle persistence → lift the gazetteer to a genome current with
peer-delegation → use the grow-door (and then the fold) as the proof.** Which front feels
most alive is the steer; this note is the map, not the order of march.
