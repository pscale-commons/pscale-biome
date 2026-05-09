# Minimal package — open exploration

The biome.json shell describes seven environmental currents (storage, cognition, endpoints, persistence, concurrency, federation, cadence) plus an unfolding procedure. The **minimal package** is the smallest set of parts that, bundled together, can sense those currents in any host and unfold accordingly.

This document is the open exploration. Not a spec. Add as you discover; remove as you reduce.

## Working hypothesis (2026-05-09)

The smallest viable bundle is something like:

```
[ bsp() function ]      — TypeScript port of bsp2-star.py (vendored from bsp-mcp-server/src/bsp.ts)
[ sentinel blocks ]     — sunstone, whetstone, agent-id, evolution, manifest, gatekeeper, block-conventions, biome
[ storage adapter ]     — pluggable: fs | local-db | hosted-db | upstream-beach | adapter-chain
[ host sensor ]         — inspects env, filesystem, ports, network reach; returns a conditions block
[ unfolder ]            — reads biome.json branch 8, composes surfaces per sensed conditions
[ surface drivers ]     — small modules: mcp-stdio, mcp-http, beach-server, browser-router, relay-ws, cli — each gated by env
```

That's six layers. Not all needed in every unfolding — surfaces especially are conditional.

## Open questions

### Q1. Is bsp() vendored or imported?

**Option A: Vendored.** Copy `bsp.ts` and `bsp-fn.ts` into `pscale-biome/src/`. Pro: zero dependencies on bsp-mcp's release cadence. Con: drift over time; two sources of truth.

**Option B: Path import.** TypeScript path mapping to `../bsp-mcp-server/src/bsp.ts`. Pro: single source of truth. Con: ties the two repos at the filesystem level; breaks if either moves.

**Option C: Wait for bsp-mcp to publish to npm.** Pro: clean dependency graph. Con: requires bsp-mcp to be packaged for library use, which is currently not the case (it's an executable).

**Leaning toward A** for now (vendor with a comment naming the canonical source), because it keeps pscale-biome self-contained and unblocks work. Re-evaluate when bsp-mcp publishes.

### Q2. What does the host sensor actually inspect?

Candidates (drawn from biome.json branch 8):

- Filesystem write access (path exists? writable? permissions?)
- Database connection strings in env (SUPABASE_URL, DATABASE_URL, PGURI, etc.)
- LLM API keys in env (ANTHROPIC_API_KEY, OPENAI_API_KEY, etc.)
- Network reach (can resolve happyseaurchin.com? can reach a federated beach?)
- Port availability (3001? 8080? something else?)
- Process arguments and config files
- TTY presence (stdin attached? interactive?)
- Browser capabilities if running in a browser context (localStorage? IndexedDB? WebWorker?)
- Phone-specific: Termux? PWA? Background notification access?

Each becomes one bit of a "conditions block" — itself a pscale block written to `biome:9` (metadata) so the next cycle reads what was sensed.

### Q3. Does pscale-biome need its own MCP, or just use bsp-mcp's?

User flagged this: *"We may need to create a new mcp on railway, eg biome-mcp so hold off."*

If the biome only ever consumes bsp() and the substrate primitives, it doesn't need its own MCP — it's a client of bsp-mcp. But if the biome wants to expose **unfolding-related operations** to LLM apps (e.g., "tell me what surfaces this biome currently exposes," "switch tier policy," "wake the embedded loop"), those would need their own tools.

Possible biome-specific tools (not yet decided):
- `biome_status` — return the sensed conditions and current unfolding
- `biome_resense` — re-run the sensor (e.g., after an env change)
- `biome_compose` — re-walk the unfolding procedure
- `biome_expose` / `biome_unexpose` — toggle a surface at runtime

If these emerge, biome-mcp becomes a real thing. For now: defer.

### Q4. What is the smallest first deliverable?

Three candidates, ordered by minimum:

**4a. Sense-and-print** (smallest). A single binary that, when run on any host, prints what biome would unfold there. No commitments. Just observation. Output is a JSON conditions block plus a description of the would-be unfolding.

**4b. Stdio biome** (next smallest). A binary that takes stdin/stdout, exposes bsp() and primitives via the MCP stdio transport, walks biome.json on its own substrate. Equivalent to running bsp-mcp locally with a default filesystem adapter. The "biome on a thumbdrive" shape, minus a UI.

**4c. HTTP biome** (full conditional). Same as 4b but conditionally exposes HTTP surfaces (beach endpoint, browser route, relay) based on env. The first version that can act as a node in the federation.

**Leaning toward 4a** as the first move — it forces the sensor design and produces something useful (you can run it on three hosts and compare outputs) without committing to any surface yet.

### Q5. How does the user "initiate" a biome?

Open. Possibilities:

- `npx pscale-biome` (run-once)
- `npx pscale-biome init` then `npx pscale-biome run` (two-stage)
- A single binary with sub-commands: `biome sense`, `biome unfold`, `biome run`
- Just `biome` (bare command), behaves differently per host
- A library, no binary — invoked from the user's own runtime

User explicitly said *"the same package should work on computer, another on a phone etc."* — so the entry should be portable. `npx`-style works on computer; might need a different shape for phone (Termux supports npx; PWA wouldn't).

Defer this until the sense-and-print exists.

## Reductions to attempt

Once a working bundle exists, ask:

- Can the bundle run with NO LLM key (pure beach/relay mode)? If yes, the LLM is optional, and the package without it is a beach.
- Can the bundle run with NO storage adapter (pure pass-through to upstream beach)? If yes, the storage is optional, and the package without it is a router.
- Can the bundle run with NO surfaces (just sensing, just walking)? If yes, the surfaces are optional, and the package without them is a sensor.

Each "if yes" reduces the package. The minimum is whatever's left when nothing more can be removed without breaking the biome's nature.

## Adjacent considerations

- **xstream is converging.** `feature/block-agents` branch has stripped Supabase, wired a sovereign browser kernel, and is moving toward block-conformal data. xstream may itself become the browser-shape biome unfolding. pscale-biome and xstream should not duplicate work.
- **happyseaurchin's "beach is the surface" change.** No privileged "beach" block name; the directory IS the listing. Biome's storage current may want similar: no privileged block names, the unfolding announces what's there.
- **mobius-2 is the reference agent.** When the biome runs an embedded loop, the loop should follow mobius-class patterns (concern dispatch, function-config aperture, filmstrip, A-loop, C-loop). Don't reimplement; learn the shape and produce a TS analogue if needed, or shell out to mobius if both are present.

## Update log

- **2026-05-09** — Document created. biome.json shell staged. pscale-biome project skeleton initialised. No implementation yet.
