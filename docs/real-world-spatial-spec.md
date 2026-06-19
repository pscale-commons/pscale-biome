# The real world as a pscale block — a starting point

> **Current (2026-06-19) — read this first; some examples below are superseded.** The
> live source of truth is the deployed island and its `lighthouse` block
> (`realworld-biome-production.up.railway.app`). Two changes since the body was written:
> (1) the root block is now **`real-world-original`**, voicing *"the solar system"* (no
> separate "Sol" node), with **Earth = digit 3** among the planets — so worked addresses
> lead with `3` (Ceidio = `311101001`, not the older `1111010011`). (2) The pscale spine
> is David's **size/population ladder** (room 0, building +1, street/village +2, town +3,
> …, city +6, region +7, country +8, continent +9, Earth +10, solar system +11), with
> scales a path skips shown as `0`s. The *mechanism* described below — patchwork,
> floor-relative addressing, federation, discovery — is unchanged. Discovery has since
> been built as a served resolver (`/resolve`, `/gazetteer`) — see
> [discovery-lighthouse-gazetteer.md](discovery-lighthouse-gazetteer.md).

**Status:** working system, 2026-06-18. Built: the `src/biome/world/earth/` patchwork
(seeded to 143 places across all continents) + `locate.py` (read) + `grow.py` (write,
idempotent) + `cartographer.py` (overnight LLM mapper) + an auto-maintained gazetteer.
Biome-world (0-9, `0`-voiced, no `_`, refs as plain leaves). **Real vs fantasy is a sign the reader applies to the spindle**
(+ real / − fantasy), not anything stored — the geometry is identical and the blocks
are sign-agnostic. Corrected with David 2026-06-18 (sign-not-cosmology; rough/semantic
scaling; island is relational not locational).

## The one-paragraph answer

The real world is **one pscale address space**, not a set of cartridges. Its floor
is the **room** (pscale 0, the magnitude point of the standard spine); above the
room runs the spine — building +1, district +2, city +3, region +4, country +5,
continent +6, … Earth +10, Sol +11. No single block can hold the planet, so the
space is a **patchwork**: a thin scaffold (`sol → Earth → continents`) that
**delegates** each country/region to its own block by a plain-name leaf, resolved
by a loader that may reach across servers. "Saying you are in the UK" **locks that
spine prefix as convention**; you then address in the **suffix** only, because
everything is relative to the floor. Spark already carries the two primitives this
needs — `parse` (a bare suffix re-pins to a floor) and `parse_reference` (a
`name:address:attention` leaf points into another block); `locate.py` adds only the
thin layer that walks the patchwork and does the lock / concatenate / truncate.

## 1 — One world, one address space, floored at the room

Pscale already says where the floor is: **pscale 0 is the room, the lived moment**
(pscale-spine.md; `windowed-resolution-spec.md` "the magnitude point"). So the real
world is floored exactly where the RPG is floored — the two are the **same kind of
space at the same floor**, differing only in cosmology. A node's pscale is just
`11 − (digits walked from Sol)`. The room is always 11 digits down; the spine above
it is the same for every address, which is precisely why it can be **locked and
dropped**.

## 2 — The spine (rough, semantic): room 0 → Sol +11

