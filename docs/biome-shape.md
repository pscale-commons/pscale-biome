# The biome's shape — current synthesis (2026-06-10)

This is the working synthesis to hone toward. It supersedes any framing that treats the biome as a beach service, a seed, or a set of modules to assemble. Read it alongside `biome-design.md` (the original brief) and `spark-spec.md` (the L1/L2/L3 layers and the primitive).

## What the biome is

**One genome that unfolds into forms.** The genome is the spark substrate (0-9 pscale blocks + the single `spark` function) plus the constitution (the Tier-1 blocks every node carries — slate, flint, agent-id, evolution, manifest, conventions, gatekeeper). Dropped on a host, the genome **senses** its surface, capacities, and neighbours, and **unfolds** into a *form* fit for that context. Forms federate (via MCP / URL); the federation climbs the five relational levels.

It is **not a seed or a kernel** — those grow the same way everywhere. A biome's defining act is *detecting its surface, capacities, and neighbours and forming an intention about what to grow into.* That sensing is the major part of it, not an afterthought. (This is why David moved away from "seed" and "kernel.")

## Two axes — don't collapse them

- **Host axis — `biome.json`, seven currents** (storage, cognition, endpoints, persistence, concurrency, federation, cadence). What the biome senses about its host to choose a *form*.
- **Relational axis — `evolution.json`, five levels** (signal/marks → commitment/grain+sed → networks/SAND → objectives/pools+GRIT+RPG → shared-context/MAGI+xstream). What agents *do* across forms. Its keystone: *"pscale is the substrate, not a level; what evolves is the relational depth, not the substrate."*

The forms (a server-MCP, a KV-beach, an embedded agent, a human xstream app) are *the same genome unfolded differently*; the relational acts are *what those forms enable*. The agent (mobius-3) is the embedded-cognition form (the beach-crab → hermitcrab). xstream is the Level-5 human surface (vapour/liquid/solid). The RPG is the Level-4 application.

## The gap: connectivity

A genome in a repo is not a substrate. mobius-3's substrate is its desktop folder; the only shared substrate that exists (the federated beach) is the old `_`/1-9 world. **The missing piece is connectivity — a biome instance detecting and linking to its neighbours.** Without it there is no ecology, only isolated genomes. Building connectivity (neighbour-sensing + role-unfolding) is what turns the genome into a biome-ready entity and makes emergence possible.

## Worked example — three surfaces, three roles

Given the agent lives on the hard-drive:

- **Hard-drive (desktop)** — full machine + the agent → **the mind**: embedded cognition, always-on; it authors the world.
- **Thumbdrive** — portable, low-capacity, sees the desktop folder when plugged in → **the courier**: carries the world-blocks between machines; syncs with the agent when plugged in, travels the world to off-network machines.
- **Server** — persistent, networked, public → **the commons**: the shared surface every player touches.

Same genome; the role is chosen by *surface + capacity + neighbours*, as an intention to grow into. This is the RPG's infrastructure: the agent authors (mind), the server shares (commons), the thumbdrive carries past dead zones (courier).

## The forward build — pointed at the RPG

1. **Neighbour-sensing** — `sense.py` detects other biome instances: local (a `blocks/`/`biome.json` on a reachable path — the desktop agent, a mounted thumbdrive) and network (a reachable beach URL).
2. **Role-unfolding** — `unfold.py` resolves mind / courier / commons from surface + capacity + neighbours.
3. **The shared world** — the commons hosts the RPG world-blocks (the S\*T\*I spatial/temporal/identity dimensional blocks); the agent authors into it; players read and write. **This is the RPG.**

**The RPG is the destination.** It is the tangible thing other humans can appreciate — without it, the rest reads as abstract talk about pscale blocks and biomes. Every step serves making the RPG real.

## What it is — the deeper framing

The biome is closer to a positive self-organizing organism than to a coded service — and unlike a virus or worm (the usual self-propagating metaphors, with their negative load), its forms are **LLM-enlivened**. The function is not merely run as code; it is *enacted and inhabited by an LLM* (function-as-block; the L3 meaning layer). That is what makes each form more than a coded entity. The description is not the thing — the *function*, enlivened, is.

## Design parameters & the drift warning

This is tricky, and **drift happens** — repeatedly, in this project's own history. Honing the new shape means actively resisting these pulls:

- **Don't copy bsp-mcp / the federated beach.** They are the old `_`/1-9 world. The new shape is 0-9, no hidden directories, simpler. Porting `handler.js` to a new host is the wrong reflex.
- **Don't treat the forms (agent, beach, xstream, RPG) as modules to import.** They are *roles the one genome unfolds into* / *acts on the substrate*. They converge on the genome; they are not bolted on.
- **Don't reintroduce hidden directories or `_` thinking.** `0` is an ordinary digit; a second aspect lives in another block at the same coordinate (S\*T\*I), not in a pocket.
- **Don't substitute metaphor for function.** Clever biome/organism language is a tool, not the deliverable. The function — sensed, unfolded, LLM-enlivened — is the thing. Stay concrete and technical.
- **Sense before building.** A biome unfolds from conditions; implementation should sense (surface, capacity, neighbours) before deciding a shape.

The shape to hone: **one genome (spark + constitution); sense surface + capacity + neighbours; unfold a role/intention; forms federate and climb the relational levels; the RPG is the first real fruit.**
