# spark / flint / slate — a pscale primitive from first principles

**Status:** first-principles draft (session of 2026-06-07). Supersedes the `_`/1-9 lineage (bsp · sunstone · whetstone) and the 0-9 rebase (zand · sunztone · whetztone). Same family — JSON, digit keys `0`-`9` — rebuilt on a cleaner foundation in which **hidden directories never exist.** Set name TBD; provisionally "the spark set."

## The three artifacts

A pscale primitive is always three things wearing one face:

| artifact | role | read… | lineage |
|---|---|---|---|
| **slate** | the teaching block — external self-description | by an LLM *without* a function; from it the LLM encodes its own function | sunstone · sunztone |
| **spark** | the function — the canonical, well-designed convention | it reads/writes blocks | bsp · zand |
| **flint** | the operational manual | *through* the function; if the spark is right, walking flint coheres internally | whetstone · whetztone |

The fire: you read the **slate**, strike a **spark** from it, and the spark reads the **flint**. `slate = spark + flint` — the external form names both the function and the internal form it operates on. A fresh LLM handed only the slate can re-derive a conforming spark and confirm it against the flint.

## First principles of the geometry

**1 — A block is digit-keyed JSON.** Keys are single digits `0`–`9`. No special characters, no `_`, no metadata wrapper. The dict is the block.

**2 — `0` is the node's own semantic; `1`–`9` are its elaboration.** At any node, the `0` says what *this node is* — its fact-for-its-parent. The `1`–`9` are what lies within it: alternatives, contents, sub-places, next steps.

**3 — The zero-spine generates the floor, and that is its only job.** Descend `0` from the root until the first string; the number of steps is the **floor**; the floor is pscale 0. Intermediate `0`-objects may be semantically empty — **supernesting is allowed to be purely structural**: the outer levels can carry zero semantic, with all meaning held at pscale 0 (a beach of marks is exactly this — you append, the floor rises, the scaffolding above means nothing). The floor is the one coordinate invariant under growth, which is why blocks are laid against each other (the floor-fold) **by pscale, never by walk-depth.**

**4 — There are no hidden positions.** A `0`-branch's non-zero children — `0,1`, `0,2`, `0,0,0,1`, wherever the semantic finally lands — are ordinary positions at their pscale. They appear in a disc at that pscale and are reached by an ordinary walk. Nothing is "entered." Where an older system hooked a second aspect into a pocket under the zero-spine and reached it with a star, **this set has no pocket to enter**: a second aspect of a coordinate lives in *another block at the same coordinate*. One address, many blocks — the dimension is which block you read, not a hidden branch of the address.

**5 — pscale = floor − depth.** The decimal in an address anchors the floor (one decimal, always). Addresses are written with one dot (`30.5`); walks with commas (`3,0,5`).

**6 — Semantic-numbers are total.** With no hidden directory, address→position is a clean bijection: every digit-string walks to exactly one position; every position has exactly one canonical address.

## The möbius of `0`, and its voicing forms

The twist survives: a `0` that has siblings is the semantic *of its parent* — read upward it is a fact-about-the-parent (a summary); read downward it heads its own siblings. **What** a `0` summarizes is not fixed — it is a *voicing form* chosen per block by intent, on two axes.

**Relational — which direction in the tree the `0` concentrates:**

| form | tree-kin | the `0` summarizes | direction |
|---|---|---|---|
| **current** | siblings | its own `1`–`9` — the canonical voicing | here |
| **previous** | older cousins | the prior parent's children — what came before | back |
| **next** | younger cousins | the next parent's children — what is projected | forward |
| **parental** | uncles & aunts | the parent's sibling-ring — the context one level up | up |

There is no "down" form: down is the elaboration itself, not a reference.

**State — the condition of what is summarized:** `complete-locked` (settled, immutable) · `complete-editable` (settled, revisable) · `incomplete` (fresh, in-formation).

These are combinations — 4 × 3, most latent. What matters is which the **use-cases** call for:

| use-case | relational | state | why |
|---|---|---|---|
| **spatial coordinate** | current | either | the places around me, some still to fill in |
| **temporal coordinate** | current | either | the unfolding sequence |
| **history** | previous | complete | each supernest distils the finished prior group — history compresses as it deepens |
| **identity** | parental | either | the social rings I sit inside, refracted through me |
| **marks** | *null* | — | no summary at all; supernest is pure structure; all semantic at pscale 0, by append |

