# Hand-over — pscale-biome (to the next instance, 2026-06-10)

You're picking up an experimental project at a deliberate pause. The work is conceptually subtle and **drift is the main hazard** — it has happened repeatedly here, including pulls back toward copying the old bsp-mcp/beach. Read this and the docs before building.

## Read first, in order
1. `CLAUDE.md` — standing rules (don't propagate upstream; pscale notation: one-decimal addresses, comma walks; **don't touch production bsp-mcp/beach**).
2. `docs/biome-shape.md` — the **current synthesis**: what the biome is, the connectivity gap, the three roles, the forward build, and the drift traps. This is the shape to hone toward.
3. `docs/spark-spec.md` — the spark primitive and the three layers (L1 code / L2 blocks / L3 meaning).
4. `docs/biome-design.md` — the original "one package, unfolds to fit host" brief.

## Where we are (built, on branch `feat/mobius-3-agent`)
- **The spark set** (`src/spark/`) — the 0-9 pscale primitive: `spark.py` + `spark.ts` (parity, 42/42 and 33/33), with `slate.json` (teaching) + `flint.json` (manual) + `tezt/`. Clean geometry: no hidden directories, voicing = relational×state, ring-`0` as head, `fold` + `refer/star` included. Supersedes zand/sunztone/whetztone (now legacy in `src/zand`, `src/sentinel`).
- **The biome unfolding** (`src/biome/`) — `sense.py` (host sensor), `unfold.py` (reads the 0-9 shell `src/sentinel/ztone/biome.json` through spark, picks currents from conditions), `store_fs.py` + `beach.py` (a filesystem store served by spark), `activate.py` (the first writing activation). Proven once as **v001**, a local filesystem beach.
- **The three-leg dev rig** — `src/biome/new-biome.sh` cuts a generation: frozen snapshot → `/Volumes/CORSAIR/biome/biome-runs/`, runnable experiment → `~/Desktop/biome-runs/`, from the git source. **Edit source only; run the desktop copy; the CORSAIR snapshot stays frozen.** (Mirrors the mobius-3 setup.)

## The next build — pointed at the RPG
1. **Neighbour-sensing** — DONE (v002, 2026-06-10). `sense.py` detects kin: local biome instances (activated via their `blocks/biome.json` becoming, dormant via a cut genome), agent shells (the mobius shape), and answering beaches (probed at `/.well-known/pscale-beach`, world distinguished: legacy `_` vs ztone 0-9). Plus `sense_capacity` (disk, removable surface). Detection is reading — a neighbour's identity is its becoming-block, read through spark.
2. **Role-unfolding** — DONE (v002). The shell grew the role vocabulary at 8.8 (compose, subnested): 8.81 mind, 8.82 courier, 8.83 commons, 8.84 silent substrate — address 8.8N walks 8,8,N. `unfold.resolve_role` senses which condition holds and reads the role's meaning from the shell; the becoming-block records the intention + sensed kin at key 9. Proven: the desktop v002 declared commons (sensing v001, the CORSAIR snapshots, the legacy beach); the same genome sensed read-only from /Volumes/CORSAIR declared courier with 3 kin to carry between. `tezt/tezt_biome.py` 16/16.
3. **The shared world — NEXT** — the commons hosts the S\*T\*I RPG world-blocks; the agent authors; players read and write. **The RPG is the destination** — the tangible thing that makes all this real to other people. Keep the line to it short. The role intention is recorded but not yet *grown into* — a commons that actually serves (an endpoint another biome can read), and the first world-blocks on it, is the move that turns declared roles into an ecology.

## Drift traps (the hard part)
- Don't copy bsp-mcp / the federated beach (old `_`/1-9). The new world is 0-9, simpler.
- Don't treat agent / xstream / beach / RPG as modules to import — they are *roles the one genome unfolds into* / *acts on the substrate*.
- Don't reintroduce hidden directories or `_` thinking.
- Don't substitute metaphor for function. Be concrete. The biome's function is **LLM-enlivened** — that's what makes each form more than code.
- `src/xstream` is a stale 2026-05-09 vendor; `src/agent` is not canonical mobius-3 (David's desktop copy is). Don't build on either without checking.

Start with **neighbour-sensing** — the smallest piece that proves connectivity (a thumbdrive biome detecting the desktop agent and declaring "I'll be the courier").
