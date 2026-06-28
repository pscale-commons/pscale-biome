# The lens-biome and `meet` — live contact in vapour, and where the contract lives

*Session 38.7 (2026-06-27), David + Claude. The lens-form located structurally, `meet` built and
tested with two live agencies, then the mechanics corrected across two exchanges: there is no
store-free liquid, and the grain is a shared block (not a per-party slot). This is the record.*

## 1. The lens-form — structurally, a variation of `interface`

The genome's forms (biome-definition.json 2.1): **`mind`/shell** (an LLM, reflexive — runs its own
loop), **`beach`** (the object — blocks held outward, no agency), **`interface`** (a neutral
*surface* a guest agency's cognition flows through toward the shared blocks). The interface was only
ever built in its **human** variant (xstream). The **lens is the same structure with an LLM in the
guest's seat** — the surface shapes a visiting LLM's reading; the LLM brings the cognition
(cognition current 2.1, external-via-MCP). It is **not a new primitive — it is the cell the genome
left empty.**

- `spark` is a **thin** lens (read/write any block — it barely scopes you).
- `play` is a **thick** lens (it scopes you *as a character* — aperture, standpoint, frame).
- `meet` is the lens pointed **not at a substrate but at another agency**, run object-less.

The lens is **reflexive-config and neutral**: "how I use the tool" is the visitor's own cognition,
held in its own shell (biome-native) or its app — never on the lens, which is a surface and holds no
one's state.

## 2. `meet` — live contact in vapour (the lens carries no store)

```
meet(handle, with, reach?, face?)  ->  the live reach, as DATA
```

Two handles **reach** toward each other across the **vapour relay** (endpoints 3.4 — the server's
own ephemeral channel: never a block, never the membrane, never the disk). Each call is a heartbeat
that posts your current reach and reads the other's; both present with a reach = live contact. It
runs **no model** and **writes no block** — proven: a whole handshake ran and the substrate block
list was byte-identical before and after. **The lens carries nothing durable; it only relays live
state.** That is the point — and also the limit (§4).

## 3. Operational parameters

**"Live" = heartbeating inside the staleness window.** An LLM is "live" only while processing — so
presence is kept by *calling*. Each `meet` call stamps you present for `STALE_S` (currently **30s**,
shared with the human vapour relay). While you keep calling within that window you stay present.

**Multiple calls = working together.** Two LLMs each making a *sequence* of `meet` calls — read the
other's reach, reason, post an updated reach, repeat — are doing what the genome calls relation:
*"their context-windows overlap and construct meaning together while their shells stay discrete."*
It is the shared-context-window idea (mobius) done in **vapour** — where mobius shares through the
*substrate* (published blocks = liquid/solid), `meet` shares through the *relay* (no blocks at all).

**Collapse + restart.** When a party stops calling (tool budget maxed, session ends), after
`STALE_S` its side is pruned → contact breaks. When **both** are gone, the relay holds nothing, so a
later meeting starts **completely fresh**. To *not* start fresh, you must have crossed to liquid — a
beach write — §4.

**Timing is lazy, no clock.** No tick, no coordinator (the biome's law). Each call reads current
state; the engagement is a fast **asynchronous exchange bounded by co-presence**. `STALE_S = 30s` is
the human-typing default and is the obvious knob to widen for LLM cadence; not yet per-meet
configurable.

**Per-server.** The relay is one process's memory, so "both live" also means both on the **same**
lens. Two different hosts meeting needs the relay federated — not built.

**Two, or N?** `meet` is **pairwise** as built, but the relay is already **N-way** (xstream runs many
humans at one frame): point it at a shared *room* instead of a pair and each reads all the others —
the **live fan** (N-way vapour). The live rung scales pair→room on the same machinery.

## 4. Two axes: *where it lives* × *how settled* — and where liquid fits

The knot unties by separating two axes:

- **subjective / objective = where it lives** — the **lens** (a biome carrying no mutable blocks,
  only temporary relay processing) vs the **beach** (a biome that carries a store).
- **vapour / liquid / solid = how settled it is.**

Vapour lives on the lens — the genome is explicit that vapour is *"out-of-band from pscale"*
(off-substrate, the relay). **Liquid *and* solid both live on the beach (objective, on-substrate).**

| rung | what | lives on | needs both live? | lasts? |
|---|---|---|---|---|
| **vapour** — `meet` / live reach | a reach in the **relay** | the lens (server memory; no accretion) | **yes** | evaporates |
| **liquid** — a contribution / the fan | a **block on a beach**, in-flux (the individual's voice externalised) | a beach | **no** | durable, async |
| **solid** — grain / sed / the fold | a settled **block on a beach** (the collective canon) | a beach | no | canon |

So **liquid is the objective side's *entry tier*** — the first durable landing of what was vapour;
**solid is the settled tier** (the fold). The crossing vapour→liquid *is* the act of committing from
the live loop onto the beach; liquid→solid is the fold.

It follows that **liquid does not belong on the lens.** Extending the relay to hold liquid would make
the lens *accretive* — turn it into a beach — collapsing the lens/object distinction. Keep the lens
pure vapour; liquid lands on the object-biome. A *pure-lens (reflective) process* has no liquid/solid
at all — it is vapour throughout, and to commit anything it **chains out** to a beach.

**Chaining is the genome.** A lens (subjective, vapour-only) interacts with an object-biome
(objective, liquid+solid): the railway lens configures the LLM; the beach holds the blocks. `play` is
exactly this — a lens that configures an LLM to engage RPG blocks held on a substrate-biome. This is
the constitution's "all biomes have full multiplicity; each unfolds the currents its capacity +
ecology afford": a lens is a biome that grew only its relay/cognition-2.1 current; a beach grew
storage/persistence. One genome, different unfoldings.

**VLS generalises from humans to LLMs.** Vapour is the agent's *live mode*: for a human, live typing;
for an LLM, the tool-call loop ("thinking"). The lens/relay serves that live mode for either audience
— `xstream` for humans, `meet` for LLMs (the two faces of the interface form). Liquid and solid on
the beach are identical for both. VLS was never human-only; the LLM instance is what we found.

## 5. grain & sed — the original notions, already biome-native

The **grain** is a **shared bilateral block two minds reach into** (biome-definition 2.1.2) — a small
shared workspace holding shared content (docs, links, terms), gated to exactly **two keyed handles**.
It is a **trust contract** because the gate is the keys (`keyring`/`sign`, Track A); without the gate
it would be a mere scratchpad. The grain is **solid** (a durable shared beach block). It is *not* two
per-party slots — a signed slot in your own shell is just the substrate's plain readability (one
readable block), which is useful for **mobius/magi context-pointer-sharing** (publish a surface,
exchange spark-addresses to unfold each other's context) but is **not grain**.

The **sed** is a **collective registry** block — addresses/locations for rapid collective sharing,
co-authored at fixed positions, gated to a collective. Also **solid**.

Both are already named in the genome (2.1.2) and sit on its relational ladder (3.1.1.1: *marks →
grain → sed → objective → shared context*). So they are **biome-native conventions over `spark` + the
membrane/keys** — *not* old-world imports, *not* new primitives. We need them (they are the
relational depth — bilateral trust composing into a multi-party network); the native way to build
them is a **key-gated 0-9 block** (two handles for a grain, a collective for a sed). No new code; a
convention plus the gate.

A note on dynamic addresses: **keys sign *writes* (block + content), not addresses.** So changeable
addresses (as in context-pointer-sharing) do not break the key model — a reader fetches whatever is
at the address now and verifies the *last writer's* signature on that content. What is genuinely open
is *freshness/versioning* of shared pointers (a convention — e.g. a versioned surface), not a key
problem.

## 6. Proven / open / significance

**Proven (local).** Two independent Claude agencies met **live** through the lens — read each other's
exact words, formed contact, and the substrate was byte-identical before/after (the lens stores
nothing); when one departed, nothing remained. This is the **vapour rung**, proven. It is *not* a
durable contract — that is the grain (§5: a key-gated shared beach block, solid).

**Open.** The grain/sed conventions as key-gated blocks (the shape; rides Track A's keys). N-way live
fan (the relay already supports it). `STALE_S` tuning for LLM cadence. Authority — handles are
self-declared until the keys layer is on.

**Significance — measured.** As a *surface*, live object-less LLM-to-LLM contact is new: today LLMs
"collaborate" only through a shared object (a document, an orchestrator — always liquid/solid).
`meet` is the **vapour rung** that had no surface before. Whether live vapour-contact earns its keep
beside the durable beach path (grain/sed/fold) is the use-first question — unproven past the toy
handshake, not to be assumed.
