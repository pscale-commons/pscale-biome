#!/usr/bin/env python3
"""
test_zand.py — exercises the core invariants of zand.py.

Run: python3 test_zand.py

No pytest dependency. Each test is a function whose name starts with
'test_'; failures raise AssertionError with a helpful message.
"""
import json
import sys
import traceback

from zand import (
    InvalidAddressError,
    canonicalise,
    collect_zero_text,
    floor_depth,
    format_address,
    parse_reference,
    walk_block,
    zand,
)


# ============================================================================
# Sample blocks
# ============================================================================

def make_floor1_block():
    return {
        "0": "root voicing",
        "1": "branch one",
        "2": {
            "0": "branch two voicing",
            "3": "two-three leaf",
        },
        "5": {  # headless branch (no '0' key)
            "1": "five-one leaf",
        },
    }


def make_floor2_block():
    return {
        "0": {
            "0": "floor-2 root voicing",
            "1": "above-floor-one voicing",
        },
        "1": "top-level one (pscale 1)",
        "2": {
            "0": "top-level two voicing (pscale 1)",
            "5": "deep leaf at 2.5 (pscale -1)",
        },
    }


# ============================================================================
# Floor discovery
# ============================================================================

def test_floor_1():
    assert floor_depth(make_floor1_block()) == 1


def test_floor_2():
    assert floor_depth(make_floor2_block()) == 2


def test_floor_0_when_no_zero():
    assert floor_depth({"1": "no zero key"}) == 0


def test_floor_3_deep_zero_spine():
    block = {"0": {"0": {"0": "deep voicing"}}}
    assert floor_depth(block) == 3


# ============================================================================
# Address canonicalisation
# ============================================================================

def test_dotted_at_floor_passes_through():
    digits, canon = canonicalise("30.5", 2)
    assert digits == ["3", "0", "5"]
    assert canon == "30.5"


def test_bare_pins_to_floor_2():
    digits, canon = canonicalise("305", 2)
    assert digits == ["3", "0", "5"]
    assert canon == "30.5"


def test_bare_pins_to_floor_1():
    digits, canon = canonicalise("305", 1)
    assert digits == ["3", "0", "5"]
    assert canon == "3.05"


def test_bare_pins_to_floor_when_short():
    # Bare '3' on floor 2 — implicit decimal at floor, pad-left to floor.
    digits, canon = canonicalise("3", 2)
    assert digits == ["0", "3"]
    # Canonical display strips leading zeros above the floor.
    assert canon == "3"
    # Dotted '3.' gives the same walk under the floor-pinning rule.
    digits_dotted, _ = canonicalise("3.", 2)
    assert digits_dotted == ["0", "3"]


def test_bare_splits_at_floor_when_longer():
    # Bare '305' on floor 2 — implicit decimal at floor 2 → '30.5'.
    digits, canon = canonicalise("305", 2)
    assert digits == ["3", "0", "5"]
    assert canon == "30.5"
    # On floor 1, same input → '3.05'
    digits1, canon1 = canonicalise("305", 1)
    assert digits1 == ["3", "0", "5"]
    assert canon1 == "3.05"


def test_dotted_pads_left_under_supernesting():
    # '30.5' read against floor 3 (after one supernesting)
    digits, canon = canonicalise("30.5", 3)
    assert digits == ["0", "3", "0", "5"]
    # The semantic terminus is still pscale -1 (3 - 4 = -1)
    assert (3 - len(digits)) == -1


def test_dotted_rejects_left_exceeding_floor():
    try:
        canonicalise("305.5", 2)
    except InvalidAddressError:
        return
    raise AssertionError("expected InvalidAddressError for left > floor")


def test_multi_decimal_rejected():
    try:
        canonicalise("1.2.3", 1)
    except InvalidAddressError:
        return
    raise AssertionError("expected InvalidAddressError for multi-decimal")


def test_non_digit_rejected():
    try:
        canonicalise("1a2", 1)
    except InvalidAddressError:
        return
    raise AssertionError("expected InvalidAddressError for non-digit")


# ============================================================================
# Walk-with-empty semantics
# ============================================================================

