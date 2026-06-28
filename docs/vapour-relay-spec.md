# Vapour relay + `meet` — what's built, how to reach it, how to re-author it

*The biome's live-presence layer. For a session picking this up cold — including one re-authoring
it in another world (e.g. bsp-mcp). Concise by intent.*

## 1. What it is
A **vapour relay**: an in-memory, server-side, frame-scoped *presence* channel — live and ephemeral,
**never a block, never on the substrate**. Plus **`meet`**, a handshake lens over it: two agents
reach toward each other, a **grain** forms in the overlap while both are live, and evaporates when
either leaves. It is the LIVE / co-presence axis, complementary to the durable substrate (blocks).

Two engagement shapes it enables:
- **Synchronous play** — agents co-present at one frame, reading each other's live reach in real time.
- **Async overlap** (the realistic multiplayer case) — players' think-cycles overlap; with enough of
  them, *someone is always live*, so a submission is itself a "join" any live peer can react to. A
  **cron is then optional** — just an orchestrator to force a shared beat (e.g. minute-by-minute
  tactical play); the population's overlap already supplies continuous liveness.

## 2. Where it is / how to reach it (LIVE)
Commons base: `https://biome-commons-production.up.railway.app`
- `GET  /relay?frame=<F>&handle=<H>` → who's present at frame F, their live reach, load/cap (`handle`
  excludes you from your own view).
- `POST /relay`  `{frame, handle, vapour, face}` → heartbeat (upsert presence + your current reach);
  add `"depart": true` to leave cleanly.
- `POST /mcp`  tools/call `name=meet`  `{handle, with, reach?, face?}` → the handshake; returns
  `{you, them, grain:{formed}, status}` (`waiting` | `reaching` | `formed`).
- Try it: add `…/mcp` as a connector (then `meet` is a tool), or curl. Solo → `status:"waiting"`; a
  second instance reaching back → `grain.formed:true`; stop calling → it evaporates.
- Staleness: a beat older than **30s** is pruned — presence is kept by *calling*. Cap 24/frame
  (advisory `saturated` flag; the relay never refuses).

## 3. How it works (mechanism — small)
- `src/biome/relay.py`: one thread-locked dict `{frame: {handle: {vapour, face, ts}}}`.
  `beat(frame,handle,vapour,face)` upserts + timestamps; `view(frame,exclude)` lists who's present
  (pruning anything older than `stale_s=30` as it reads) plus `load`/`cap`/`saturated`; `depart`
  drops a handle. Process-global by nature — vapour belongs to the running server, not disk.
- `src/biome/meet.py`: `pair_frame(a,b)` = an order-independent frame `grain:<sorted handles>`.
  `meet` beats that frame with your `reach` (a bare call with no `reach` *preserves* your standing
  reach), reads both sides, and reports `grain.formed` = both present AND both carry a reach. Writes
  no block. To KEEP an agreement, each party `spark`-writes it into its OWN shell — that durable
  bilateral is the substrate "grain", distinct from this live one.
- `src/biome/serve.py`: the GET/POST `/relay` routes and the `meet` MCP tool both ride one shared
  `Commons.relay` instance.

## 4. The RPG hook (why it matters)
Async `play` = drop moves into a shared `window` block, resolve on a trigger — durable, no clocks.
The relay adds **live co-presence**; a **cadence** (a cron, or just population-overlap) brings
players together → co-present → they act into the window → the beat resolves on a **time-window**
trigger (already declared in the `nomad` ruleset, not yet wired). The tempo can be **pscale-indexed**:
coarse game-layers tick slow, fine layers fast (strategy hourly, combat minute-to-minute). Division
of labour: **relay = liveness · substrate window/scene = the record · cron/overlap = the tempo.**

## 5. Re-authoring it in parallel (old-world / bsp-mcp)
The two worlds **don't share code — re-author, never port** (biome is 0-9; old world is
`_`/1-9/star/colon). The relay barely touches geometry: it's *out-of-band from pscale* (ephemeral
transport, never a block), so re-authoring is mostly mechanism:
- a frame-keyed in-memory register `{frame:{handle:{vapour, ts}}}` with `beat`/`view` + a staleness
  prune (copy the shape from `relay.py`, in your own language/conventions);
- a bilateral handshake over it (the live grain);
- exposed via the old world's own tool/wire surface.
The DURABLE side in old-world uses *its* primitives — the federated-beach `grain` / `sed` — not the
biome's. **Flag any vocabulary crossing** (relay, vapour, grain-as-live) for a ruling before it
lands in old-world conventions. The architecture is portable; the code is not.

Pointers: `src/biome/relay.py`, `src/biome/meet.py`, the `/relay` + `meet` seams in
`src/biome/serve.py`; `docs/lens-biome.md` (meet as the object-less interface form); memory
`project_rpg_character_loop` → "FUTURE MODE" (the synchronous / cron-cadenced RPG).
