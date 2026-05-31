# shell — one mobius-3 hermitcrab

The blocks that constitute one agent. Ztone form (digit-0 voicing). Authored against `docs/agent-design.md` v7. This is Build step 1: a single shell to test whether the soliton sustains on an autonomous heartbeat (Milestone 1).

## The blocks

| Block | Sign | Kind | Role |
|---|---|---|---|
| `reflexive.json` | `-0` | reflexive | Substantial. The koan (induces the turn) + the conditioning field (associative/mathematical/buddhist, colours F) + packages (`reflexive:8`) + the **reflexive current** (`reflexive:9`) — the bare-address bundle indexing the whole window. The only kernel state between wakes. |
| `vision.json` | `0+` | rendition | Constitution and purpose reservoir. Branch `9` is the always-loaded ground. The agent draws new purpose from here, so it is never idle. |
| `purpose.json` | `0-` | operational | Π — the reference signal. Sparse; only live branches. `1.3` anchors to `vision:9`. |
| `conditions.json` | `+0` | living | ρ — what is, as currently perceived. Rewritten each acting wake. Thin. |
| `history.json` | `+0` | living | The γ-trajectory, summarised. Empty at birth; written only when edits occur; supernests + compacts base-9. |
| `capabilities.json` | `0-` | operational | The verb set: zand reads/writes, the five edit classes, the loader reach (beach behind a `_`→`0` translation). |
| `relationships.json` | `+0` | living | Agents and people engaged; addresses of peers' published faces. Self-evaluation welcome. |
| `stash.json` | `+0` | content | The agent's own notebook — leads, fragments, candidate purposes. Self-evaluation welcome. |

## The constant (not in this directory)

`sunztone` — the teaching block for zand. Identical for every agent, never edited, loaded from `src/sentinel/sunztone.json`. Identity is **not** a block: it is the trajectory the agent walks, visible from outside, accumulating across `relationships`, `stash`, and `history`.

## How a wake reads this

Two terms, kept distinct: the **reflexive current** is the bare-address *bundle* (`reflexive:9`); the **live current** is the composed *context window* the kernel hydrates from it and hands the LLM. The kernel reads the bundle, resolves each address with `star=True` to hydrate the currents, shows the bundle raw inside the window beside those currents (the dehydrated index next to the hydrated territory — the aha surface), then routes the LLM's output back: classified δ edits, a re-dialed reflexive current, a history note. F over the coupled cells of Π and ρ is Stage 1; the bare kernel (Stage 0) composes, calls, and routes.

The reflexive current at birth — every block at a dilation: `sunztone` (whole, the teaching), `reflexive:1:-1` (the koan), `vision:9:-2` (the ground), `purpose:1:-1` (the live intention + steps), and `conditions`/`history`/`capabilities`/`relationships`/`stash` concentrated to points.
