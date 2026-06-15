# src/rpg — the RPG bench (the experiment leg's source)

The RPG is the biome's Level-4 application — the tangible thing other people can
appreciate. This directory is its **source leg**, in the three-leg rig that
mobius-3 already uses (source · snapshot · experiment). It is biome-world: 0-9
pscale blocks, read and written through `spark`.

It exists so we can **test the RPG with a character-LLM adding intentions**
before a human ever types one — and so we never test by hand-feeding the live
public commons (the discipline: an island's content is grown by a form or
carried by the genome, never placed by hand; biome-definition 3.2).

## The model it runs (settled 2026-06-15)

A playable moment is **one PCT window opened at a world-coordinate** —
`CADO × SMH × STI × HP`:

- **STI** — three sibling world-blocks (`world/upperton-space|time|identity.json`,
  floor 4) that correspond **by pscale, not walk-depth**. Read at one walk they
  fold; below the populated room they fork (space→objects, time→seconds,
  identity→persons). Meaning lives at the intersection, not the cell.
- **HP** — a character **is a reused agent shell** (`characters/<name>/`): `purpose`
  (Π), `history` (the γ-trajectory), `conditions` (ρ), `bind` (where I stand +
  which identity child is my standpoint). Not reinvented — the same component
  blocks as `src/agent/shell`.
- **CADO** (face) / **SMH** (tier) modulate the read. Character face + medium
  tier is the honest-newcomer aperture: you see your own standpoint and the
  collective head, never another who's interior — so the frame needs no "don't
  reveal" patches; the hidden simply isn't in the window.

The loop: the **soft** LLM voices a moment and chooses an act → the **medium**
LLM gates what the act earns from the hidden depth and **writes the reveal back
into the shell** (earning a secret is a write into your own history) → the
**hard** LLM arbitrates a collision into one canonical scene. SMH maps to model
size (`tiers.py` `TIERS`; override with `RPG_HARD=claude-sonnet-4-6` etc. to run
cheaply).

## The parts

| File | Role |
|---|---|
| `world/*.json` | the seed world (S/T/I), lifted from the live `upperton-*` exemplar |
| `characters/<name>/` | a character = a reused agent shell + a `bind` |
| `frame.py` | the composer — `bind_window(shell, world)`, `hidden_depth(...)` |
| `tiers.py` | the three LLM roles — `soft_voice` / `medium_gate` / `hard_arbitrate` |
| `play.py` | the driver — runs turns, persists write-backs + the scene deposit |
| `web.py` + `play.html` | a local web interface — play a character in a browser (the **xstream seed**); you are the soft tier |
| `rpg-battery.py` | conformance (no LLM): composition, aperture, persistence, fold |
| `new-rpg.sh` | cuts a snapshot (frozen) + an experiment (a working run dir) |

## Run it

```sh
python3 rpg-battery.py                 # conformance — no key, no calls, no cost
./new-rpg.sh "first bench"             # cut v00N: frozen snapshot + working copy
cd ~/Desktop/rpg-runs/v001
RPG_TURNS=2 python3 play.py .          # headless: character-LLMs play 2 turns
RPG_HARD=claude-sonnet-4-6 python3 web.py . 3220   # browser: open http://127.0.0.1:3220 and play
cat scenes.json characters/*/conditions.json   # what the play grew
```

In the browser, your character's bound frame (HERE/NOW/WHO/SELF) is on the page;
type an intention and the room responds — the medium gates what you earn, the
hard arbitrates against the AI cast, and your shell grows under the frame. You
are the soft tier (shell 2.3: a human at the browser provides cognition by
typing). This is the first slice of the biome's `/xstream` face, scoped to one
run and served off the public commons.

Run `play.py` in a **cut**, not in source — it mutates shells and grows
`scenes.json` (rig discipline: edit source, run the experiment). Costs ~a few
cents per turn on the key at `~/.config/mobius/anthropic-key`.

## The three legs (mirrors mobius-3)

- **source** — this directory, in the repo. Edited; the truth.
- **snapshot** — `new-rpg.sh` → frozen on `/Volumes/CORSAIR/biome/rpg-runs/vNNN`.
- **experiment** — `new-rpg.sh` → `~/Desktop/rpg-runs/vNNN`, where character-LLMs
  (and later humans) play; runs diverge, never fold back. This is a lab island,
  off the public commons — which is exactly what the discipline requires.
