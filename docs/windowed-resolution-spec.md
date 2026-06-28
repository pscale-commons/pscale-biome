# Windowed resolution — spec for a new session

The **core multiplayer resolution process** for the biome RPG, re-derived from the
bsp-mcp / pscale-beach **"in-loop resolution"** pipeline into biome-world (0-9).
This is the brief; a new session builds it. It **replaces the placeholder** in
`src/biome/resolver.py` (commit → gather current liquid → one synthesis), which
has no window, no self-clock, no dice/skeleton layer, and no timing.

## Discipline (read first)

- The prior art is **OLD-WORLD** (`_`/1-9, Redis, star-doors). Read it as
  **reference** — the *algorithm*, not the storage. **Re-derive in 0-9; never
  port** the `_`, the star, the Redis specifics. (Two-worlds boundary, CLAUDE.md.)
- **Rules live as blocks** (the `mechanic` flint); the kernel only routes — the
  de-crystallisation the resolver hand-off established (`docs/rpg-resolver-handoff.md`).
- `serve.py` stays **keyless** (door + face + relay). The resolver/medium is the
  **cognition** current — keyed, a form beside the door.
- The RPG bench `src/rpg/` (tiers.py/play.py) is the **behavioural reference** —
  do not extend it; de-crystallise.

## The model (David's, confirmed by the prior art)

Resolution is **asymmetric and self-clocking** — no central scheduler:

1. A commit with **no open window opens one** — a claim for the next *D* seconds
   (the window). Commits landing inside it **join**.
2. The window **closes lazily**: there is no cron — the next participant computes
   `open_ts + D ≤ now`.
3. The **first commit after close does both**: it **resolves** the gathered
   window **and opens the next** (and joins it). The resolution cost is borne by
   the next committer; nothing in the middle holds the clock → it scales and
   federates.

