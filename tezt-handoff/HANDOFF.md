# ztone test handoff — federated zand workflow

This is a self-contained test package for **zand**, the pure-digit pscale primitive. Your task is to write your own implementation of `zand` from the two teaching blocks here, then verify it against the canonical battery of **69 tests across 8 batteries**.

**You may not look at any other zand implementation.** The two teaching blocks (`sunztone.json` and `whetztone.json`) are your only specification.

## Your task

1. Read `sunztone.json` — the teaching block (nine branches).
2. Read `whetztone.json` — the operational manual (six branches).
3. Write `zand.py` in this directory.
4. Run `python3 run-tezt.py`.
5. Iterate on failures until `=== Summary: 69/69 tests passed ===`.

## The eight batteries

| Battery | Tests | What it exercises |
|---|---:|---|
| `tezt-spatial.json` | 9 | Core shapes: whole, spindle (×4 depths), disc (×2 pscales), ring, directory — against a floor-3 spatial fixture |
| `tezt-canonical.json` | 9 | Address parsing: bare/dotted, pad-left, split-at-floor, trailing-zero preservation, canonical display form, terminus pscale arithmetic |
| `tezt-edge.json` | 9 | Error cases (multi-dot, non-digit, exceeds-floor) and boundary behaviour (off-spindle attentions, absent walks, integer input, empty address) |
| `tezt-sunztone.json` | 9 | Reflexive walks of sunztone itself — exercises whole, spindles at depths 1–4, disc, ring, directory, point |
| `tezt-star.json` | 9 | Reference resolution: bare name, `name:address`, `name:address:attention`. Includes controls (plain text, unresolvable) |
| `tezt-absorption.json` | 9 | Supernest invariance — the same dotted address resolves to the same content across floor 1, 2, 3 fixtures |
| `tezt-nesting.json` | 9 | Subnest preservation (string lifts to `{0: original, …}`) and supernest growth (block wraps under new outer level) |
| `tezt-reverse.json` | 6 | Inverse direction: given a content marker (the prompt), write the call that returns it |

## What `zand.py` must export

```python
def zand(block, number=None, attention=None, content=None,
         star=False, block_loader=None):
    ...
    return {"mode": ..., ...}
```

And an exception class:

```python
class InvalidAddressError(ValueError):
    ...
```

Six modes are used: `whole`, `spindle`, `point`, `ring`, `directory`, `disc`. Plus `error` (synthesised by the runner when InvalidAddressError is caught — your zand only needs to raise the exception).

Spindle entries and disc nodes carry a `status` field: `voiced`, `headless`, `absent`. The runner asserts on the status sequence for spindle tests — this verifies walk-with-empty (the walk never halts on missing structure).

## Fixtures included

| Fixture | What it is |
|---|---|
| `test-spatial-floor3.json` | Floor-3 spatial block — THORNKEEP, TAVERN, KITCHEN, HEARTH, BELLOWS, … |
| `sunztone.json` | The teaching block, also used as a fixture (floor 1) |
| `test-refs.json` | Block containing leaf references to `other` (used by star battery) |
| `other.json` | Target of references resolved by star (used by star battery) |
| `absorb-floor1/2/3.json` | Identical content at floors 1, 2, 3 (used by absorption battery) |
| `subnest-before/after.json` | Same block before and after a subnest operation |
| `super-before/after.json` | Same block before and after a supernest operation |

## Workflow

1. **Read sunztone first.** Especially branch 0 (top voicing), branch 2 (geometry), branch 3 (number / address — sub-branches 3,0 through 3,5; note 3,3,1 has standard-form worked examples), branch 4 (function signature in 4,0; shapes in 4,3).
2. **Read whetztone for operational specifics.** Branch 1 (signature), 2.3 (address pinning, floor padding), 3 (shape derivation — sub-branches per shape with worked examples).
3. **Write a draft `zand.py`.** Start with `floor_depth`, `parse_address`, `canonicalise`, then the walk loop, then the shape readers, then `zand` itself.
4. **Run `python3 run-tezt.py`.** Read FAIL lines.
5. **For each failure**, open the relevant tezt-X.json branch — branch.0 is the test description, branch.2 is the expected outcome. Compare to what your zand returned.
6. **Iterate.** When you see `69/69 tests passed`, you have a conforming zand at the contract level.

## What passing means

`69/69` means your `zand` matches the canonical zand on every test in all eight batteries — covering core shapes, address canonicalisation, error handling, reference resolution, supernest invariance, and structural growth (subnest/supernest preservation).

It does NOT cover writes (zand with `content=X`), locks, gray encryption, or modifiers (face/tier). Those will come in further batteries.

## Report back

After you complete (or get stuck), please report:

1. **Did you pass 69/69?** If not, which branches failed and what your `zand` returned.
2. **Was sunztone clear?** Specifically: which sections did you have to re-read, and which were genuinely ambiguous? Where did you have to guess?
3. **Was whetztone clear?** Same question.
4. **Which batteries were hardest to pass and why?**
5. **What would you add to sunztone or whetztone to make the next session smoother?** Sentences or worked examples that would have saved you time.
6. **How long did it take?** Wall-clock estimate from "open the package" to "69/69".

This is the federated experiment. If you can write conforming zand from just the two teaching blocks, the ztone specification is operational. If sunztone/whetztone have gaps, your failures and report tell us where to improve.

## Federated implication

Two independent sessions each passing 69/69 starting from sunztone+whetztone alone means their implementations are equivalent at the contract level — even though their code may differ entirely. That's what "federated bsp/zand" means in practice: same spec, many implementations, interchangeable as long as they pass.
