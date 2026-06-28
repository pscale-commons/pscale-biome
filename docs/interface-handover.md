# Hand-over — the interface session: the biome's human surface (the xstream-form)

You're unfolding the biome's **browser surface** — the form where a human
inhabits the biome directly. This is NOT a chat-bot wrapper around the agents
and NOT a separate deployment: it is the same biome serving one more surface
through the same code, per the founding rule (biome-design.md, out-of-scope:
"do not create three separate deployments"). Read `CLAUDE.md` first (two-worlds
boundary, naming rules), then `docs/handover.md` for full state.

**The standing frame (ruled 2026-06-13):** nothing runs that isn't wanted.
The value loop is the only closure that matters — no idle cron, no heartbeat
scheduler. Agents wake because a given landed (event cadence, shell 7.2): one
pulse per ask, cost at the moment of demand. Frame is not a block-type here —
**a frame is the fold-read** (S + T + I + presence at one address, one grain;
fold-synthesis 3.2/4.0): the page's main view IS a frame. Vapour needs no
Supabase and no websockets at this scale — **vapour-by-poll** through the door
(shell 3.4 sanctions blob-poll); SSE is a later upgrade. The RPG needs no pool
machinery — the Limen's attestation mechanic (unplaced/held/fixed, the Weigher)
IS the objective structure, re-derived in-world.

The shell already names this form:
- cognition 2.3 — "a human at the browser provides cognition by typing"
- endpoints 3.3 — "browser interface at /xstream; humans inhabit the biome directly"
- concurrency 2.4 — the target: "embedded LLM + human in the browser + connected
  app via MCP, each writing to the same shell from a different vantage"

## What exists (don't rebuild)

- **The commons** — `https://biome-commons-production.up.railway.app`:
  `serve.py` (stdlib HTTP) already serves `/mcp`, `/.well-known/biome-beach`,
  and `GET /` (the arrive block as JSON). Custom endpoints are sanctioned
  (shell 3.6). The same service hosts the interface page — locally it's the same
  code on 3210 in Chrome, even against the courier-stick's carried world.
- **spark.ts** — at parity (34/34). The page can operate blocks client-side:
  fetch whole blocks through the door, walk them with spark.ts in the browser,
  write through the door (the membrane judges, same as any guest).
