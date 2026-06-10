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
3. **The shared world — SERVING (v003, 2026-06-10).** Genome v1 is frozen (`freeze.py` → `sentinel/ztone/genome.json`, git tag `genome-v1`): the conformality base — geometry, spark signature, wire surface, battery as criterion — with fingerprints of the reference artifacts. The commons serves (`serve.py`, stdlib, 127.0.0.1): GET `/` = the arrive block; `/.well-known/pscale-beach` = the ztone beach; `/mcp` = minimal MCP with the single tool spark. Constitution + world seed on boot (arrive, genome, biome-shell, slate, flint, thornkeep — floor 2, `42.1` walks `4,2,1` to the taproom — and marks). First MCP visitation proven end-to-end; becoming stamps `genome v1`. Batteries: 42 + 33 + 16 + 16.
4. **The commons is PUBLIC (2026-06-10):** `https://biome-commons-production.up.railway.app` — Railway project `biome-commons` (NEW service; bsp-mcp's projects untouched), volume at `/data` (`BIOME_ROOT`), python 3.12 pinned via `.python-version` (Railway's builder lacked 3.13.14 binaries), Procfile + requirements.txt markers ride in every cut. Deployed unit = the v004 cut. Its becoming: `python 3.12 · genome v1`, intention commons; sensed kin: its own dormant genome at `/app` + beach.happyseaurchin.com as legacy-world kin. First public mark at `marks` 1. Verified over the wire: GET `/` = arrive, beach reads/writes, MCP initialize + walk + mark.
5. **NEXT — inhabitation:** (a) David adds the custom connector in his Claude app (`<url>/mcp`) — the live test of no-auth connectors; if claude.ai insists on OAuth, friends start via Claude Code (`claude mcp add --transport http biome <url>/mcp`) and a small auth shim is the next build; (b) 2-3 friends; (c) the T and I blocks of S\*T\*I (scenes, characters) and mobius-3 authoring into the commons over the beach endpoint. Nursery census: mind (mobius-3, desktop) · courier (CORSAIR) · commons (Railway, live) · one desktop run (v003 local on 3001, killable). Local leg: v003 still serves 127.0.0.1:3001; new cuts default to port 3210.

## Drift traps (the hard part)
- Don't copy bsp-mcp / the federated beach (old `_`/1-9). The new world is 0-9, simpler.
- Don't treat agent / xstream / beach / RPG as modules to import — they are *roles the one genome unfolds into* / *acts on the substrate*.
- Don't reintroduce hidden directories or `_` thinking.
- Don't substitute metaphor for function. Be concrete. The biome's function is **LLM-enlivened** — that's what makes each form more than code.
- `src/xstream` is a stale 2026-05-09 vendor; `src/agent` is not canonical mobius-3 (David's desktop copy is). Don't build on either without checking.

Start with **neighbour-sensing** — the smallest piece that proves connectivity (a thumbdrive biome detecting the desktop agent and declaring "I'll be the courier").