def test_walk_voiced_path():
    block = make_floor1_block()
    digits, _ = canonicalise("2.3", 1)
    chain, terminal, _, _ = walk_block(block, digits, 1)
    assert len(chain) == 3, f"expected 3 entries, got {len(chain)}"
    assert chain[0]["status"] == "voiced"
    assert chain[0]["text"] == "root voicing"
    assert chain[1]["status"] == "voiced"
    assert chain[1]["text"] == "branch two voicing"
    assert chain[2]["status"] == "voiced"
    assert chain[2]["text"] == "two-three leaf"


def test_walk_absent_when_overshooting_string_leaf():
    # Address 1.234 — but 1 is a leaf string, so 2/3/4 don't exist
    block = make_floor1_block()
    digits, _ = canonicalise("1.234", 1)
    assert len(digits) == 4
    chain, terminal, _, _ = walk_block(block, digits, 1)
    assert len(chain) == 5
    assert chain[0]["status"] == "voiced"  # root
    assert chain[1]["status"] == "voiced"  # branch one
    assert chain[2]["status"] == "absent"
    assert chain[3]["status"] == "absent"
    assert chain[4]["status"] == "absent"
    # All absent entries have pscale matching their depth
    assert chain[4]["pscale"] == -3
    assert terminal is None


def test_walk_into_headless_node():
    # Position 5 is an object with no '0' key
    block = make_floor1_block()
    digits, _ = canonicalise("5", 1)
    chain, terminal, _, _ = walk_block(block, digits, 1)
    assert chain[1]["status"] == "headless"
    assert chain[1]["text"] is None
    assert isinstance(terminal, dict)


def test_walk_through_headless_to_voiced():
    block = make_floor1_block()
    digits, _ = canonicalise("5.1", 1)
    chain, terminal, _, _ = walk_block(block, digits, 1)
    assert chain[1]["status"] == "headless"
    assert chain[2]["status"] == "voiced"
    assert chain[2]["text"] == "five-one leaf"


def test_walk_pscale_matches_address():
    # The terminus pscale equals floor - len(digits), always
    block = make_floor1_block()
    for addr in ["1", "2.3", "5.1", "1.234", "1.99999"]:
        digits, _ = canonicalise(addr, 1)
        chain, _, _, _ = walk_block(block, digits, 1)
        assert chain[-1]["pscale"] == 1 - len(digits), \
            f"mismatch for {addr}: {chain[-1]['pscale']} vs {1 - len(digits)}"


# ============================================================================
# Read shapes
# ============================================================================

def test_spindle_default_when_only_number():
    block = make_floor1_block()
    result = zand(block, "2.3")
    assert result["mode"] == "spindle"
    assert result["floor"] == 1
    assert len(result["entries"]) == 3


def test_point_when_attention_at_terminus():
    block = make_floor1_block()
    # 2.3 → terminus pscale = 1 - 2 = -1
    result = zand(block, "2.3", attention=-1)
    assert result["mode"] == "point"
    assert result["pscale"] == -1
    assert result["text"] == "two-three leaf"
    assert result["status"] == "voiced"


def test_point_at_absent_position():
    block = make_floor1_block()
    result = zand(block, "1.234", attention=-3)
    assert result["mode"] == "point"
    assert result["status"] == "absent"
    assert result["text"] is None


def test_ring_when_attention_shallower():
    block = make_floor1_block()
    # Walk '2.3' (terminus pscale -1); attention 0 → ring at depth 1
    # (root's children at the floor).
    result = zand(block, "2.3", attention=0)
    assert result["mode"] == "ring"
    assert result["pscale"] == 0
    digit_set = {s["digit"] for s in result["siblings"]}
    # Root's digit children: '0', '1', '2', '5'
    assert digit_set == {"0", "1", "2", "5"}, f"got {digit_set}"
    walked = [s for s in result["siblings"] if s["is_walked"]]
    assert len(walked) == 1
    assert walked[0]["digit"] == "2"  # spindle went through '2' at this level


def test_ring_includes_headless_sibling():
    block = make_floor1_block()
    # Walk '2.3' (terminus -1); attention 0 → ring at root's children.
    # Position '5' is headless in this block.
    result = zand(block, "2.3", attention=0)
    digits_seen = {s["digit"]: s for s in result["siblings"]}
    assert digits_seen["5"]["status"] == "headless"
    assert digits_seen["1"]["status"] == "voiced"