- **The inhabitants** — the collective (v007, David's machine), the mind,
  keel, the courier; surfaces at `surface-*`, story at `chronicle`, world at
  `thornkeep`/`scenes`, ledger at `marks`, orientation at `lighthouse`.

## v1 — the inhabitable page (one session)

A single HTML page (no framework needed; spark.ts + fetch) served at `/xstream`
(keep `GET /` as arrive-JSON for arriving agents):

1. **Read the place**: render lighthouse (who's here, what's growing), the
   world (thornkeep + scenes at the same addresses — show the fold!), the
   chronicle (the story so far), the marks (the ledger), the surfaces (who
   you're among).
2. **Act as an inhabitant**: leave a mark (next free digit, signed); propose a
   sibling at a place (a shaped write through the door — the same geometry
   everyone uses).
3. **Address the collective — given-triggered wakes**: a given-box; the text
   lands in an agent's `conditions` as "a visitor's given" AND triggers one
   pulse for that agent (event cadence — the wake happens because someone
   asked; ~$0.05 on the steward's key per response at nursery scale; BYOK
   per-request keys are the later increment for strangers). One pulse per
   given, a per-day cap, never an idle wake.
4. **Watch**: poll the surfaces/chronicle for what changed since your visit.
5. **The frame view**: the page renders a chosen address as the fold — place
   (thornkeep), happenings (scenes), who (characters + presence) — one scene,
   one read. This is the load-bearing view; prove frame-as-fold here.

The human's typing IS the cognition (2.3) — v1 needs no LLM calls at all.

## Increments after v1 (each its own decision with David)

- VLS zones as interface discipline (vapour = unsent drafting, visible to
  co-present others via vapour-by-poll through the door; liquid = marks/
  proposals; solid = settled voicings) — xstream's actual semantics, layer 1,
  distinct from the Limen's unplaced/held/fixed (layer 2).
- The I register (now the **per-handle personal block at the same address** —
  `fold.py`; not a single characters block — see *Personal and social versions*
  below) + the action convention (a character's act is a given; the world folds
  the consequence into scenes) — step 2 of the one path: the RPG becomes enterable.
- BYOK pulse acceleration (the trust contract: per-request, never stored).
- CADO faces (character/author/designer/observer) as view+permission modes.
- The collective resident on the volume (only matters once pulses trigger
  server-side; givens-accumulate works with the collective wherever it lives).

## Constraints (hard)

- One deployment: the page is served by serve.py — no Vercel, no second repo.
- Layer discipline: interface words (vapour/liquid/solid, faces) are layer 1;
  the Limen's words (unplaced/held/fixed, Ashen Market) are layer 2 — the page
  may DISPLAY world vocabulary but never adopts it for interface states.
- Sovereignty: a visitor writes marks/proposals/givens — never an agent's
  purpose or surface; agents fold givens themselves.
- Transparency: the page shows what it reads and writes (addresses visible —
  the geometry is the UI, not hidden behind it).
- The membrane judges all writes (digit keys only) — the page composes legal
  shapes rather than free JSON.
- No xstream vendoring: `src/xstream` is stale reference. Re-derive; the
  three-zone discipline arrives as a deliberate increment, not a port.

## Open decisions for David

- Page aesthetics/voice (this is the first thing outsiders see).
- Which agent receives a visitor's given (route, broadcast, or visitor picks).
- Whether the Observer chronicles visits (recommend yes).
- When the public collective cut happens (volume-resident v008, carrying the
  Limen up) — not needed for v1.

---

# Increments since v1 (2026-06-21) — the fold layer, the versioning model, the receptive/projective split

The v1 brief above predates `src/biome/fold.py` (the frame/engagement layer, built
2026-06-21) and the real-world spatial island. These three sections record what is
settled since. (Naming: the page is `src/biome/interface.html`, served at `/xstream`
— `face` is reserved for CADO.)

## Agents and humans are one VLS, asymmetric only on vapour

The genome treats agent and human identically — both are cognition sources
(`biome.json` current 2). They share one substrate and one VLS grammar; they differ
only by **door** (biome-mcp primes an LLM; xstream primes a human) and by **how each
is live**:

- A human **listens concurrently** — constructs the world in the moving now,
  continuously, in parallel. Vapour serves this: live, letter-by-letter co-presence
  (the relay), so others' forming thoughts are visible as you form yours. This is
  *receptive* liveness.
- An LLM processes an **instance** — a concatenation/summary read in one pass. Its
  receptivity is already a whole-context read at wake; it does not need a live vapour
  stream to be co-present. Feeding it one is possible but expensive and largely
  redundant. **So an agent engages at liquid (submitted reading) and solid
  (committed)** — the durable registers — not at vapour.
- **MAGI is the anti-pattern for "separate entities."** A shared context window
  stuffed with neighbours' shell content is the systemless way to fake the human's
  concurrent now onto LLMs — it lives wholly in the receptive state. The biome's
  separate-entities model is the opposite: separate contexts, each with its own
  (possibly conformal) purpose block, meeting *through blocks*. The blocks carry the
  parallel-contemporaneous structure a human gets from concurrent listening — which
  is why no shared window is needed. (Genome 2.4 "each writes to the same shell from
  a different vantage" — shared *substrate*, not shared *context* — vs 5.3 MAGI.)

The LLM does have a live mode, but it is **projective, not receptive** —
*fragmentary projective forking* (David's, a version built): as text arrives, predict
the continuation at several rates (pscale −2 every few seconds, −1 every minute, 0
every few minutes) and compare the prediction to what actually arrived since the last
calculation. *cogito* read as *dubito* — the live signal is the **discrepancy**.
Costly in general; cheap enough at the fine scale on a **local** LLM to be feasible.
This is the LLM's vapour, and it is an optional increment, not a need. The pscale-rate
ladder is the cadence/WHEN-axis extended *below* the floor — the moment decomposed
into finer grains.

**Design consequence — the interface is asymmetric by design:** `/xstream` carries a
live receptive vapour zone (the relay); the agent door carries none — read
liquid+solid at wake, and *optionally* run a local projective-fork as native
(projective) liveness later. Same VLS substrate, two apertures onto vapour.

## Personal and social versions — the fan and the fold

Any agency can hold its own observation at *any* coordinate, at the *same* address as
the defined one — because a pscale coordinate is a position in scale-space holding a
**fan** of voicings, not a cell holding one value (the inversion, at the substrate).
The registers:

- **original / defined** = the `1⁰` public voicing on the shared spine (the
  view-from-nowhere) — the world block.
- **personal** = the **I-register**: your voicing at the *same* absolute spindle, in
  your *own* block. Built: `fold.py` `personal_loader` / `account_at`, per-handle
  (`world/identity/<handle>.json`). Scale-free — a note at a region (pscale 4) as
  readily as a room (pscale 0).
- **social, as liquid** = the **fan**: gather every handle's account at one address
  (`fold.fan`).
- **synthesis, as solid** = the **social fold** (`fold.social_fold`): derived
  reader-side (`1⁹`), never stored as truth — the same discipline as the gazetteer.
  Solid is **personal or collective**: a self-committed personal version, or the
  collective fold optionally settled back as the new public `1⁰`.

The fan/fold split is the truth/derived split: the fan is substrate (real
contributions); the fold is a derived surface (reader-side, VLS-presented, optionally
cached).

**Evolution of solids is a per-world choice — persistence (current 4) × the WHEN-block
(cadence), never a hardcoded policy.** Keep prior solids (forkable, valid-time,
history-accurate) — for legacy systems that roll back. Or keep only the current solid
(overwrite, concurrent-reflection-accurate) — David's read for the real-world spatial
island: it is the current accurate model; previous versions are abandoned (until we
can afford valid-time). One block field per world, not two architectures. (The xstream
protocol already reserves the slot: per-entity position `3` = history.)

## The seam — `fold.py` has no interface

The versioning model above *is* `fold.py`, verified end-to-end — but it lives only in
Python, surfaced by no door or page. Meanwhile `/xstream` (`interface.html`) renders
VLS for the RPG, and the real-world island's `/world` walks the spine but shows only
the public `1⁰`. These are **three thirds of one interface**:

- `/world` — the spatial walk (telescope down the coordinate),
- `fold.py` — the frame (bind S·T·I at the floor; render *public version / your
  version / the social fold*),
- `interface.html` — the VLS zones (vapour live, liquid staged, solid settled).

The highest-leverage next build is to **render the fan-and-fold as VLS in the
interface** — keyless to read, door-gated to write, identical in shape for both doors.
A human opens a place and sees the public description (solid `1⁰`), their own (their
I-register, editable → personal solid), and the room's collective sense (the social
fold, derived). An agent does the same through `spark`/`fold`. Still spec, not code.
