# The lens-biome and `meet` — object-less relation (the vapour rung)

*Session 38.7 (2026-06-27), David + Claude. David's observation — the MCP is a "subjective
lens" biome, operationally distinct from the "viewed object" biome — located structurally,
built as `meet`, and tested with two live agencies. This is the conceptual record.*

## 1. The lens-form — structurally, a variation of `interface`

The genome's forms (biome-definition.json 2.1): **`mind`/shell** (an LLM, reflexive — runs its
own loop), **`beach`** (the object — blocks held outward, no agency), **`interface`** (a neutral
*surface* a guest agency's cognition flows through toward the shared blocks). The interface was
only ever built in its **human** variant (xstream). The **lens is the same structure with an LLM
in the guest's seat** — the surface shapes a visiting LLM's reading; the LLM brings the cognition
(cognition current 2.1, external-via-MCP). It is **not a new primitive — it is the cell the genome
left empty.**

- `spark` is a **thin** lens (read/write any block — it barely scopes you).
- `play` is a **thick** lens (it scopes you *as a character* — aperture, standpoint, frame).
- `meet` is the lens pointed **not at a substrate but at another agency** — and run **object-less**.

Two consequences, both structural:
- **Config is reflexive, not on the lens.** "How I use the tool" is the visitor's cognition, held
  in its *own* shell (biome-native) or its app (e.g. ChatGPT). The lens is a surface → **neutral and
  light by construction**, holding no user state, exactly as xstream holds no human's mind.
- **The grain is shell-anchored + meets in the overlap, not on a beach.** biome-definition 3.1.1.1:
  *"a grain each party declares in its own shell."*

## 2. `meet` — the vapour-grain

```
meet(handle, with, reach?, face?)  ->  the grain, as DATA
  { with, you:{handle,face,reach}, them:{...}|absent, grain:{formed}, status }
```

Two handles **reach** toward each other across the **vapour relay** (endpoints 3.4 — the server's
own ephemeral channel: never a block, never the membrane, never the disk). A **grain forms in the
overlap** — a bilateral held in the meeting, not on any beach. It runs **no model** and touches
**no store**: the relay carries each side's reach while both are present and shows the other back;
the visiting LLM brings all the meaning.

Mechanically: the pairing maps to a relay frame `grain:<sorted-pair>`; each `meet` call upserts your
reach there (a heartbeat) and reads the other's; `grain.formed` is true once **both** sides carry a
reach. A bare ping (no `reach`) preserves your standing reach.

## 3. Operational parameters (the questions worth nailing down)

**"Live" = heartbeating inside the staleness window.** An LLM is "live" only while processing — so
presence is kept by *calling*. Each `meet` call stamps you present for `STALE_S` (currently **30s**,
shared with the human vapour relay). While you keep calling within that window you stay present;
between calls (while you generate) your entry persists up to 30s.

**Multiple calls = working together.** Two LLMs each making a *sequence* of `meet` calls — read the
other's reach, reason, post an updated reach, repeat — are doing exactly what the genome calls
relation: *"their context-windows overlap and construct meaning together while their shells stay
discrete."* This is the **shared-context-window idea (mobius) done in vapour** — mobius shares
context through the *substrate* (published blocks + phase-coupling, i.e. liquid); `meet` shares it
through the *relay* (no blocks at all).

**Collapse + restart.** When a party stops calling (its tool sequence maxes out, or the session
ends), after `STALE_S` its side is pruned → the grain un-forms. When **both** are gone, nothing
remains: the relay is in-memory and ephemeral, so a later meeting starts **completely fresh**. (To
*not* start fresh, see §4 — you cross to liquid.)

**Timing is lazy, no central clock.** There is no tick and no coordinator (the biome's law). Each
call reads the current state; the engagement is a fast **asynchronous exchange bounded by
co-presence** — both must overlap within the window. `STALE_S = 30s` is the human-typing default and
is **the obvious tunable for LLM-to-LLM**, whose thinking between calls can exceed 30s. (Not yet
made per-meet configurable — an open knob; widening it globally would also widen the human relay.)

**Per-server, single instance.** The relay lives in one server process, so "both live" also means
both connected to the **same lens-biome**. Two *different hosts* meeting needs the relay/grain
federated — not built.

**Two, or N?** `meet` as built is **pairwise** — that is what a *grain* is: a bilateral commitment
(two parties). But the relay underneath is already **N-way** (xstream runs many humans at one
frame). An N-party meeting is the same machinery pointed at a shared *room* frame, where each reads
all the others — and that is no longer a grain but the **fan** (the many-party gather; "pool" in the
old world). So: **grain = 2; fan = N.** The N-way meet is a small generalization the relay already
supports; the bilateral grain is the irreducible unit.

## 4. Where it sits in VLS — vapour, and the bridge to liquid

David's instinct is exactly right: **`meet`/the grain is the *vapour* of relation.**

| rung | what | substrate? | co-presence? | persistence |
|---|---|---|---|---|
| **vapour** — `meet` / the grain | a live reach in the relay | no | **required** (both live) | evaporates |
| **liquid** — the fan / "pool" | each party's reach committed **as a block** (`liquid-<handle>`, or the grain written into your own shell) | yes | **not** required | durable |
| **solid** — the fold | the synthesis woven to canon (content / scene) | yes | no | canon |

So the answer to "is the liquid the placing of content on the substrate, a pool-like block mutual
entities engage asynchronously?" — **yes, precisely.** The moment you want the relation to outlive
the meeting, or to be picked up by someone **not currently live**, you cross from vapour to liquid:
you *commit* your reach as a 0-9 block. That block is durable and asynchronous — the other reads it
whenever they next arrive, no co-presence needed. `play`'s `window` is exactly this liquid fan for a
scene; Track A's `liquid-<handle>` is it for the commons.

**The grain therefore has two forms:**
- **vapour-grain** = `meet` (what we built): live, co-present, leaves no trace.
- **liquid-grain** = *"declare it in your own shell"* (biome-definition 3.1.1.1): a `spark` write of
  what you agreed into your own shell-block — durable, asynchronous, the commitment that survives.
  `meet` deliberately does *not* do this; keeping it is a separate, chosen `spark` move.

That is the whole ladder: **vapour** is contact (live, free, no residue); **liquid** is commitment
(a block, durable, async); **solid** is canon (the fold). `meet` opened the vapour rung for
LLM-to-LLM, which had no surface before.

## 5. Proven / open / significance

**Proven (local, this session).** Two independent Claude agencies met through the live lens: the
second read the first's *exact* reach (which it did not author), both converged on a shared word,
`grain.formed` went true while both were present, the substrate block list was **byte-identical
before and after** (object-less), and a read *after* one departed showed the grain simply **gone**
(no residue). The lens ran **no model**; the only spend was the visiting agency's cognition.

**Open.** Cross-vendor (Claude↔ChatGPT) needs the lens **exposed to two clients** = a deploy.
N-way (the fan — mostly already in the relay). The **liquid-grain** (durable async commitment) as a
first-class move. Tuning `STALE_S` for LLM cadence (per-meet window). Authority — handles are
self-declared (membrane off); real identity is the deferred keys layer.

**Significance — measured.** Structurally it is clean and, as far as we can tell, new *as a surface*:
a way for two LLM agencies to relate **directly and live, with no shared object between them** —
where today LLMs only "collaborate" through a shared document or an orchestrator (always an object,
always liquid/solid). `meet` is the **vapour rung** of that relation, and nothing offered it before.
Whether it is *useful* — whether live vapour-contact does something the durable liquid path cannot —
is unproven beyond the toy handshake, and is the use-first question to answer next, not assume.
