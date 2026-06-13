# ztone — phased plan

> 🗄️ **Retired intermediary-era document (2026-05-28) — "ztone" terminology is retired.** This describes the z-era first pass (zand/sunztone/whetztone) at pure-digit pscale, **superseded** by the spark set (slate/flint/spark, `src/spark/`); the agent line closed the z-era at the v007 recut (2026-06-12). Reference/history only — do **not** treat the phases here as the live plan. Current: the memory `project_biome_shape.md`, `docs/spark-spec.md`.

Trajectory from the foundational primitive (done) to full ecosystem deployment. Phases 1-3 are complete; phases 4-10 are recommended in order but each can pick up independently.

## Phase 1 — Harden the primitive ✓ DONE

**Outcome:** `zand.py` (canonical) + `zand.ts` (port) + 81-test battery + parity infrastructure. Three independent federated sessions have each passed the full suite from sunztone+whetztone alone.

Artifacts:
- `src/zand/zand.py` — canonical Python implementation
- `src/zand/zand.ts` — TypeScript port with same semantics
- `src/zand/zand-cli.ts` — JSON-in JSON-out CLI for cross-impl testing
- `src/zand/test_zand.py` — 37 internal unit tests
- `src/zand/tezt/` — 10 test batteries, 81 tests; `run-tezt.py` driver; `parity-test.py` for py↔ts
- `src/zand/migrate.py` — `_` → `0` key translator
- `src/sentinel/sunztone.json` + `whetztone.json` — teaching blocks
- `tezt-handoff/` — federated handoff package (also at `~/Downloads/tezt-handoff/`)

## Phase 2 — Translate the rest of the sentinel ✓ DONE

**Outcome:** All seven underscore-era sentinel blocks have a ztone-form counterpart at `src/sentinel/ztone/`. Migration tool ships at `src/zand/migrate.py`.

Translated:
- `agent-id.json` (floor 1)
- `block-conventions.json` (floor 1)
- `evolution.json` (floor 2)
- `gatekeeper.json` (floor 1)
- `manifest.json` (floor 1)
- `progression.json` (floor 1)
- `biome.json` (floor 1)

The text content of these blocks is preserved verbatim. References inside their text strings that mention `_` notation are unchanged — those should be updated manually as the blocks come into active use, since the right replacement depends on intent (some `_` references describe the historical underscore convention; others describe addresses that should now use digit-0).

## Phase 3 — TypeScript port + parity tests ✓ DONE

**Outcome:** `zand.ts` passes 81/81 parity with `zand.py` across all batteries. Strict-mode typecheck clean. Enables the biome's TypeScript stack to use ztone directly.

Decision recorded: Python remains canonical reference; TypeScript runs parity tests against Python's outputs. Future ports (Rust, Go, etc.) should do the same.

---

## Phase 4 — Substrate adapters (NEXT)

**Estimated effort:** 2-3 sessions.

The primitive sees only JSON dicts in memory. Substrate adapters are how blocks are loaded from / persisted to various backends. The `block_loader` parameter is the interface.

Files to create:
- `src/substrate/filesystem.py` — directory-of-JSON-files adapter (thumbdrive biomes)
- `src/substrate/localstorage.ts` — browser localStorage / IndexedDB (browser-tab biomes)
- `src/substrate/postgres.py` — Postgres JSONB adapter (matching current bsp-mcp commons shape)
- `src/substrate/well_known.py` — HTTP / `.well-known/pscale-beach` adapter (federated peers)
- `src/substrate/adapter_protocol.md` — the interface spec each adapter must implement

Each adapter implements:
- `load_block(name) -> dict | None`
- `save_block(name, dict, version_token=None) -> token | conflict`
- `lock_state(name) -> {locked: bool, owner: str?}`
- `verify_secret(name, secret) -> bool`
- Per-substrate routing rules (e.g., `sed:<collective>` for sedimentary collectives)

**Acceptance test:** the same zand call works against all four adapters (read/write a position; verify content) without changing zand's signature.

## Phase 5 — MCP transport

**Estimated effort:** 1-2 sessions.

Re-author the bsp-mcp server scaffolding for ztone. The piece deliberately not vendored when the biome was first set up.

Files to create:
- `src/mcp/server.ts` — MCP server exposing zand operations
- `src/mcp/tools/zand.ts` — tool definition (read + write)
- `src/mcp/tools/disc.ts`, `tools/spindle.ts`, etc. — optional per-shape tool surfaces

**Decision point:** expose the tool as `zand`, `bsp`, or both (bsp as compatibility shim during transition). Recommend `zand` for new clients; `bsp` as alias for current bsp-mcp callers.

**Acceptance test:** a client (Claude Desktop, or another MCP client) calls the MCP tool with a (block, number, attention) tuple and gets back the expected shape.

## Phase 6 — Biome unfolding

**Estimated effort:** 1-2 sessions.

