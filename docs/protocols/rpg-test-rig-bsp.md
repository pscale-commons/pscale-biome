# RPG Test Rig — bsp-mcp / federated beach (cartridge sandpits)

> **OLD-WORLD (beach) document.** This describes a test rig on **bsp-mcp**, the
> **federated beach** (`_` semantic key, digits 1-9, star-door, `bsp()`) and
> **cartridge subdomains** as sandpits. It is **not** biome-world. The biome's RPG
> lives in 0-9 spark blocks — see [`../rpg-resolver-handoff.md`](../rpg-resolver-handoff.md)
> and the genome session. **Carry the rule-learnings across the worlds; never the
> blocks.** Written by the pscale-biome instance as a setup description for David's
> beach work — production bsp-mcp / beach is untouched.

## Why this rig

To develop the RPG **rules** fast: stand the play up in a **cartridge sandpit**,
let **character-LLMs replace every player**, run it automatically for many turns
across many runs, judge the **consistency of the narrative it generates**, and
only **commit a proven rule to the real beach**. The cartridge isolation is the
discipline — iterate on rules without polluting production.

The rig's design is substrate-agnostic; what follows is its instantiation in the
beach's idiom. The semantics of the five verbs live in
[`../rpg-resolver-handoff.md`](../rpg-resolver-handoff.md); encode them here as
beach blocks — the meaning is shared, the encoding is `_`/1-9.

## The three legs → cartridges

- **source** — the canonical rule-blocks + world-blocks + character-blocks, held
  off the live beach (a source cartridge, or version control). Edited; the truth.
- **snapshot** — a frozen cartridge state, a fork-point.
- **experiment** — a **cartridge subdomain**: an isolated beach holding one run's
  blocks, where the character-LLMs play. Diverges; never folds back to production.

A run = fork a fresh experiment cartridge from a snapshot, play it out headless,
evaluate, discard or harvest.

## The blocks in a sandpit (beach idiom, `bsp()`-served, `_`-and-1-9)

- **world** — three sibling blocks at shared coordinates: `<world>:space`,
  `<world>:time`, `<world>:identity`. Read the same spindle across all three to
  fold (the S\*T\*I crossing); they correspond by **pscale**, not walk-depth.
- **characters** — one passport-shaped block per character: purpose, history,
  conditions, a *bind* (where it stands + which identity child is its standpoint),
  and a *perceived* block — its own lived T, which is the filtered NOW feed (never
  the omniscient record).
- **rules** — the five verbs as **skill-blocks** (the synthesis-rule pattern of
  [`protocol-xstream-frame.md`](protocol-xstream-frame.md) §4): `rule:compose-frame`,
  `rule:soft-act`, `rule:medium-resolve`, `rule:soft-render`, `rule:settle`. The
  runner reads these via `bsp()` and applies them — the rules are **blocks under
  test, not code**. This is the whole point: edit a block, re-run, see the rule
  change behaviour without a code change.
- **world-truth** — the omniscient record the medium writes (shown to no player);
  the equivalent of the frame's solid / `_synthesis` lane.

## The runner (the daemon)

Reuse your existing RPG-via-bsp-mcp daemon (the synthesis / propagation daemons of
`protocol-xstream-frame.md` §7) and layer the SMH/STI refinements on top. Each
turn, per character, the runner:

1. **compose-frame** — `bsp()`-read the character's window per `rule:compose-frame`:
   `<world>:space|time|identity` at its bind-address (space descent + room
   contents; time descent + the character's **own** `perceived` recent; identity
   standpoint = the X−1 pick + the collective head), plus its shell.
2. **soft-act** — hand the window to the soft-LLM (CADO **Character** face, SMH
   **Soft** tier); it acts. A **human** plays this tier by typing; a
   **character-LLM** plays it for automatic runs.
3. **medium-resolve** — the medium-LLM, reading the full field via `bsp()` (every
   who at the place + objects in reach + the world-truth history), resolves what
   actually happens — omniscient, the more-grounded reading authoritative.
   `bsp()`-write to the world-truth lane. Shown to no player.
4. **soft-render** — per character, the soft-LLM renders **second-person**,
   perception-limited; `bsp()`-write each slice to that character's `perceived`.
   Discovery-by-action lives here — an act surfaces what it would let the
   character notice.
5. **settle** — `bsp()`-write consequences (a move, a wound, a death) into the
   world-blocks; the beach persists and federates them. A death endures for a
   later player because the **identity block now says so** — persistence is a
   write, not a server's bookkeeping.

Every character — including the nominal "player" — can be a character-LLM, so the
whole loop runs **headless** for rule-testing. Swap one back to a human (the Soft
tier, by typing) when you want a person in the seat.

## Sandpit → evaluate → commit

1. Edit a `rule:*` block in the experiment cartridge.
2. Run N automatic rounds (character-LLMs in every seat).
3. Judge the narrative it generated: does it stay **consistent**; do consequences
   **persist and propagate**; does perception stay **limited** (no leak of what a
   character couldn't know); does agency have **purchase** (do player acts shift
   outcomes)?
4. If the rule proves out, **commit** it to the canonical rules / the production
   beach. If not, edit the block and re-run — all in the cartridge; production
   untouched.

## Scaling note

The reason this is worth doing as blocks rather than code: the same rule-blocks,
federated, let small groups of players share one world across many connected
beaches without a central simulation. Consistency is **semantic** — every runner
reads the same rule-blocks and world-blocks and an LLM extends them coherently —
not a synchronised global state. Test that the rules *generate* consistent
narrative here, cheaply, with character-LLMs, before a single real player arrives.

## Boundary

The rig **design** and the rule **semantics** cross between worlds freely — test
them wherever iterates fastest. The block **artifacts** do not: beach blocks stay
`_`/1-9; biome blocks stay 0-9; neither is written into the other's substrate.
**Port learnings, re-author encodings.** "Cartridge" is a beach word; it never
enters biome artifacts. This document is a description for the beach side; the
biome instance neither ports blocks nor touches production bsp-mcp.