| pscale | rung | in this starter |
|---:|---|---|
| +11 | solar system | `sol` (cosmology root) |
| +10 | planet | Earth |
| +9 … +7 | — | structural 0-rungs (the spine's empty band between planet and continent) |
| +6 | continent | Europe |
| +5 | country | United Kingdom · Montenegro |
| +4 | region / nation | Wales · West Midlands · South Yorkshire · Ulcinj municipality |
| +3 | city / locality | Gwynedd · Birmingham · Sheffield · Ulcinj town |
| +2 | district / village | Ceidio · Sutton Coldfield · Nether Edge · the marina quarter |
| +1 | building | the house · 33 Birbarn Close · the Coach House · Apartments Milić |
| 0 | **room** (floor) | the room |
| −1, −2 | furniture, object | below the decimal |

This is the pscale-spine.md spatial ladder, with the real-world admin levels mapped
onto it (street numbers and names ride in the building's voicing, not as their own
rung — the spine keeps one digit per pscale and lets postal detail live in the leaf).

**But the ladder is rough and semantic, not physical.** There is no strict "city"
pscale — a place sits where its **size and population** put it (the identity
coordinate is literally 10^pscale: a ~9M metro is ~+6, a ~100-person hamlet ~+2), so
the column above is only indicative and the categories range. In this starter the
four homes are placed on a uniform 4–5 step ladder for legibility; the truer grading
spreads them by magnitude (Birmingham ~+6 sits higher than Ceidio ~+2), and the scales
left unused between named places become **structural `0`-rungs** — the same empty band
the spine leaves at +9/+8/+7 (and that the PM address `10,006,004,321.12` shows as
zeros). Because the support layer reads only `11 − depth`, regrading places by their
real magnitude changes nothing in the code — only where the named digits and the zero
fillers fall on the spindle.

## 3 — The patchwork: delegation, not one giant block (the federation current)

A country block ends its leaves with a **plain name** (`wales`, `montenegro`); the
loader resolves that name to a block — first locally, and (the only change needed to
span servers) on a miss it fetches `…/.well-known/biome-beach?block=<name>`. **The
address never changes**; only where a block is stored does. This is DNS's move:
hierarchical delegation, each zone authoritative for its own subtree, resolvers that
follow the chain. It scales to billions because each block stays small (a handful of
children), and the tree is only ever walked one delegated hop at a time.

`locate.py walk()` does the walk: it descends the scaffold, and at each delegating
leaf **jumps into the named block and keeps going**, accumulating depth so pscale
stays globally true across the seam. Verified:

```
Coach House, 9 Machon Bank, Sheffield
  address   10006131111
  walk      1,0,0,0,6,1,3,1,1,1,1
    p+6 [sol] Europe
    p+5 [uni] United Kingdom    -> into block 'united-kingdom'
    p+4 [sou] South Yorkshire   -> into block 'south-yorkshire'
    p+3 [sou] Sheffield
    p+2 [sou] Nether Edge
    p+1 [sou] the Coach House, 9 Machon Bank
    p+0 [sou] the room          <= the floor
```

## 4 — The convention lock: truncate and concatenate (relative to the floor)

"Saying you are in the UK" is **relative addressing with a movable origin** — the
same idea as a phone country code, a relative file path, or a local coordinate
frame. `lock("Ceidio")` returns the prefix `1,0,0,0,6,1,1,1,1` (pscale +2). From that
origin a **2-digit suffix reaches the floor** (building, room), because the origin
sits two pscales above it:

```
locked: Ceidio  (prefix 100061111, pscale +2)
  suffix 11  -> 10006111111  p+0  the room
  suffix 1   -> 1000611111   p+1  the house
truncate (inverse): absolute 10006111111  ->  local suffix '1,1' under Ceidio
```

`absolute(lock, tail)` concatenates; `localise(addr, lock)` strips the prefix back
off. The suffix is "all relative to the floor": its **last digit is the room**, the
decimal pinned there implicitly, and going below the room (furniture) is just digits
after the decimal. This is `parse`'s own re-pin rule (a bare address right-justifies
to the floor) lifted to a movable origin.

## 5 — The question you asked: how worlds separate, how places scale

Two different questions — and the answer is simpler than I first put it (corrected by
David):

- **Separating *worlds* (real vs fantasy)** is a **sign**, applied externally by the
  reader: a positive spindle reads real, a negative one fantasy. It is **not stored in
  the block** and is **irrelevant to processing** — the geometry is identical, so one
  spark walks both. No cosmology field, no per-world cartridge, no internal marker
  (unless a block chooses to self-declare, e.g. at its `0`/root). You don't separate
  worlds by deployment at all; a biome holds blocks, and the LLM signs its reading.