def test_directory_when_attention_deeper():
    block = make_floor1_block()
    # Address '2' → terminus pscale 0; attention -1 = directory to depth 2
    result = zand(block, "2", attention=-1)
    assert result["mode"] == "directory"
    assert isinstance(result["subtree"], dict)
    assert result["subtree"]["0"] == "branch two voicing"
    assert result["subtree"]["3"] == "two-three leaf"


def test_disc_all_positions_at_pscale():
    block = make_floor1_block()
    result = zand(block, number=None, attention=0)
    assert result["mode"] == "disc"
    assert result["pscale"] == 0
    addrs = {n["address"]: n for n in result["nodes"]}
    # On floor 1, positions at depth 1 are '0', '1', '2', '5'
    assert "1" in addrs
    assert "2" in addrs
    assert "5" in addrs
    # '5' shows as headless
    assert addrs["5"]["status"] == "headless"


# ============================================================================
# Star reference following
# ============================================================================

def test_parse_reference_simple():
    assert parse_reference("other") == ("other", None, None)
    assert parse_reference("other:1") == ("other", "1", None)
    assert parse_reference("sed:commons") == ("sed:commons", None, None)
    assert parse_reference("sed:commons:13") == ("sed:commons", "13", None)


def test_parse_reference_with_address():
    assert parse_reference("block-name:30.5") == ("block-name", "30.5", None)


def test_parse_reference_with_attention():
    # Three-part references: name:address:attention
    assert parse_reference("other:5:0") == ("other", "5", 0)
    assert parse_reference("other:5.1:-3") == ("other", "5.1", -3)
    assert parse_reference("sed:commons:13:1") == ("sed:commons", "13", 1)


def test_parse_reference_rejects_non_reference():
    assert parse_reference("this is just text") is None
    assert parse_reference("") is None
    assert parse_reference("123") is None  # starts with digit


def test_star_resolves_reference_default_to_spindle():
    """With no attention in the reference, resolution defaults to spindle
    (matches zand's own default for 'address only, no attention')."""
    other = {"0": "other root", "1": "other one"}

    def loader(name):
        return {"other": other}.get(name)

    block = {"0": "container", "1": "other:1"}
    result = zand(block, "1", attention=0,
                  star=True, block_loader=loader)
    assert result["mode"] == "point"
    # Resolved into a spindle (no attention given in reference)
    assert isinstance(result["text"], dict)
    assert result["text"]["mode"] == "spindle"
    # Spindle should have entries down to depth 1 with 'other one'
    entries = result["text"]["entries"]
    assert entries[1]["text"] == "other one"


def test_star_resolves_reference_with_attention():
    """When the reference carries an attention, the shape derives normally."""
    other = {"0": "other root", "1": {"0": "branch one", "5": "deep"}}

    def loader(name):
        return {"other": other}.get(name)

    # Reference 'other:1:0' — address '1' (terminus pscale 0), attention 0 = point
    block = {"0": "container", "1": "other:1:0"}
    result = zand(block, "1", attention=0,
                  star=True, block_loader=loader)
    assert result["mode"] == "point"
    assert isinstance(result["text"], dict)
    assert result["text"]["mode"] == "point"
    assert result["text"]["text"] == "branch one"

    # Reference 'other:1:-1' — directory from '1' down to depth 2
    block2 = {"0": "container", "1": "other:1:-1"}
    result2 = zand(block2, "1", attention=0,
                   star=True, block_loader=loader)
    assert result2["mode"] == "point"
    assert isinstance(result2["text"], dict)
    assert result2["text"]["mode"] == "directory"


def test_star_resolves_bare_blockname_to_whole():
    """Bare reference (no address) resolves to the whole target block."""
    other = {"0": "other root", "1": "other one"}

    def loader(name):
        return {"other": other}.get(name)

    block = {"0": "container", "1": "other"}
    result = zand(block, "1", attention=0,
                  star=True, block_loader=loader)
    assert result["mode"] == "point"
    assert isinstance(result["text"], dict)
    assert result["text"]["mode"] == "whole"


def test_star_passes_through_non_reference():
    block = {"0": "container", "1": "just plain text"}
    result = zand(block, "1", attention=0,
                  star=True, block_loader=lambda n: None)
    assert result["mode"] == "point"
    assert result["text"] == "just plain text"


# ============================================================================
# Write
# ============================================================================

def test_point_write_replaces_leaf():
    block = {"0": "root", "1": "old"}
    result = zand(block, "1", attention=0, content="new")
    assert result.get("ok")
    assert block["1"] == "new"


