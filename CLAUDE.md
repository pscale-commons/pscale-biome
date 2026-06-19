# pscale-biome — to the next instance

## Stop. Read this before touching anything.

This is an **experimental working tree**. The code here was vendored from three production codebases on 2026-05-09. Changes you make here must NEVER be propagated upstream without an explicit instruction. This project exists to discover what a unified biome package looks like — it is not a contribution path back to its sources.

## Terminology — use exactly these

| Term | Means |
|---|---|
| `bsp-mcp` (production) | The MCP service running at `https://bsp.hermitcrab.me/mcp/v1` on Railway. Source: `pscale-commons/bsp-mcp-server` on GitHub, local at `/Users/davidpinto/Projects/bsp-mcp-server/`. **DO NOT MODIFY THIS PROJECT.** |
| `pscale-beach` (production) | The beach package. Source: `pscale-commons/pscale-beach` on GitHub, local at `/Users/davidpinto/Projects/pscale-beach/`. **DO NOT MODIFY THIS PROJECT.** |
| `xstream` (production) | The interface running at xstream.onen.ai. Local at `/Users/davidpinto/Projects/xstream/`. **DO NOT MODIFY THIS PROJECT.** |
| `pscale-biome` (this project) | The experimental working tree. The only project you may modify. |

If you hear or read "biome" in conversation, it means this project unless explicitly qualified.

## Pscale notation in conversation and code