Convert `biome.json` (already translated to ztone form at `src/sentinel/ztone/biome.json`) into the operational shell. The seven sentinel currents become zand-walkable. Sense-the-host logic reads configuration through zand.

Tasks:
- Make `src/sentinel/ztone/biome.json` the active shell (replace `src/sentinel/biome.json` as the reference)
- Wire `src/sentinel/biome.json` reflexive seed (branch 9) using `name:address:attention` references
- Implement sense-the-host (`src/sentinel/sense.py` or similar) that walks the biome shell via zand
- Boot procedure: read biome.json with zand, configure substrate adapter per host conditions, expose endpoints per current 3

**Acceptance test:** drop the biome onto a fresh host (laptop, VPS, thumbdrive), watch it unfold to fit conditions and serve zand operations.

## Phase 7 — xstream rewiring

**Estimated effort:** 3-5 sessions; the substantial integration.

Replace the underscore-bearing bsp calls in xstream with zand calls. Use Farey distance natively for the proximity filter. vapor/liquid/solid cycle's pscale arithmetic via zand.

Tasks:
- Refactor xstream's pscale layer to call zand instead of bsp
- Implement Farey distance between two pscale addresses (mathematical foundation: depth-in-unit-interval paper)
- Update vapor/liquid/solid handlers to use zand modes (point/ring/directory/disc) for their reads
- Re-wire CADO faces (player/author/designer) to operate via zand modifiers (when Phase 5 lands)

**Acceptance test:** the Mos Eisley cantina test — three players, one hour, synchronised imagination — works on the ztone stack.

## Phase 8 — Hermit-crab shell (mobius) on ztone

**Estimated effort:** 2-3 sessions.

When the canonical mobius surfaces from the separate drive, port it to zand. The reflexive block pattern uses sunztone:7-style address grafting. Concern-loop reads/writes state through zand.

Tasks:
- Get the canonical mobius from the user's separate drive
- Port to zand operations
- Implement the reflexive seed pattern using ztone references
- Boot test: mobius runs against a biome substrate and persists its state via zand writes

**Acceptance test:** an agent persists across instances by reading its reflexive block via zand, performing concerns, and writing the updated block back.

## Phase 9 — Federation

**Estimated effort:** 2-3 sessions.

Cross-biome reads via HTTP/MCP using `https://origin:address:attention` references. The `/.well-known/pscale-beach` endpoint serves zand operations. Block ecology by mutual reference becomes a real network across hosts.

Tasks:
- Wire URL-as-agent-id (per `docs/biome-design.md`)
- Implement the well-known endpoint serving zand
- Add cross-biome reference resolution (URL prefix routing in `block_loader`)
- Cycle detection for multi-level star across federation (since unbounded networks can have ref loops)

**Acceptance test:** two biomes on different hosts can read each other's blocks by URL using only the reference syntax.

## Phase 10 — Migration & launch

**Estimated effort:** variable.

Translate existing production blocks. Optional bilingual period (both bsp and zand operational against the same substrate during transition). Deprecate underscore form.

Since the biome project is pre-public, this is cleaner than it could have been — no users to migrate, just internal data.

Tasks:
- Audit production bsp-mcp and pscale-beach for blocks that need migration
- Run `migrate.py` on each
- Verify with the zand test suite
- Set deprecation date for underscore form

---

## What's still uncovered (each becomes a future battery)

Each of these is a real spec extension and should get its own test battery:

| Concern | Battery name | What it tests |
|---|---|---|
| Locks | `tezt-locks.json` | write-lock with passphrase; secret as proof; lock-state transitions |
| Gray encryption | `tezt-gray.json` | opt-in self-encryption with secret as key |
| Modifiers | `tezt-modifiers.json` | face (CADO) and tier (SMH) access filtering |
| Substrate dispatch | `tezt-substrate.json` | name-prefix routing (sed:, grain:, https://) |
| Cycles | `tezt-cycles.json` | star with A↔B reference loops; verify cycle detection or graceful failure |

Each battery follows the existing pattern: branch-per-test JSON with call + expected outcome; runner extends `BATTERIES` and the EXPECTED_MODE / EXPECTED_COUNT / MARKERS maps.

## How to pick up from here

A new CC session should read in this order:
1. `tezt-handoff/HANDOFF.md` — the federated test workflow
2. `docs/ztone-spec.md` — the consolidated spec overview
3. `docs/ztone-phased-plan.md` — this file
4. `src/sentinel/sunztone.json` and `whetztone.json` — the teaching blocks
5. `src/zand/zand.py` — the canonical implementation (or `zand.ts` for TS work)

The natural next phase is **Phase 4 (Substrate adapters)** — it makes zand actually deployable. Phase 5 (MCP transport) and Phase 6 (Biome unfolding) follow naturally.

Phases 7-10 are integration-heavy and depend on Phases 4-6 being stable. They can also be done in parallel by separate sessions if context permits.
