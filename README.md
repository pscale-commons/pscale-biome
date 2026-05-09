# pscale-biome

> **Status: Experimental.** Not production. Not deployed. Exploring whether the five concerns of a pscale node — storage, BSP function, MCP transport, hermit-crab agent shell, xstream interface — can be unified into one package that unfolds into whatever host receives it.

## What this is

A working tree assembled from existing production codebases (`bsp-mcp-server`, `pscale-beach`, `xstream`) plus a design shell (`src/sentinel/biome.json`). The goal is to discover the **minimal package** — the smallest bundle that, when placed on a host, becomes a functioning biome.

The design overview is in [docs/biome-design.md](docs/biome-design.md). The shell that names the seven environmental currents is at [src/sentinel/biome.json](src/sentinel/biome.json).

## What's NOT this

- This is not `bsp-mcp-server`. That is the production MCP service running on Railway.
- This is not `pscale-beach`. That is the production beach package on Vercel.
- This is not `xstream`. That is the production interface at xstream.onen.ai.
- Changes here MUST NOT propagate to those repos. This is a separate experimental working tree with its own git history.

## Layout

```
src/
├── bsp/                    — bsp() function (vendored from bsp-mcp-server)
│   ├── bsp.ts                walker (DO NOT modify; port of bsp2-star.py)
│   ├── bsp-fn.ts             unified bsp() with shape derivation
│   ├── locks.ts              sha256 lock salt namespaces (compatibility with prod)
│   └── keys.ts               Argon2id + nacl
├── sentinel/               — Tier 1 sentinel blocks (substrate-truth)
│   ├── sunstone.json         geometry teacher
│   ├── whetstone.json        bsp() operational reference
│   ├── agent-id.json         addressing model
│   ├── evolution.json        five-level ecosystem map
│   ├── manifest.json         constitution index
│   ├── gatekeeper.json       L1→L2 admission shell
│   ├── block-conventions.json  canonical block-shape catalogue
│   ├── progression.json      orientation flow
│   └── biome.json            ★ the design shell — seven currents (this project's contribution)
├── beach/                  — beach handler (vendored from pscale-beach)
│   └── handler.js            /.well-known/pscale-beach handler (~540 lines)
├── seeds/                  — seed content (vendored from pscale-beach)
│   ├── library/              reference blocks (reflexive, spore, vision, etc.)
│   └── templates/            operator-presence scaffolds (passport, shell, etc.)
├── init/                   — seed wizard (vendored from pscale-beach)
│   └── seed.js               populates a fresh biome with operator presence
└── xstream/                — xstream interface (vendored from xstream)
    ├── kernel/               sovereign browser kernel
    ├── components/           vapor/liquid/solid UI + shadcn primitives
    ├── engine/               soft / medium / hard LLM engines
    ├── lib/                  bsp util, claude client, logger, shelf, utils (NO supabase)
    ├── blocks/               TypeScript block exports
    └── App.block-agents.tsx  the post-Supabase reference app

docs/
├── biome-design.md         — design overview (David's draft)
├── minimal-package.md      — open exploration: what's irreducible?
├── systemic-kernel.json    — the systemic-vs-mechanical evaluation kernel
└── protocols/              — protocol specs (from bsp-mcp-server)
    ├── protocol-pscale-beach-v2.md
    ├── protocol-xstream-frame.md
    ├── protocol-agent-shell.md
    ├── protocol-block-references.md
    ├── presence-via-marks.md
    └── beach-crab-ladder.md
```

## Provenance

Every file is either authored here or vendored from a specific source. Track changes from upstream with care.

| Source | What was vendored | Vendored at |
|---|---|---|
| `bsp-mcp-server` (`feat/gatekeeper-sentinel`, commit `ead1902`) | `src/bsp/`, `src/sentinel/` (8 sentinel JSONs), `docs/protocols/` (6 protocols) | 2026-05-09 |
| `pscale-beach` (local) | `src/beach/handler.js`, `src/seeds/library/`, `src/seeds/templates/`, `src/init/seed.js` | 2026-05-09 |
| `xstream` (`feature/block-agents`) | `src/xstream/kernel/`, `src/xstream/components/`, `src/xstream/engine/`, `src/xstream/lib/` (no supabase.ts), `src/xstream/blocks/`, `App.block-agents.tsx` | 2026-05-09 |
| `happyseaurchin` (local) | `docs/systemic-kernel.json` | 2026-05-09 |
| User draft | `docs/biome-design.md` | 2026-05-09 |
| This project | `src/sentinel/biome.json`, README, CLAUDE.md, docs/minimal-package.md | 2026-05-09 |

Mobius / mobius-2 was deliberately NOT vendored — the user has updates on a separate drive (pct-soliton work) and the canonical version is being tracked down.

## The five concerns (per biome-design.md)

| # | Concern | Source code in this tree |
|---|---|---|
| 1 | Storage (beach surface) | `src/beach/handler.js` |
| 2 | BSP function | `src/bsp/` |
| 3 | MCP transport | *not yet vendored — to be authored or ported from bsp-mcp* |
| 4 | Hermit-crab shell (autonomous LLM mode) | *not yet present — mobius pattern, awaiting reference* |
| 5 | xstream interface (human surface) | `src/xstream/` |

Two of the five concerns are missing from the working tree. That's part of what the experiment is for — figuring out what those become when the biome is the unification rather than the federation.

## The open question

What's the **minimal package**? See [docs/minimal-package.md](docs/minimal-package.md).

## License

TBD.