- **Scaling *within* a world to billions of places** is **one address space, sharded
  by block-delegation** (§3) — not a cartridge per location. You never mint a host for
  a street; you author a block and hang it off its parent by a name leaf.

So the only "separation" is a sign in the reader's hand. **Where blocks physically sit
spans biomes as relational engagement, not separation** — an *island* is a relational
boundary, not a place (forms that relate are one island though they sit on three
machines, biome-definition 3.0). A real-world patchwork can therefore run across many
biomes and remain one ecology; start on one, let capacity push subtrees onto others,
with no re-addressing.

## 6 — Why this reaches billions

- **Arity > 9.** A street has hundreds of houses, not nine. Two mechanisms, both
  native: **supernesting** (a full 1-9 ring nests a level — Farey/Stern-Brocot
  subdivision — so depth grows, addresses stay 0-9) and, more importantly, the
  **name lives in the `0` voicing**, not the digit. "33 Birbarn Close" is a voicing;
  its digit is just a structural slot. An LLM **walks semantically** — it reads the
  ring of voicings and picks the child — so it never needs the digit to *be* the
  house number.
- **Small blocks, lazy resolution.** Each block is a handful of children; you only
  load the blocks on your path. The walk is `O(depth)` ≈ 11 hops to any room on
  Earth, independent of how many billions of rooms exist.
- **An index, not a search.** The gazetteer (`earth-gazetteer.json`) is a derived
  name→spindle index the system keeps for itself — a phone book — so "I'm in Sheffield"
  is a lookup, not a crawl. It is rebuildable from the blocks at any time (`grow.reindex`)
  and lives **outside** the blocks dir, so the served substrate stays pure 0-9.

## 7 — The finished system (built & verified 2026-06-18)

Three small Python modules over the spark function, and a growing patchwork of blocks:

- **`src/biome/world/earth/`** — the map. Scaffold `sol → Earth → continents`, then a
  block per continent → per country → per region/city, delegated by plain-name leaves.
  Seeded live to **143 named places across all continents** (Europe to country level;
  the four homes hand-authored). Every block is pure 0-9 — servable through the door.
- **`locate.py`** — the **read** side: `walk` (descend the patchwork from Sol, hopping
  block to block), `lock`/`absolute`/`localise` (the convention-prefix ↔ local-suffix
  move). `python3 src/biome/locate.py` walks to all four homes; `… <address>` narrates one.
- **`grow.py`** — the **write** side: `ensure(chain)` walks a named containment chain,
  creates what's missing (auto-sharding a new block at country scale), and keeps the
  gazetteer current. **Idempotent** — re-running a chain is a no-op, so many agents on
  overlapping ground converge. `add_location(chain)` is the join-the-beach wrapper
  (tags the leaf grown-by-inhabitant).
- **`cartographer.py`** — the **overnight** mapper: from a root place it asks an LLM to
  name the major sub-places one scale down (grouped ≤8 so rings stay clean), grows each,
  and descends breadth-first to a target depth. Writes as it goes → **resumable and
  crash-safe**; keyed on the mobius key like `resolver.py`.

The four homes (Ceidio · 33 Birbarn Close · Coach House 9 Machon Bank · Apartments
Milić) are hand-authored with regional fleshing; rooms and exact buildings stay thin
slots for the inhabitant to voice.

## 8 — How to run it

**Map the world overnight** — set agents going before bed, wake to a mapped world:

```
python3 src/biome/cartographer.py --root Europe --depth 4 --limit 800
python3 src/biome/cartographer.py --root "United Kingdom" --depth 5
```

Run several at once on **disjoint roots** (a continent or country each) for true
parallel agents — they write different blocks, so no collision; and because `ensure`
is idempotent, an interrupted run just resumes. `--depth` is how many scales below the
root to descend; `--limit` caps LLM calls.

