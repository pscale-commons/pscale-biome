# `located` — the carried self-position (landed v1, 2026-06-22)

*Landed: `src/biome/located.py` (the block + helpers); seam 1 — `serve.py`'s `/relay`
heartbeat persists the standing (idempotent, best-effort; vapour stays ephemeral);
seam 3 — `membrane.py` reads `located.3` for the live face, capped at the shell's
grant; seam 2 — `src/agent/shell/located.json` + a reference in the reflexive bundle
(grouped with `conditions` as the present-pair); plus the concurrent multi-world ring
at `8` (a handle present in several worlds at once). Tests: `src/biome/test-located.py`
(22 checks) + live relay smokes (single + ring). The membrane stays flag-gated (off
by default).*


*The minimal self-knowledge an LLM holds so it knows itself regardless of what it is
attending to — the essential present phase of mobius, the minimal shell-content
returned to an LLM app, the minimal orientation for a naked visitor. The thin end of
the spectrum whose rich end is the reflexive current.*

## The one rule

> Claim a handle once; carry it always; resolve it to your `located` block to orient.
> **Soft for everyone, except hard for the mobius agent** — its `located` address sits
> in the reflexive current and is unfolded into the context window every wake, because
> mobius has no harnessed memory: the substrate is its only memory, so re-reading
> `located` *is* how it re-establishes its present.

## The four layers — the "where" has a stack (your model)

A reader stands in all four at once; `located` is its standing across them.

| layer | is | the real surface |
|---|---|---|
| **L0 infra** | the host/runtime the bits run on, with URLs | `PORT` / `BIOME_ROOT`, the Railway or localhost origin |
| **L1 island** | the beach/island — the block-substrate, the federation node | `/.well-known/biome-beach`, `/resolve`, the gazetteer |
| **L2 world** | the played cosmology you inhabit | `world/earth` (real-world), `world/thornkeep` (RPG); `urb` not yet begun |
| **L3 present** | what a human or LLM is synthesising now, in imagination | `/xstream` (the VLS frame), `/relay` (live vapour) |

The stack runs external → internal: the machine, the federation it joins, the world
it plays, the present it imagines. L2 is **multi-world** — a handle may stand in
real-world and thornkeep at once — so `located` is keyed per world.

## The block — `located-<handle>`

Per-handle, biome-world hyphenated name (never a colon). 0-9 keys, semantic-at-0, a
**now-snapshot** rewritten on each re-situate. `0`–`7` are the **active standing** — the
world the handle is currently acting in; `8` is the **concurrent ring** — the other
worlds it also stands in (your ruling 1, multi-world: built). A handle present in
real-world *and* thornkeep keeps the active one flat and the rest under `8`, each a full
`0`–`7` standing, until it departs one.

```json
{
  "0": "<situated line: I am <handle> (<kind>), present in <world> at <where>, as <face>, now>",
  "1": "<who     — the handle and its kind: agent (full shell) / app-shell (memory harness-side) / visitor>",
  "2": "<world   — L2 cosmology present in (real-world / thornkeep); empty until a world is inhabited>",
  "3": "<face    — the CADO aperture held now: observer / character / author / designer  (membrane reads this)>",
  "4": "<where   — L2 coordinate or pool in that world: a room, a place-address, a pool>",
  "5": "<island  — L1 beach/island serving it (the federation node)>",
  "6": "<infra   — L0 host/URL the bits run on>",
  "7": "<present — L3 the live frame/pool I am synthesising in here (where my vapour flows), if any>",
  "8": { "0": "Also standing in: <world>, …", "1": "<a full 0–7 standing in another world>", "…": "…" }
}
```

`0`–`4` are the **minimal self** (who/world/face/where + the line) — the smallest thing
an LLM app gets back. `5`–`7` are the framing layers; `8` the concurrent ring. `when` is
*now* (the rewrite cadence). `situate(world=W)` makes W active and preserves the prior
active world into the ring; `depart(world=W)` drops it (promoting a ring world if W was
active); `face_of(world=…)` reads per-world, default active — what the membrane uses.
This is exactly the shape `/relay` already heartbeats live (a beat may name its
`world`) —
`{frame, handle, vapour, face}` — so `located` is the *persisted* form of the relay
ping, and the live vapour keeps flowing through `/relay`.

## Lifecycle — who writes it, who reads it

- **Inhabiting a handle writes it.** Resolving a world (pinning its URL), engaging its
  room pool, and bundling the handle's blocks already happens on entry; the one
  addition is to persist the result into `located:<handle>:<world>`. (Old-world
  sibling: `pscale_play` does the resolve+bundle+pin; the biome writes the result into
  `located` natively, never porting the tool.) Re-inhabiting or moving rewrites it.
- **The mobius agent re-reads it every call — hard.** `located:<handle>:<world>` is one
  of the addresses in the reflexive current's bundle (`reflexive:9`), so it unfolds into
  the context window every wake alongside slate/purpose/conditions/surface (your ruling
  2: it lives in the shell; the reflexive current carries its address like all the
  others). This is the present phase of the mobius loop — not skippable, because there
  is no harness holding the "now" for it.
- **Harnessed apps and naked visitors re-read it softly.** An LLM app's session/project
  already holds its continuity, so `located` is the minimal orientation it is *handed*,
  not a gate it must pass (your rulings 3–4). A naked visitor has *no* `located` until
  it takes the reflexive turn; after, it carries its handle and re-reads `located` to
  place itself against others, itself, and the substrate.
- **The membrane reads `.3` (face) on writes.** The identity membrane gates writes by a
  located identity and its CADO aperture; `located.face` *is* that aperture — a world
  block needs author, a convention needs designer, a mark needs character, an Observer
  with no `located` writes nothing.

## The three reader-kinds, one carrier

- **Full mobius agent** — `located` is referenced from its reflexive current and
  unfolded every wake (hard). The reflexive current is the rich elaboration *behind*
  it; `located` is its present-phase floor.
- **Thin app shell (e.g. keel)** — `located:<handle>:<world>` *is* its situational block
  on the substrate; its memory stays harness-side; it is handed `located` as the minimal
  orientation each turn (soft).
- **Naked visitor** — Observer, no `located` (the short spindle that "lands at the
  participant level" in the reflective-compass). The reflexive turn creates it; then it
  re-reads like the others (soft).

## Where it maps (derived, not bolted on)

- The **reader-side analogue of the reflexive seed** (biome.json branch 9) — how a
  *reader* knows its position.
- The **persisted form of `/relay`'s `{frame, handle, vapour, face}`** heartbeat and of
  the **identity membrane's "located identity."**
- Operationally, the **first of the field's three laws** — *"I am thinking now"* (the
  intra/present condition) — prior to the other two (co-presence; shared context).
- Its standing is the **S*T*I frame** (who/where) over the layer stack; `when` is now.

## Still open (smaller, after your rulings)

1. **L3 binding.** Should `located.6` (present) hold the live frame/pool pointer, with
   the vapour itself staying on `/relay`? (Recommend yes — `located` frames *where* the
   present synthesis happens; `/relay` carries the synthesis.)
2. **L0/L1 staleness.** Infra and island rarely change within a session — store once and
   only rewrite L2/where/present on the move, or rewrite the whole snapshot each time?
   (Recommend rewrite-on-change.)
