# Hand-over — the face session: the biome's human surface (the xstream-form)

You're unfolding the biome's **browser surface** — the form where a human
inhabits the biome directly. This is NOT a chat-bot wrapper around the agents
and NOT a separate deployment: it is the same biome serving one more surface
through the same code, per the founding rule (biome-design.md, out-of-scope:
"do not create three separate deployments"). Read `CLAUDE.md` first (two-worlds
boundary, naming rules), then `docs/handover.md` for full state.

The shell already names this form:
- cognition 2.3 — "a human at the browser provides cognition by typing"
- endpoints 3.3 — "browser interface at /xstream; humans inhabit the biome directly"
- concurrency 2.4 — the target: "embedded LLM + human in the browser + connected
  app via MCP, each writing to the same shell from a different vantage"

## What exists (don't rebuild)

- **The commons** — `https://biome-commons-production.up.railway.app`:
  `serve.py` (stdlib HTTP) already serves `/mcp`, `/.well-known/biome-beach`,
  and `GET /` (the arrive block as JSON). Custom endpoints are sanctioned
  (shell 3.6). The same service hosts the face page — locally it's the same
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
3. **Address the collective**: a given-box — the text lands in an agent's
   `conditions` as "a visitor's given, awaiting the next wake". NO key needed:
   givens accumulate and fold on the collective's own cadence. (Optional
   accelerator, later increment: BYOK — visitor key triggers a pulse now;
   key used per-request, never stored/logged/echoed.)
4. **Watch**: poll the surfaces/chronicle for what changed since your visit.

The human's typing IS the cognition (2.3) — v1 needs no LLM calls at all.

## Increments after v1 (each its own decision with David)

- VLS zones as interface discipline (vapour = unsent drafting in page state;
  liquid = marks/proposals; solid = settled voicings) — xstream's actual
  semantics, layer 1, distinct from the Limen's unplaced/held/fixed (layer 2).
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