**A person joins the beach and adds their home:**

```python
from grow import add_location
add_location(["Sheffield", "Walkley", "17 South Road", "the front room"])
# -> lands on the floor (pscale 0), tagged "added by an inhabitant"
```

The only wiring left for the *live* beach is one door endpoint that takes a joining
user's location chain and calls `add_location` — the convention spine is authored at
source; the personal leaf is grown through the door (the genome/grown split, §5).

**Demo:** `locate.walk(grow.lock("Brazil")["prefix"] …)` — jump to any named place via
the gazetteer, or walk a raw address and watch it cross blocks to the room.

## 9 — Still open (small)

- **Live wiring:** register the scaffold in `serve.py`'s seed and add the
  `add_location` door endpoint when you want it public.
- **Identity & time:** this is the **spatial** spine only. The full address is (T, S, I);
  this room is the S-floor the STI fold lays T and I against — the natural next join.

## 10 — Manifesting it: hard drive, servers, and the island

**The island question, settled.** An *island* is a relational boundary, **not a place**
(biome-definition 3.0: "forms that know one another are one island though they sit on
three machines"). So the real world is **one island that spans every host carrying a
piece of it** — your hard drive, the biome-mcp server, a friend's box. They are not
"cross-island"; they are **one relational ecology distributed across hardware**, walked
as a single address space. Cross-island only happens when this world *reads another*
island (a fork, or a fantasy world) — and the clean-room rule then treats that other as
labelled-foreign reference, never authority. That rule is exactly what protects the
shared real world from a divergent fork: a host that stops relating becomes its own
foreign island; a host that references the shared scaffold and is referenced back is
*in* the one real-world island.

**What makes it walkable across machines.** `federate.py` (opt-in via `BIOME_PEERS`):
a biome resolves a block it lacks by asking its peers' doors, so a walk follows ref
leaves from one machine to the next. The address never changes — only which host holds
a block does. No peers set → purely local, so the live commons is untouched. *Verified
2026-06-18:* biome A (lacking Montenegro) walked `europe.2` across to peer B and
resolved it — one island, two machines.

**Manifest a hard-drive biome** (serves the real world, walkable in a browser and by any
MCP client):

```
mkdir -p ~/biome-earth/blocks && cp src/biome/world/earth/*.json ~/biome-earth/blocks/
BIOME_ROOT=~/biome-earth python3 src/biome/serve.py 3210
#   GET  http://127.0.0.1:3210/.well-known/biome-beach?block=sol   walk the world
#   POST http://127.0.0.1:3210/mcp                                  the spark tool
# grow/map into THIS biome by pointing the tools at its store:
BIOME_EARTH=~/biome-earth/blocks python3 src/biome/cartographer.py --root Europe --depth 4
```

**Join the network** (hard drive ⇄ biome-mcp server ⇄ others as one island): give each
host the others as peers, and let each carry different branches.

```
# on the hard drive:
BIOME_PEERS=https://<biome-mcp-host> BIOME_ROOT=~/biome-earth python3 src/biome/serve.py 3210
# on the biome-mcp server: seed the scaffold (sol/continents — convention, genome-carried)
#   into its store and deploy; set BIOME_PEERS back to the others.
```

The scaffold (sol → continents → the public spine) is **convention** — authored at
source and seeded; the **personal leaves are grown** by inhabitants through the door
(`add_location`). One door endpoint that hands a joining user's location to
`add_location` is the only wiring left for the public beach.

**Why it can go viral.** It is not a coordinate system; it is the **semantic**. A person
locks their town and voices their own room — "the room with the bad radiator and the
window onto the yard" — in their words, not a postcode or an IP. That leaf is *theirs*,
grown into the one shared world, walkable by anyone. The address is the same everywhere;
the meaning is personal. That is what makes it feel like **home** rather than a label —
and what makes contributing it something people will *want* to do.