When discussing or writing pscale addresses (the biome's pure-digit form):

- **Address** — written with exactly one decimal point, pinned to the floor. Example: `30.5` on a floor-2 block. The decimal is a floor anchor, not a separator. Multi-dot forms like `3.0.5` are forbidden — they were pre-bsp legacy and they read as a structural hazard.
- **Walk** — the digit sequence the walker traverses, written with commas. Example: address `30.5` walks `3,0,5`. Address `1.234` walks `1,2,3,4`.

This applies to prose, code comments, JSON examples, and any output a Claude instance produces in this project. The address form has one decimal; the walk form has commas. Never mix.

## Two worlds — the boundary (read when anything feels mixed)

Two block-worlds exist and must never interbreed. They are mechanically distinguishable — a block cannot be in both:

| | **the beach** (old world) | **the biome** (new world) |
|---|---|---|
| Geometry | `_` semantic key, hidden directories, star-as-door, digits 1-9 | `0` as semantic digit, no hidden positions, refs as plain leaves, digits 0-9 |
| Function | `bsp()` — bsp-mcp on Railway | `spark` — `src/spark/` |
| Lives at | production repos, beach.happyseaurchin.com, xstream.onen.ai | this repo (genome source) · `~/Desktop/biome-runs/` (live instances) · `/Volumes/CORSAIR/biome/` (frozen snapshots) · the commons host when it exists |
| Status | mature, production, being built on | experimental, contained |

**The mechanical test** for any stray JSON: `_` anywhere in its keys → beach-world; pure single-digit keys with `0` as semantic → biome-world. (`sense._probe_beach` applies the same test to substrates: `world: legacy | biome`.)

**Crossing rules:**
1. No beach-world block is ever copied into a biome store. **Re-author in 0-9; never port.** (The slate already carries the biome's native Thornkeep at 3.6 — that is the RPG seed, not any old-world Thornkeep file.)
2. No biome block is ever written to a federated beach.
3. The biome may *read* beach-world substrates only as labeled foreign kin (`kind: beach, world: legacy`) — sensing, never storage.
4. In this repo, biome-world is exactly: `src/spark/`, `src/biome/` (the constitution blocks live at `src/biome/constitution/`), and `src/agent/` (the mobius-3 source — spark-speaking since the v007 recut). Everything else under `src/` — including all of `src/sentinel/` — is beach-world vendor or superseded drafts (`src/zand` and the sentinel `*ztone*` stones were the 0-9 first pass; "ztone" is retired terminology from that intermediary stage) — reference only, never built on.
5. **Separate doors (genome v3):** the old federation's wire door is `/.well-known/pscale-beach`; the biome's is `/.well-known/biome-beach`. A biome *signposts* the old door (404 + note), never serves it, and its write membrane refuses any content carrying a non-digit key (notably `_`).
6. **Separate routing language:** "the beach" / "take me to the beach" belongs to the old world (bsp-mcp). The biome answers to "the commons" / "Thornkeep". Never use beach-language in biome invitations, tool descriptions, or connector names — an LLM holding both connectors routes by these words.
7. **Vocabulary crossings are deliberate.** Old-world *convention* words (lighthouse, passport, pool, shell:handle colon-naming, …) do not enter biome blocks, code, or conventions silently — not even when another Claude instance carries them in via a block. Flag the provenance and get it ruled by David first. Already-ruled shared substrate-nouns: block, walk, marks, beach-in-compounds (biome-beach), and lighthouse (ruled 2026-06-11: the enduring per-space orientation block — the Alexandria sense; a clearing empties, a lighthouse stands). Z-era words (zand, ztone, sunztone, whetztone) never appear in biome-world artifacts, including test fixtures. Colon-prefixed block names (`grain:`, `sed:`, `shell:handle`, …) are the old world's category system — biome block names are plain hyphenated words (ruled 2026-06-11: `surface-keel`, never `surface:keel`).

## What this experiment is asking

> Can the five concerns of a pscale node — storage, BSP function, MCP transport, hermit-crab shell, xstream interface — be unified into one package that, when placed on a host, **unfolds** to fit that host's conditions?

Read [docs/biome-design.md](docs/biome-design.md) for the *founding* design overview (2026-05-09). The seven environmental currents that the unfolding is governed by live in the **live** biome-world shell [src/biome/constitution/biome.json](src/biome/constitution/biome.json) (`0`-keyed). ([src/sentinel/biome.json](src/sentinel/biome.json) is the original `_`-keyed shell from the founding session — superseded vendor per rule 4; historical origin only.)

## Live: the real-world spatial island (2026-06-19)

A worked, deployed instance of the biome principle — a real-world pscale spatial map served as its **own biome island** (a separate cosmology from the RPG commons), with a human walker, a name→URL resolver, and biome-mcp. A new session can find and use it:

- **Live biome:** `https://realworld-biome-production.up.railway.app` — the door, `/mcp` (biome-mcp), `/resolve?name=<place>` (the gazetteer: name → URL, derived live), and `/world` (the walker). Read its `lighthouse` block first for orientation.
- **Human UI:** `https://happyseaurchin.com/virtual-ai-agents/real-world/`.
- **Source:** branch `feat/real-world-spatial` — blocks in `src/biome/world/earth/`; `discover.py` (+ `serve.py` `/resolve`), `grow.py`, `locate.py`, `cartographer.py`, `federate.py`. Design: [docs/real-world-spatial-spec.md](docs/real-world-spatial-spec.md) + [docs/discovery-lighthouse-gazetteer.md](docs/discovery-lighthouse-gazetteer.md). Memory: `project_real_world_spatial`.
- Root block `real-world-original` ("the solar system", Earth = digit 3); spine room 0 → solar system +11. **Reads are free** (a plain fetch + the spark function + a URL); the per-biome MCP is a write-gate + convenience, not needed to read.

## Operating principles

1. **This is not production.** Nothing here ships to a real user. No Vercel deploy. No Railway deploy. No npm publish. Until the user explicitly asks.

2. **Don't push back to source repos.** If you need to update `bsp-mcp-server` or `pscale-beach` or `xstream`, **stop** and tell the user. The vendoring is one-way for a reason.

3. **Don't add features the biome shell doesn't describe.** If a feature is needed, map it to a current in the live shell `src/biome/constitution/biome.json` (storage, cognition, endpoints, persistence, concurrency, federation, cadence). If it doesn't map, the shell needs to grow first.

4. **Sense before you build.** The biome unfolds from conditions, not configuration. Implementation should sense the host (filesystem? port? key? browser?) before deciding a shape.

5. **The minimal package is still being explored.** See `docs/minimal-package.md`. Don't over-implement. Each piece should justify itself by what unfolds on some host.

6. **Vendored files are not yours to modify casually.** Changes to vendored files (bsp.ts, sentinel JSONs, beach handler, etc.) are real architectural decisions. If a vendored file needs to change for the experiment, document why in a commit message and consider whether the change should also flow back to the source repo.

## What's missing (deliberately)

Two of the biome-design.md's five concerns were NOT vendored at the start. Both have since been re-authored biome-native (status updated 2026-06-13) — don't re-create them:

- **MCP transport.** ~~Not vendored.~~ **Now exists, biome-native:** `src/biome/serve.py` serves the single `spark` tool at `/mcp` (alongside the `biome-beach` wire door). The original bsp-mcp scaffolding (`src/server.ts`, `src/tools/`) was deliberately not vendored — and should not be.
- **Hermit-crab shell.** **Now exists, biome-native:** `src/agent/` IS the mobius-3 reference, spark-speaking since the v007 recut (the collective runs there; `mind.py` is the embedded-cognition form). The "separate drive / pct-soliton" note is historical.

## Open questions

These were the founding open-questions (2026-05-09). Most are now settled — status annotated inline (updated 2026-06-13); kept for provenance, not as live questions.

1. What does "sense the host" actually do? Concrete inspection list at boot time. → **ANSWERED:** built at `src/biome/sense.py` (`sense_neighbours`, `sense_capacity`); `unfold.py` resolves a role from it.
2. Vendor or path-import or wait-for-publish for `bsp-mcp-server`'s function code? → **MOOT:** the biome's function is the **spark set** (`src/spark/`), not `bsp()`. bsp-mcp stays an old-world reference; nothing is imported from it.
3. Where does the seed wizard live in a unified biome? → **OVERTAKEN by the face:** the biome serves its own inhabitable page; seeding is genome-owned (constitution, refreshed on boot) + store-owned (world/marks, grown by guests).
4. Is xstream's `App.block-agents.tsx` the right entry, or does the biome need its own React shell? → **OVERTAKEN:** the biome serves its own page at `/xstream` from `serve.py` (one deployment, no second repo). See `docs/face-handover.md`.
5. How does the human author the shell when the biome is for them, not an LLM? → **THIS IS THE ACTIVE FRONT — "the face":** the face IS the biome's xstream-form; humans are inhabitants, typing is cognition. See `docs/face-handover.md` and the memory `project_biome_shape.md` (items 16–17).

## Don't lose track of

- **The live design shell is `src/biome/constitution/biome.json`** (biome-world, `0`-keyed) — the most architecturally load-bearing artifact in this project. (`src/sentinel/biome.json` is the *original* `_`-keyed shell from the founding session — superseded vendor per rule 4; read only as historical origin, never edit it as the live shell. Both carry the same seven currents, in the two worlds' geometries.)
- `docs/biome-design.md` is the design overview David and Claude crystallised before this project was scoped.
- `docs/systemic-kernel.json` is the evaluation kernel for "is this proposal systemic or mechanical." Walk it when in doubt about whether a feature you're adding is derived or assembled.
- `docs/protocols/` carries the **old-world (beach) federation protocols** — `_`/1-9, hidden directories, star-as-door, colon-named blocks, `/.well-known/pscale-beach`. They describe the *legacy* federation, **not the biome's**. The biome federates via the `biome-beach` door in pure 0-9 (`src/biome/serve.py`, rules 4–7). Read protocols/ only to understand the old world; never import its mechanics into biome-world. (Each file now carries an old-world banner.)

## Provenance

This project began on 2026-05-09 in a session where David and Claude orbited the question: *can the pscale ecology fit into one deployable cell?*

The biome.json shell was authored in that session. Vendoring happened at the end of the session after the design crystallised and David explicitly asked for a separate experimental project. mobius-2 was excluded because canonical updates live on a separate drive that was not accessible.

Source commits at vendoring time:
- `bsp-mcp-server`: `feat/gatekeeper-sentinel` branch, head `ead1902 feat(sentinel): bundle gatekeeper as Tier-1 role-shell at (pscale, gatekeeper)`
- `pscale-beach`: latest local copy
- `xstream`: `feature/block-agents` branch, head `f128864 [UI] Add download story button`