def test_deep_write_creates_headless_intermediates():
    """The keystone test for the user's authoring model.

    Writing 'deep' at address 1.234 against {0: root, 1: 'branch one'} should:
    - Preserve 'branch one' as the new object-at-1's '0' voicing
    - Create 2 and 3 as headless intermediates
    - Place 'deep' at the terminus
    """
    block = {"0": "root", "1": "branch one"}
    zand(block, "1.234", attention=-3, content="deep")

    # Structural assertions
    assert isinstance(block["1"], dict)
    assert block["1"]["0"] == "branch one"  # original voicing preserved
    assert isinstance(block["1"]["2"], dict)
    assert "0" not in block["1"]["2"]       # intermediate is headless
    assert isinstance(block["1"]["2"]["3"], dict)
    assert "0" not in block["1"]["2"]["3"]  # intermediate is headless
    assert block["1"]["2"]["3"]["4"] == "deep"

    # Re-read 1 — still gives "branch one" via zero-text collection
    result = zand(block, "1")
    assert result["entries"][1]["text"] == "branch one"
    assert result["entries"][1]["status"] == "voiced"

    # Re-read 1.234 — chain has voiced, voiced, headless, headless, voiced
    result = zand(block, "1.234")
    statuses = [e["status"] for e in result["entries"]]
    assert statuses == ["voiced", "voiced", "headless", "headless", "voiced"]
    assert result["entries"][4]["text"] == "deep"


def test_directory_write_replaces_subtree():
    block = {"0": "root", "1": "old leaf"}
    zand(block, "1", attention=-2, content={"0": "new voice", "5": "new sib"})
    assert isinstance(block["1"], dict)
    assert block["1"]["0"] == "new voice"
    assert block["1"]["5"] == "new sib"


# ============================================================================
# Voicing-aware ring reads (the S*T*I hidden-directory property)
# ============================================================================

def test_ring_does_not_expose_zero_subtree():
    """The S*T*I-equivalent property: ring reads return only zero-text from
    object siblings, never their underlying digit children. The 0,1 and 0,2
    positions are NOT enumerated alongside top-level 1, 2, ..., 9.

    Block setup: floor-2 block where block['0'] is a branch (object with
    deeper voicing) and carries 'hidden' siblings at 0,1 and 0,2.
    """
    block = {
        "0": {                            # branch — has deeper voicing
            "0": "floor-2 voicing",
            "1": "hidden at 0,1",         # must NOT appear in root's ring
            "2": "hidden at 0,2",
        },
        "1": "top-level 1",
        "2": "top-level 2",
    }
    # Walk bare '12' = [1, 2] on floor 2 → terminus depth 2, pscale 0.
    # Attention 1 (pscale 1 = root's children level) → ring at depth 1
    # with parent = root.
    result = zand(block, "12", attention=1)
    assert result["mode"] == "ring", f"got {result['mode']}"
    assert result["pscale"] == 1
    digit_set = {s["digit"] for s in result["siblings"]}
    # Should be exactly {0, 1, 2} — root's digit children only.
    # 'hidden at 0,1' and 'hidden at 0,2' are NOT in this enumeration.
    assert digit_set == {"0", "1", "2"}, f"got {digit_set}"
    zero_sib = next(s for s in result["siblings"] if s["digit"] == "0")
    assert zero_sib["is_branch"] is True
    assert zero_sib["text"] == "floor-2 voicing"
    # Verify no leakage: no sibling's text mentions 'hidden'
    for s in result["siblings"]:
        assert s["text"] is None or "hidden" not in s["text"], \
            f"hidden content leaked into ring: {s}"


# ============================================================================
# Test runner
# ============================================================================

def run_all():
    tests = [
        (name, fn) for name, fn in globals().items()
        if name.startswith("test_") and callable(fn)
    ]
    passed = 0
    failed = 0
    failures = []
    for name, fn in tests:
        try:
            fn()
            print(f"  ok   {name}")
            passed += 1
        except Exception as e:
            print(f"  FAIL {name}: {e}")
            failures.append((name, traceback.format_exc()))
            failed += 1
    print(f"\n{passed} passed, {failed} failed of {len(tests)} tests")
    if failures:
        print("\n--- Failure details ---")
        for name, tb in failures:
            print(f"\n{name}:\n{tb}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run_all())
