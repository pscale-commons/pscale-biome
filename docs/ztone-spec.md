# ztone — the pure-digit pscale primitive

> 🗄️ **Retired intermediary-era document (2026-05-28) — "ztone" terminology is retired.** This spec describes the z-era first pass (zand/sunztone/whetztone) at pure-digit pscale, **superseded** by the spark set (slate/flint/spark, `src/spark/`). Reference/history only — the live primitive spec is `docs/spark-spec.md` and the live teaching blocks are `src/spark/slate.json` + `src/spark/flint.json`. Current state: the memory `project_biome_shape.md`.

**Status:** read + write side complete. Three independent federated implementations have each passed the full test suite on first run (9/9, 69/69, 78/78), evidence the spec is operationally portable.

## What ztone is

The foundational primitive of the pscale ecology, rebased from underscore-bearing notation (where `_` was the voicing carrier outside the digit alphabet) to pure-digit form (where `0` plays that role).

A ztone block is JSON where every key is a single digit `"0"` through `"9"`. Digit `0` carries the voicing — the zero-position semantic that makes its sibling digits `1`-`9` cohere. There are no special characters; `0` is a digit like any other in JSON.

This rebases the geometry onto its proper mathematical home (Farey / Stern-Brocot tree — every digit is a mediant subdivision). It also removes the only ambiguity in the prior system: address parsing, function semantics, and composition rules all collapse to digit-only operations with one canonical decimal point as a floor anchor.

## The two teaching blocks

| Block | Branches | Role |
|---|---:|---|
| **sunztone.json** | 9 | The teaching block — geometry, number/address, function, voicing, growth, composition, substrate, design. Self-describing and walkable by the function it teaches. |
| **whetztone.json** | 6 | The operational manual — signature, address parsing, shape derivation (point/ring/directory/disc), write, star, substrate. Direct reference for implementers. |

Both blocks are pure-digit (floor 1). Together they are the complete spec — three sessions have written conforming `zand` implementations from these two files alone.

## The function (zand)

```python
zand(block, number=None, attention=None, content=None,
     star=False, block_loader=None) -> ResultDict
```

**Read modes** (when content is None):
| `number` | `attention` | Returns |
|---|---|---|
| None | None | `{mode: "whole", block, floor}` |
| None | int | `{mode: "disc", pscale, nodes: [...]}` — all positions at that depth |
| str | None | `{mode: "spindle", address, floor, entries: [...]}` — chain from root |
| str | == terminus | `{mode: "point", pscale, text, status}` |
| str | > terminus | `{mode: "ring", pscale, siblings: [...]}` |
| str | < terminus | `{mode: "directory", subtree}` |

**Write modes** (when content provided):
| Call | Returns |
|---|---|
| `(number, attention=terminus, content=str)` | `{mode: "point-write", ok, address}` — sets leaf |
| `(number, attention > terminus, content=dict)` | `{mode: "ring-write", ok}` — replaces digit children at attention-depth parent |
| `(number, attention < terminus, content=dict)` | `{mode: "directory-write", ok}` — replaces subtree |
| `(None, None, content=dict)` | `{mode: "whole-write", ok}` — clears block, installs content (in place) |

**Star** (`star=True`): leaf strings matching `name`, `name:address`, or `name:address:attention` are resolved by recursive zand calls via `block_loader`. Star propagates through the recursive call so multi-level chains (A→B→C) resolve in a single outer call.

**Spindle entries** carry status: `voiced` / `headless` / `absent` — walk-with-empty: the walker never halts on missing structure.

## Address grammar

```
address := bare | dotted
bare    := digit+
dotted  := digit+ '.' digit*
```

Plus an empty form (`""`) representing root with no walk. Multi-dot forms (`1.2.3`) are forbidden. Floor-aware pinning: every address resolves against the block's floor (the depth at which the root zero-spine first terminates in a string). Dotted addresses padded left with zeros if shorter than floor (preserves semantic position across supernesting); bare addresses split at floor boundary if longer.

