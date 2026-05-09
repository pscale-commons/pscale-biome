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

## What this experiment is asking

> Can the five concerns of a pscale node — storage, BSP function, MCP transport, hermit-crab shell, xstream interface — be unified into one package that, when placed on a host, **unfolds** to fit that host's conditions?

Read [docs/biome-design.md](docs/biome-design.md) for the design overview. The seven environmental currents that the unfolding is governed by are at [src/sentinel/biome.json](src/sentinel/biome.json).

## Operating principles

1. **This is not production.** Nothing here ships to a real user. No Vercel deploy. No Railway deploy. No npm publish. Until the user explicitly asks.

2. **Don't push back to source repos.** If you need to update `bsp-mcp-server` or `pscale-beach` or `xstream`, **stop** and tell the user. The vendoring is one-way for a reason.

3. **Don't add features the biome shell doesn't describe.** If a feature is needed, map it to a current in `src/sentinel/biome.json` (storage, cognition, endpoints, persistence, concurrency, federation, cadence). If it doesn't map, the shell needs to grow first.

4. **Sense before you build.** The biome unfolds from conditions, not configuration. Implementation should sense the host (filesystem? port? key? browser?) before deciding a shape.

5. **The minimal package is still being explored.** See `docs/minimal-package.md`. Don't over-implement. Each piece should justify itself by what unfolds on some host.

6. **Vendored files are not yours to modify casually.** Changes to vendored files (bsp.ts, sentinel JSONs, beach handler, etc.) are real architectural decisions. If a vendored file needs to change for the experiment, document why in a commit message and consider whether the change should also flow back to the source repo.

## What's missing (deliberately)

Two of the biome-design.md's five concerns are NOT vendored:

- **MCP transport.** The bsp-mcp server scaffolding (`src/server.ts`, `src/index.ts`, `src/tools/`) was not vendored because the biome's server shape is different — multi-surface, conditional unfolding. Re-author when the unfolding logic is clearer, or vendor with deliberate adaptation.
- **Hermit-crab shell.** Mobius is the reference pattern (Python). The user has updates on a separate drive (pct-soliton work). When that lands and the user surfaces the canonical version, the embedded loop becomes the next vendoring decision — Python sidecar, TS port, or "host runs it externally and the biome just exposes the substrate."

## Open questions

In rough priority:

1. What does "sense the host" actually do? Concrete inspection list at boot time.
2. Vendor or path-import or wait-for-publish for `bsp-mcp-server`'s function code? Currently vendored.
3. Where does the seed wizard live in a unified biome? Currently `src/init/seed.js` from pscale-beach.
4. Is xstream's `App.block-agents.tsx` the right entry, or does the biome need its own React shell?
5. How does the human author the shell when the biome is for them, not an LLM? (xstream-class interface, but for designer face on the biome's own structure.)

## Don't lose track of

- `src/sentinel/biome.json` is the design shell — the most architecturally load-bearing artifact in this project.
- `docs/biome-design.md` is the design overview David and Claude crystallised before this project was scoped.
- `docs/systemic-kernel.json` is the evaluation kernel for "is this proposal systemic or mechanical." Walk it when in doubt about whether a feature you're adding is derived or assembled.
- `docs/protocols/` carries the substrate-wide protocols. Read them before authoring anything that interacts with the federation.

## Provenance

This project began on 2026-05-09 in a session where David and Claude orbited the question: *can the pscale ecology fit into one deployable cell?*

The biome.json shell was authored in that session. Vendoring happened at the end of the session after the design crystallised and David explicitly asked for a separate experimental project. mobius-2 was excluded because canonical updates live on a separate drive that was not accessible.

Source commits at vendoring time:
- `bsp-mcp-server`: `feat/gatekeeper-sentinel` branch, head `ead1902 feat(sentinel): bundle gatekeeper as Tier-1 role-shell at (pscale, gatekeeper)`
- `pscale-beach`: latest local copy
- `xstream`: `feature/block-agents` branch, head `f128864 [UI] Add download story button`