Resolution itself is **layered** (don't spend the LLM on dice — spend it on the weave):

- **dice / skeleton** (mechanical, cheap, batched): per-action calculated
  outcomes, **deterministic** — seeded from the window's open-stamp so they are
  fixed before any resolver reads them and cannot be gamed by editing a
  submission. No LLM.
- **ONE synthesis** (the magic): a single medium-LLM pass that weaves *all* the
  dice outcomes + the intentions + the **commit timings** + semantic fit into one
  canonical moment. One-per-window, never one-per-commit.
- **per-character render** (aperture'd): each character renders that moment
  through its own knowledge/standpoint (second person) into its **own history** —
  the narrative sequence the character accumulates. (From the rig hand-off:
  soft-render → the character shell's history.)

## The prior art (reference only — pscale-beach + bsp-mcp)

The pipeline lives in **pscale-beach** (`src/pscale-beach.js`, the `winres`/append/
sweep primitives); **bsp-mcp** is read-only reference (`src/tools/pool.ts`,
`proposals/2026-06-05-in-loop-resolution.md`, `function:thornwood` directive).
Verified by two readers, 2026-06-16. The mechanism:

- `liquid:pool:<room>` — the window. One slot per author (OVERWRITING — revisable
  pre-commit mirror). Root carries `"Window opened <ISO-ts>."` — **immutable for
  the window's life** (a withdraw/resubmit never moves it; that stamp is the dice seed).
- **Close** = `open_ts + duration ≤ now`, duration from a directive (default 90s).
  Detected by the **next toucher**, not a clock.
- **In-loop order** per touch: (1) if a window is due, **resolve it** (wear the
  medium aperture) and clear the liquid; (2) **perceive**; (3) **act** (submit →
  open/join the next window).
- **Single-resolution**: the resolver writes with `resolves_window=<open-ts>`; the
  store does atomic `SET-NX` on `winres:<pool>:<stamp>` — first wins (200), others
  get `409 window_already_resolved` and **stand down** (re-read the skeleton, render it).
- **dice**: exploding-d10, sha256-seeded from the window stamp; **handed** to the
  resolver, who is forbidden to invent them.
- **skeleton** → public `pool:<room>` (append, permanent), actors by **handle**
  (never a learned name), terse, no colour. **render** → private `witnessed:<handle>`
  (each character's history), names-as-known, depth-limited, the colour.
- **timing**: ISO-8601 timestamps on every entry; order within a window by slot,
  across windows by timestamp; each character keeps a **read marker** into the pool.

## The derivation (biome 0-9)

### Blocks (digit-keyed, membrane-legal — no `_`; `0` is the node meaning)

- **`window`** — the open window for the scope:
  `{0: "the open window at <scope>", 1: <open-ts>, 2: <duration-seconds>, 3: <resolved-ts or "">}`.
  (One per scope/pool; or `window-<scope>` if several scopes run at once.)
- **`liquid-<handle>`** — a participant's staged intention (per-handle, race-free):
  `{0: "<handle> — submitted", 1: <scope>, 2: <intention>, 3: <submit-ts>, 4: <window-open-ts>}`.
- **`scenes`** — the pool (append-only committed outcomes). Each resolved window is
  one entry: `{0: <the ONE synthesis — the public scene>, 1: <the skeleton/dice facts>, 2: <window-open-ts>, 3: <resolved-ts>}`.
- **`character-<handle>`** — the character shell as blocks: `{0: meta, 1: purpose
  (Character Force), 2: bind, 3: conditions, 4: history, 5: perceived}`. History (4)
  is where the per-character render lands and the narrative sequence grows.
- **`mechanic`** — the verbs (flint), grown (see below).
- **`claim-<window-open-ts>`** — the single-resolution lock. The biome's `SET-NX`
  equivalent: **create-locked-if-absent** (membrane lock rule R1 — "block does not
  exist + new_lock → create locked"). First resolver to create it wins; others find
  it present and **stand down**. (See "the atomic-claim gap".)

### The window lifecycle (self-clocking)

```
on commit by <handle> at <scope> (intention I):
  W = read(window @ scope)
  now = server time
  if W absent or W.1(open) + W.2(duration) <= now:        # no live window, or it closed
      if W present and W.3(resolved) == "":               #   a closed-but-unresolved window
          RESOLVE(W)                                       #   ← this committer resolves it
      open a fresh window: write(window) {1: now, 2: D, 3: ""}
  write(liquid-<handle>) {1: scope, 2: I, 3: now, 4: <current window open-ts>}   # submit / join
```

`RESOLVE(W)` (only if the committer wins `claim-<W.open-ts>`):

```
1. CLAIM: create-locked claim-<W.open-ts>; if it already exists → STAND DOWN (someone else resolves).
2. GATHER: every liquid-<h> whose 4 == W.open-ts and 2 != "" — the window's acts, with timings (3).
3. DICE / SKELETON (mechanical, no LLM — NOMAD): seed exploding-d10 from W.open-ts; per act:
   outcome = CF (Character Force, the shell's stat block) + SF (Situation Force, place/skill
   rules) + dice − difficulty (default 5) → an outcome band, per the action class. (See NOMAD below.)
4. ONE SYNTHESIS (medium-LLM): weave all skeleton outcomes + the intentions + their
   timings (3) + semantic fit → ONE public scene. Append to scenes {0: scene, 1: skeleton, 2: W.open-ts, 3: now}.
5. RENDER (per character, soft-LLM): each present character renders the scene through
   its aperture → append to character-<h>.4 (history). (Optional in v1; the public scene is the floor.)
6. CLEAR: blank the gathered liquid slots (2: "") and stamp window.3 = now (resolved).
```

### The verbs (`mechanic` grows — rules as blocks)

Current: `1` compose-frame · `2` soft-act · `3` medium-resolve · `4` soft-render · `5` settle.
Re-aimed / added for windows:

- `1` **compose-frame** — unchanged (the aperture'd window; NOW = the character's own
  perceived, not the omniscient record).
- `2` **soft-act / submit** — a character (LLM or human) perceives only its window and
  submits one intention to liquid. (Human typing OR a character-LLM — same liquid.)
- `3` **roll / skeleton** (NEW, mechanical-with-a-rule) — given the gathered acts +
  Character Force + Situation Force + the seeded dice, state each act's calculated
  outcome. The *dice* are code (deterministic from the stamp); this rule says how CF/SF/dice combine.
- `4` **synthesise** (the magic) — weave the skeleton outcomes + intentions + commit
  timings + semantic fit into ONE canonical public scene. (≈ today's medium-resolve,
  but fed the dice outcomes and the timings, not the bare intentions.)
- `5` **render** — per character, second person, only what it perceives, discovery-by-action; → history.
- `6` **settle / aftermath** (from the resolver hand-off) — write the public aftermath
  into the aperture channels (space/HERE + the collective-I head + time/NOW) so a later
  player perceives the consequence through the place; private circumstance to world-truth.
- The **window duration D** is config — a `mechanic` field or per-place in the `frame` recipe.

### Timing

Server time is available in `serve.py`/`resolver.py` (Python `time`) — note spark/
workflow scripts forbid `Date.now`, but this is server-side, fine. Every submission
and scene carries a timestamp; window-close = `open + D ≤ now`; each character keeps a
**read marker** (last-read `scenes` slot) so render only folds new outcomes.

## NOMAD — the basic game system (reference: `~/Projects/nomad-bsp`)

NOMAD is the game system at **pscale sublayer 2** (game-system — above the substrate,
below world-content). Authoritative source: `~/Projects/nomad-bsp`, currently a v0.0.1
**placeholder** (`seeds/nomad-rules.json`, `seeds/dice-config.json`) carrying the **core
formula** and referencing the full ruleset in onen-play docs (`core-gameplay-v9.md`,
`NOMAD-Plex0-Implementation.md`) — **not present in these repos**. Basic NOMAD is enough now:

- **Formula:** `outcome = CF (Character Force — stats + advantages) + SF (Situation Force —
  environmental factors) + dice (exploding d10) − difficulty (default 5)`.
- **Action classes:** SIMPLE (auto-success) · RISKY (self-risk) · COMBAT_NPC (vs NPC) ·
  COMBAT_PC (vs character — a combat_type matrix: mutual / offensive / defensive).
- **Outcome bands:** >10 overwhelming · 5–10 clear · 0–5 marginal · 0 stalemate · −5–0 minor
  fail · −10–−5 significant · <−10 catastrophic. Damage applied per action class.

This is the **skeleton** math (verb 3): mechanical and deterministic given the seeded dice.
Hold it as a biome-world block, **re-authored in 0-9** from nomad-bsp's `_`-keyed seeds
(reference, never ported). The full onen-play port is a later, separate task — basic NOMAD
(the formula + bands + classes) is the v1 skeleton.

## What exists now (to replace / extend)

- `src/biome/resolver.py` — the **placeholder** (commit-signal → gather → one synthesis).
  Becomes the windowed kernel above. The `--watch` loop becomes either the
  single-resolver (the v1 fallback) or just the timing heartbeat.
- `src/biome/world/mechanic.json` — grows verbs 3 (roll/skeleton) and reaims 4 (synthesise).
- `src/biome/interface.html` — submit/commit already write `liquid-<handle>` / a `resolve`
  signal; in the windowed model **commit = a normal submit that may also trigger the
  due-window resolution**. `/xstream` is the **watch** surface (read scenes + spy + chronicle).
- The door / relay / membrane — unchanged substrate.
- **Characters must be blocks** (`character-<handle>`) — seed the cast from the RPG
  bench's file-dir shells.

## Single-resolution & scalability (ruled 2026-06-16: by pscale, not federation)

There is **no federated version** (David). Scalability comes from **pscale**: a scene is a
handful of player-characters around **pscale 0** (the magnitude point — the room, the lived
moment), so each window is naturally small. Many scenes run independently; **higher-pscale
resolution** — aggregate decisions over large numbers of people and events — is the *same
windowed move applied at a coarser pscale*, deferred (not built now). The system scales by
**pscale-decomposition** (many small p0 windows), never by federating one big resolution.

Because a scene is small and single-instance, single-resolution is simple — no Redis, no
federation:
- **v1 — a single resolver per scene**: one keyed resolver resolves a scope's due windows;
  no race because only it resolves. Trivial and correct. Use this first.
- **later — committer-resolves with a light claim**: if resolution should be event-driven
  (no idle loop, per the standing frame), the first committer after close creates a
  `claim-<stamp>` block (membrane rule R1, create-if-absent); others find it and stand down.
  A light single-instance claim — not the old Redis SET-NX.

The asymmetric self-clock (commits open/close the window) is the **timing** model and holds
either way; the choice above is only *who runs the synthesis*.

## Ruled (2026-06-16): the per-character render is coloured

The **per-character render is definitely coloured for that character** (David) — the
private, apertured retelling into its history is *the* personalised layer. The **public
synthesis/skeleton's richness (terse vs rich) is NOT yet ruled** — leave it a knob: the
medium may write the public moment terse (bsp-mcp's way, colour all per-character) or rich
(one vivid public scene); decide once we see play. The constraint that holds regardless: a
per-character render may **omit and recolour** from its aperture, **never add** beyond the
public outcome + that character's own knowledge.

## Edge cases

- **Empty window** (no submissions) — never opens; next submit opens fresh.
- **No committer after close** — the window waits, unresolved, until the next commit
  (async; fine for continuous play). Optional: the watch-loop sweeps stale windows.
- **Solo** — duration can be ~0 → the next touch resolves immediately. Same machine.
- **Race** — see the claim gap.
- **Conflicting intentions** — the resolver writes ONE outcome from both (no veto); each
  character renders it through its frame.
- **Stale / legacy** — n/a in a fresh biome; the stamp is always written on open.

## Decisions — ruled (2026-06-16) and remaining

**Ruled:**
- **Dice** = NOMAD's **exploding d10** (roll a d10; on a 10 roll again and add, until a
  non-10), seeded deterministically from the window open-stamp.
- **Resolution math** = basic **NOMAD** (see below): `outcome = CF + SF + dice − difficulty
  (default 5)`, read into outcome bands, per action class. Basic NOMAD now; full onen-play later.
- **Window duration** = **30s** to start, but **designer-set in a pscale block** (the
  `frame`/`mechanic`) and later possibly pscale- and player-count-dependent — so make it a
  *block field the resolver reads*, never a constant.
- **Per-character render** = coloured per character (above). Public synthesis richness = a knob.
- **Single-resolution / scale** = single-resolver per scene for v1; scale by pscale (above).

**Remaining (new session, with David):**
- **CF / SF block shape.** CF is a **character stat block** in the shell; NOMAD is *flexible*
  — each character may arrange its own stats (not D&D's fixed columns). SF comes from the
  place + a **skill / situation block**. David's lean: like the S*T*I fold (same spindle,
  changing block), with **reference-leaves to skill / culture / role blocks** (hand-to-hand ·
  dagger · sword; or fighter · rogue) — the biome-native form of the old star-jump (refs are
  plain leaves here, never `_`/star). Start minimal (a flat CF stat block + a per-act
  difficulty); grow the skill/culture/role refs as play demands.
- **Public synthesis richness** — terse vs rich (the knob above), settle by play.
- **Higher-pscale resolution** (aggregate over many people/events) — deferred.

## Boundaries

Re-derive, never port (`_`/star/Redis stay in the old world). Rules as blocks. `serve.py`
keyless; the resolver keyed. Characters and world and verbs are all blocks; the kernel is
spark + the window loop + the membrane, knowing none of the rules.