```
reference grammar (parsed inside leaf strings when star=True):
  name      := letter (letter | digit | '_' | '-')*
  namespace := name (':' name)*
  address   := digit+ ('.' digit+)?
  attention := '-'? digit+
  reference := namespace (':' address (':' attention)?)?
```

## Implementation status

| Component | File | Status |
|---|---|---|
| Canonical Python | `src/zand/zand.py` | 37 unit tests passing |
| TypeScript port | `src/zand/zand.ts` | Strict-mode clean; CLI wrapper at zand-cli.ts |
| Python ↔ TS parity | `src/zand/tezt/parity-test.py` | 81/81 match |
| Test suite | `src/zand/tezt/` | 10 batteries, 81 tests |
| Migration tool | `src/zand/migrate.py` | `_` → `0` key translation |
| Sentinel ztone-form | `src/sentinel/ztone/` | 7 blocks translated (agent-id, block-conventions, evolution, gatekeeper, manifest, progression, biome) |
| Federated handoff | `tezt-handoff/` | Self-contained package for fresh-session validation |

## Test suite

| Battery | Tests | Coverage |
|---|---:|---|
| spatial | 9 | Core shapes against floor-3 spatial fixture |
| canonical | 9 | Address parsing: bare/dotted, pad-left, split-at-floor, trailing zeros preserved |
| edge | 9 | Errors + boundaries (multi-dot, non-digit, exceeds-floor, off-spindle, absent) |
| sunztone | 9 | Reflexive walks against the teaching block itself |
| star | 9 | Reference resolution: name, name:address, name:address:attention |
| absorption | 9 | Supernest invariance — same dotted address, same content, floors 1/2/3 |
| nesting | 9 | Subnest preservation (lift) + supernest preservation |
| reverse | 6 | Given a content marker, write the call |
| writes | 9 | Write side: point/ring/directory/whole + lift-on-deep-write |
| star-deep | 3 | Multi-level star (A→B→C chain) — propagation through nested zand calls |
| **Total** | **81** | |

## The federated workflow

A fresh CC session given just `sunztone.json` + `whetztone.json` (the two teaching blocks) + the test battery package can:

1. Read the two teaching blocks
2. Write its own `zand.py` (~400-500 lines Python from scratch)
3. Run `python3 run-tezt.py`
4. Iterate on failures until 78/78

**Three independent sessions** have each completed this loop on first run, in 30-40 minutes wall-clock. The spec is operationally portable — multiple implementations are interchangeable as long as they pass the suite. This is what "federated bsp" means in practice.

The handoff package at `tezt-handoff/` (also `~/Downloads/tezt-handoff/`) is the ready-to-send artifact.

## What's covered

- Read side: all six shapes (whole, spindle, point, ring, directory, disc)
- Write side: point/ring/directory/whole + lift-on-deep-write + auto-create headless intermediates
- Address parsing: bare, dotted, padding, splitting, canonical display form
- Error handling: multi-dot rejection, non-digit rejection, exceeds-floor rejection
- Reference resolution: single-level and multi-level chains (A→B→C)
- Supernest invariance: dotted addresses survive growth
- Subnest preservation: lift behavior preserves voicing

## What's NOT covered (next layer)

| Concern | What it adds |
|---|---|
| **Locks** | write-lock with passphrase; secret as proof-of-authority |
| **Gray encryption** | opt-in self-encrypted leaves (visible structure, private content) |
| **Modifiers** | face (CADO: Character/Author/Designer/Observer); tier (SMH: Soft/Medium/Hard) |
| **Substrate adapters** | filesystem, localStorage, Postgres, HTTP/`.well-known/pscale-beach` |
| **MCP transport** | JSON-RPC envelope exposing zand operations over MCP |
| **Cross-block dispatch** | substrate routing by name prefix (sed:, grain:, https://) |
| **Cycle detection** | currently relies on agent-level handling for A↔B reference loops |

See `docs/ztone-phased-plan.md` for the phased build-out of these.
