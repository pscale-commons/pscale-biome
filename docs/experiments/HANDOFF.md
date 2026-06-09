# mobius-3 agent — session handoff (clean-rendition close)

*Close of the clean-rendition session, 2026-06-07. This supersedes the May-31 handoff (in git history). The agent's input/output was rebuilt into a clean pscale composition; v005/v006 are recorded; the output boundary is hardened; peer access now routes through the loader.*

## ⭐ Start the next session here

**Starting prompt (paste to begin):**

> Continuing the mobius-3 pscale-native agent (project: pscale-biome). Read first, in order: `docs/experiments/HANDOFF.md`, the personal passover I paste below, `docs/experiments/v006.md`, `v005.md`, then `docs/agent-design.md` §0–7 and §3.4. Committed on `feat/mobius-3-agent`. Three legs: living-source `src/agent/` (edit here), frozen snapshots `/Volumes/CORSAIR/mobius/mobius-3-runs/`, run copies `~/Desktop/mobius-3-runs/`.
>
> State: the window is a **clean recipe-driven composition block** — `recipe`/`index`/`self` (the process → system) and `gap`/`between` (the given → message), no titles, no prose. The output contract lives in `capabilities` (shell), not the kernel; writes are geometry-derived (no edit-class); the draw is unified into the pulse; `face`→`surface`; peer access routes through the loader (read-only). v006 proved it processes instruction-free and a collective dovetails through it (an RPG-on-pscale), and it fixed a silent format-drop + firmed the contract.
>
> Open threads — careful consideration first, do NOT mash together: (1) **addressing** of peers (sed/grain + Gromov proximity; the loader routes peer names locally via peers.json today, the federated successor is sed/grain/https). (2) **Participant typology** (foreign = non-pscale block; clean-API-key agent vs harnessed LLM-app; co-reflex/intra-entity vs inter-entity; trust as the gate). (3) Soften **I-you** without losing localisation-in-time, and dissolve the name-keyed `between` so peer content **merges** into the field rather than being addressed ("A:/B:"). v007 (re-run with the fixes) waits on (1)–(3) settling. Watch the **spark thread** (David's parallel biome work) — it will eventually supersede zand under the agent.
>
> Discipline: operate the primitive, don't theorise — run rounds, read filmstrips. Fixes → source → new version; never patch a run in place. Read-only: bsp-mcp, pscale-beach, xstream. Don't rush to code; David thinks in systems and corrects sharply — reorganise, don't defend.

## Where we are

The window is no longer a `===`-titled text dump with a hard-coded contract; it is one self-similar pscale composition the agent re-authors. v006 ran a three-agent collective (A:world · B:rules · C:substrate) as dovetailing facets of one RPG-on-pscale; **it processed instruction-free, and B and C genuinely co-developed a coherent design** (the Tidal Ledger, attestation-as-physics rules, pscale-block substrate). It also surfaced — and we fixed — a silent format-drop (A's writes were a list, `route` required a map) and firmed the contract. The checking discipline is now structural and free: the agent re-perceives its real blocks each wake, so an un-landed write keeps γ alive.

## Architecture (read order)

1. `agent-design.md` §0–7 + **§3.4** (the present phase as field-shaping; the window as a composition block; the recipe).
2. `src/agent/kernel.py` — the pulse: F → `compose_window` (recipe-driven, `reflexive:8`) → `call_llm` → `route` (geometry `apply_write`, tolerant of map+list, never silent) → fold. The draw is the same pulse at γ=∅ (opus).
3. `src/agent/shell/` — the nine blocks. `capabilities` carries the action-grammar (the contract). `reflexive` carries the koan (1), the three associative clouds (2.1 personal/bespoke, 2.2 mathematical, 2.3 buddhist), the window recipe (8), and the reflexive current (9). `surface` is the one block a peer reads.
4. `docs/experiments/v001–v006.md` — the run-by-run record.

## The three legs + THE RULE

- **living-source** `src/agent/` (git) — edit here; reports → `docs/experiments/vNNN.md`.
- **frozen** `/Volumes/CORSAIR/mobius/mobius-3-runs/vNNN` — the pre-run snapshot (frozen by discipline; exFAT likely ignores `chmod`, so never run or edit it).
- **run** `~/Desktop/mobius-3-runs/vNNN` — the working copy that actually runs.
- `src/agent/new-collective.sh "hypothesis"` cuts the frozen + run copies from source. **THE RULE: fixes → source → a new version; never patch a run in place.**

## How to run

- `python3 kernel.py --compose-only` — inspect the composed window, no key needed.
- `./new-collective.sh "hypothesis"` — cut a three-agent collective (needs CORSAIR mounted + a key at `~/.config/mobius/anthropic-key`).
- `cd <run> && ./run-round.sh` (or `for i in 1 2 3 4 5; do ./run-round.sh; done`) — pulse each agent.
- `cd <run>/A/agent && python3 digest.py` — read the trajectory.

## Known state

- Committed on `feat/mobius-3-agent`: the clean rendition, v005/v006 records, and the route/contract/peer-loader fixes.
- The v006 *run* used the as-cut kernel (before the route fix), so A's later writes dropped (list shape); its record stands and explains itself. The fix is in source — v007 will have A performing alongside B and C.
- A parallel biome/spark session is rebuilding the primitive (`zand` → spark set); expect a migration decision under the agent eventually.