Lineage: this refactors the four sign-forms — deductive / inductive / abductive / backcasting — from *reasoning modes* into *tree directions*, which generalises past the time axis they were tuned for. `previous` ≈ inductive history; `current` ≈ deductive rendition; `next` ≈ abductive/backcast.

## Worked through coordinates and shell

**A spatial coordinate (current · siblings).** A place-block, floor at room-scale. Address `42.1` walks `4,2,1` — settlement `4` ⇒ building `2` ⇒ room `1`. Each node's `0` names the place ("the Drum"); the `1`–`9` are its sub-places (a headless one is a visible TODO). Voicing is *current*: the children are siblings. The same character's private notes on the same place are a **different block read at `42.1`** — same coordinate, no pocket.

**The shell's history (previous · older cousins, + null supernest).** pscale 0 is the latest pulse's record. When history supernests, the new outer `0` carries an inductive summary of the finished group — *previous*, complete-locked: "what the last run of pulses amounted to." Contrast a **marks** block, which supernests with *null* voicing: the outer `0`s are empty scaffold, every mark sits at pscale 0, and the floor rises purely structurally as you append.

## Deliberately absent

- Hidden directories; star-into-a-pocket. (Never introduced — nothing to remove.)
- The "structural hiding" framing. A **ring** is the `1`–`9` present at a level; the `0` is not one of the alternatives but the **voicing of their shared parent**, surfaced as the ring's head. (This is the one intentional change from zand, which listed `0` among the siblings.) Depth is reached by walking, never by entering a private space. A **disc** still emits every position at its pscale, `0`-positions included — they are first-class, not hidden.
- Star as a geometric operator. Cross-block reference (`name:address:attention` resolved via a loader) remains — but it is plainly "read another block," not a hidden-directory door.

## The three layers

- **Layer 1 — code.** The spark function, in whatever language a host runs (Python here; TypeScript for browser / KV hosts). The carried, self-sufficient core; one per runtime, all answerable to the same tezt battery.
- **Layer 2 — pscale blocks.** The data — slate, flint, shells, beach blocks — sitting on whatever surface a host provides (filesystem, KV, hosted DB, upstream beach), serviced by a Layer-1 spark.
- **Layer 3 — meaning.** What emerges in a mind reading the blocks: the imaginative, vector-cloud murmuration. Intangible; the reason the other two layers exist.

## Status

Layer 1 is built and locked: `slate.json` (teaching), `flint.json` (manual through the function), `spark.py` (the coded runtime), `tezt/tezt_spark.py` (42/42), with `fold` and `refer/star` included. The Python spark is one *ideal form*; a TypeScript spark is the same protocol for TS hosts, validated against the same battery, authored when a target unfolding needs it.

## The biome, not a stack

The biome is one package that senses where it landed and unfolds — *not* a beach plus an MCP plus an xstream built as separate deployments (`biome-design.md` forbids exactly that). The organising spine is the unfolding procedure (`biome.json` branch 8) and its reflexive seed (branch 9): the biome reads its own 0-9 genome **with the spark it carries** and composes its form from sensed host conditions. The seven currents (storage · cognition · endpoints · persistence · concurrency · federation · cadence) are a repertoire; surfaces grow only as conditions warrant, and every surface calls the one spark.

The three live instances are three unfoldings of one shell: bsp-mcp on Railway (hosted storage · external cognition · MCP endpoint), the happyseaurchin KV beach (hosted storage · `.well-known` federation · silent substrate), mobius-3 on the desktop (filesystem · embedded loop · always-on). Same genome; the receptacle determines the form.

## Next — the unfolding spine

The smallest first move that forces the whole architecture (per `minimal-package.md` Q4a): **sense-and-print** — a host sensor (`src/biome/sense.py`) that inspects the landing, and an unfolder that walks the 0-9 biome shell through spark and reports what the biome *would* become here, committing no surface. Adapters and surface-drivers follow as the unfolder reaches for them, each gated by a sensed condition, each calling the one spark.
