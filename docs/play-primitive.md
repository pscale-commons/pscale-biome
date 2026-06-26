# `play` — the biome's RPG primitive (spec + build status)

*Authored 2026-06-23 (Track B); MCP-wired 2026-06-26. The model-free, packaged RPG engine:
`src/biome/play.py`, with the `play()` entry now exposed as the MCP tool `play` beside
`spark`. Companions: `scene.py` (mechanical helpers + the NHITL test-bench), `fold.py` (the
real-world engagement layer this mirrors). Built, proven model-free, and **wired to the MCP
surface** (`serve.py`, tested locally over `POST /mcp`); deploy is David's to rule.*

## The one idea

`play` is **pure compilation over spark** — it bundles the per-turn substrate reads/writes
into one call so a low-tier LLM playing through MCP pays one round-trip, not five. It adds
**no capability** (everything it does is spark reads/writes underneath) and runs **no
model**: every act of cognition — perception, echo, history-summary, world-weave — is the
*visiting* LLM's, in the player's own app (subscription/BYOK). The host pays for hosting
(blocks) plus the free mechanical verdict; LLM cost is the player's. NPCs are the one
exception (beach-crabs, a paid host service); our NHITL test-bench is the deliberate
exception (we run models to iterate game mechanics, then hand off to HITL).

## The tool

```
play(handle, world, where?, move?, account?, place?, rules?, face?)  ->  frame   (DATA, no model)
```
- **handle** — the located identity (the character/seat).
- **world** — the cosmology (`upperton`, …); selects its root + STI blocks.
- **where** — the scene address; default = the handle's `located` standing.
- **move** — this turn's intention → the window (public contribution); on the ruleset's trigger → the mechanical verdict.
- **account** — the app's rendition of the *prior* turn → appended to the character's own shell `history` (lossless memory). Save-after-narrative by construction.
- **place** — a place-rendition. `face=character` → `spatial-<handle>` (the character's own version); `face=author` → the canonical `<world>-spatial` voicing (the weave committed).
- **rules** — the ruleset block; default = the world's pin, else `nomad`.
- **face** — character / author / designer / observer (CADO; authority gating deferred to the passphrase membrane).

**Returns** the composed frame, as data for the app to render:
`{ world, where, handle, face, S, T, I, room, window:{submitted,waiting,yours}, last, ruleset, status }`
(+ `place_fan` when `face=author`). The app's LLM renders perception + echo *from this*; the server never does.

## The movements (one call)
1. **SAVE** — `account` → shell `history` (append; supernest at nine; lossless — the visitor summarises on demand, the engine never auto-compresses).
2. **VOICE** — `place` → the spatial fold (own `spatial-<handle>`, or the author weave into canon).
3. **SUBMIT** — `move` → the window; on the trigger → the **mechanical verdict** (stat math, free) → the scene advances.
4. **ACCESS** — compose + return the frame.

(RENDER happens app-side, between calls — and the echo it shows the user doubles as the next `account`.)

## The blocks (per world, all 0-9)
| block | is | written by |
|---|---|---|
| `<world>-spatial / -temporal / -identity` | the S / T / I triad | world-author |
| `shell-<handle>` | a character: purpose/history/surface + ruleset stats | player (narrative) · designer (stats) |
| `spatial-<handle>` | the character's OWN version of places (the S×I register) | character |
| `window` | the liquid fan (submissions at a scene) | character, via `play` |
| `scene` | the settled beats (advancing T) | the engine, on resolve |
| `nomad` | the ruleset (game-set) | designer |

## GRIT / NOMAD
- **GRIT (engine)** = `play` + the STI fold + window + a few mechanical **resolution kinds** (stat-contest, ambient, …). Generic, in the tool. *What goes in GRIT = what the biome engine ships.*
- **NOMAD (game-set)** = the `nomad` block — stat schema + resolution config + trigger policy. Swap for `dnd` via `rules='dnd'`. *Modify/replace = a designer-face write.*

The biome partitions these **naturally** (engine = substrate, ruleset = block); no code-split needed, unlike bsp-mcp.

## The spatial fold (lived-in realness)
A character voices its own version of a place → `spatial-<handle>` at the place's spindle (`voice_place`). The **fan** gathers every character's version at an address (`place_fan`). An **author** (a player on upkeep, or later a crab) **weaves** the fan into the canonical `<world>-spatial` voicing (`weave_canon`), preserving the structure beneath. The weave is the *visitor's* LLM (reads the `place_fan` the frame hands it); the engine only commits the result. (`fold.py` does the same for the real world under `surface-<handle>`; the RPG uses the clearer `spatial-<handle>` — parallel, domain-named.)

## History (memory)
`history` in the shell is **lossless**, append-only, supernesting coarse-to-top — a pscale spindle the visitor can read at any dilation. The engine never summarises; the visiting LLM folds-to-summary when it wants context economy (a character-face write to its own history). The crab is this on a sweep. Why save when the app's chat-thread already remembers: (1) a pscale spindle frames the history in logarithmic-compressive form; (2) new sessions / other apps start with the character's knowledge.

## Async resolution
Resolution triggers are **designer policy** in the ruleset: first-reader-after-time-window / n-threshold / commit. Computed lazily by whoever trips it — no central tick, no server model. (Current build: n-threshold = all present seats; time/commit are declared in `nomad`, reader minimal. submit/commit also map to C/A: submit = the receptive gather, commit = the externalised initiative — the A-move's two phases.)

## Cost model (roles)
- **Host** — hosting (blocks). Flat.
- **Player** — LLM in their own app via MCP (subscription/BYOK). The only cognition by default.
- **NPC** — a beach-crab (a paid host service).
- **Testing** — NHITL (run models to iterate) → hands off to HITL.

## Build status
- **Built + proven model-free** (`play.py`): save / submit+verdict / voice+weave / access. Demo runs free (no API).
- **Wired to the MCP surface (2026-06-26).** `serve.py` carries `play` beside `spark`: `tools/list` returns both; `tools/call name=play` dispatches to `play.play(...)` and returns the frame as JSON text (the `run_play` seam, mirroring `run_spark`). `play`/`scene` now act on the store **object** (`load_block`/`save_block`/`list_blocks`), so `play` runs over whatever store the biome holds (filesystem or a remote beach); a bare directory path is still coerced to an `FsStore` at the CLI/demo entrypoints, so the standalone runners are unchanged. **Tested locally end-to-end over `POST /mcp`** — read frame → four submits → free mechanical verdict → the beat fetchable as plain JSON from the beach door — at zero server-model cost. `serve-battery` covers it (49 pass). `play`'s writes are open (the identity membrane gates the spark door, not `play`).
- **Reuses:** `scene.py` (mechanical reads, window, verdict — and the NHITL LLM test-bench used in the live multiplayer test), `fold.py` (the real-world twin).
- **Live-tested (the LLM beat form, `scene_serve.py`):** 4-seat multiplayer — two humans on two computers + an agent + an NPC, emergent aperture-intact play. That form pays per beat; `play.py` is the model-free production form that replaces it.
- **Open:** deploy — David's call: *which* biome-mcp carries `play` (an existing island holding the RPG world, or a dedicated RPG island), noting a second MCP tool is a genome-surface (constitutional) change · membrane-gating `play`'s writes (the deferred passphrase layer) · async time/commit triggers · a visitor-side history-summary helper · retiring `scene.py`'s server-LLM · generalising past the hardcoded Upperton seats (`scene.SPOT`) and the Upperton-pinned `read_S/T/I`.
