#!/usr/bin/env python3
"""run-tezt.py — drive ztone test batteries through zand and report.

Counterpart to run-bsp-tests.py for the ztone/zand pair. Imports zand
directly (no subprocess) and asserts against zand's mode/text/status
field vocabulary.

Usage:
    cd src/zand/tezt && python3 run-tezt.py

Add new batteries by extending BATTERIES, EXPECTED_MODE, EXPECTED_COUNT,
and MARKERS below.
"""
import ast
import copy
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Make zand importable (it sits one directory up)
sys.path.insert(0, HERE)
try:
    from zand import zand, InvalidAddressError
except ImportError as e:
    print(f"Error: cannot import zand from {HERE}: {e}")
    print(f"Write zand.py in this directory first (the fresh sessions task).")
    sys.exit(1)


BATTERIES = [
    # (tezt_file, fixture_file, label)
    ("tezt-spatial.json", "test-spatial-floor3.json", "spatial"),
    ("tezt-canonical.json", "test-spatial-floor3.json", "canonical"),
    ("tezt-edge.json", "test-spatial-floor3.json", "edge"),
    ("tezt-sunztone.json", "sunztone.json", "sunztone"),
    ("tezt-star.json", "test-refs.json", "star"),
    ("tezt-absorption.json", "absorb-floor1.json", "absorption"),
    ("tezt-nesting.json", "subnest-before.json", "nesting"),
    ("tezt-reverse.json", "test-spatial-floor3.json", "reverse"),
    ("tezt-writes.json", "writes-base.json", "writes"),
]


# Per-branch fixture overrides — for batteries that span multiple fixtures.
FIXTURE_OVERRIDE = {
    "absorption": {
        "1": "absorb-floor1.json", "2": "absorb-floor2.json", "3": "absorb-floor3.json",
        "4": "absorb-floor1.json", "5": "absorb-floor2.json", "6": "absorb-floor3.json",
        "7": "absorb-floor1.json", "8": "absorb-floor2.json", "9": "absorb-floor3.json",
    },
    "nesting": {
        "1": "subnest-before.json", "2": "subnest-after.json",
        "3": "subnest-after.json", "4": "subnest-after.json",
        "5": "super-before.json", "6": "super-after.json",
        "7": "super-before.json", "8": "super-after.json",
        "9": "subnest-after.json",
    },
    "reverse": {
        "1": "test-spatial-floor3.json",
        "2": "test-spatial-floor3.json",
        "3": "test-spatial-floor3.json",
        "4": "absorb-floor2.json",
        "5": "sunztone.json",
        "6": "sunztone.json",
    },
}


def block_loader(name):
    """Generic loader: look for <name>.json in HERE; return None if absent."""
    path = os.path.join(HERE, f"{name}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


EXPECTED_MODE = {
    "spatial": {
        "1": "whole",
        "2": "spindle",
        "3": "spindle",
        "4": "spindle",
        "5": "spindle",
        "6": "disc",
        "7": "disc",
        "8": "ring",
        "9": "directory",
    },
    "canonical": {
        "1": "spindle", "2": "spindle", "3": "spindle",
        "4": "spindle", "5": "spindle", "6": "spindle",
        "7": "spindle", "8": "spindle", "9": "spindle",
    },
    "edge": {
        "1": "error", "2": "error", "3": "error", "4": "error",
        "5": "spindle", "6": "disc", "7": "ring",
        "8": "spindle", "9": "spindle",
    },
    "sunztone": {
        "1": "whole",
        "2": "spindle", "3": "spindle", "4": "spindle", "5": "spindle",
        "6": "disc", "7": "ring",
        "8": "directory", "9": "point",
    },
    "star": {
        "1": "point", "2": "point", "3": "point", "4": "point",
        "5": "point", "6": "point", "7": "point", "8": "point",
        "9": "point",
    },
    "absorption": {
        "1": "spindle", "2": "spindle", "3": "spindle",
        "4": "spindle", "5": "spindle", "6": "spindle",
        "7": "disc", "8": "disc", "9": "disc",
    },
    "nesting": {
        "1": "spindle", "2": "spindle", "3": "spindle", "4": "spindle",
        "5": "spindle", "6": "spindle",
        "7": "disc", "8": "disc", "9": "disc",
    },
    "reverse": {
        "1": "spindle", "2": "spindle", "3": "spindle",
        "4": "spindle", "5": "spindle", "6": "disc",
    },
    "writes": {
        # Mode of the write call (not the verify-read)
        "1": "point-write", "2": "point-write", "3": "point-write",
        "4": "point-write", "5": "directory-write", "6": "ring-write",
        "7": "point-write", "8": "point-write", "9": "whole-write",
    },
}


EXPECTED_COUNT = {
    # None means no count assertion (e.g., whole, directory)
    "spatial": {
        "1": None,
        "2": 4,
        "3": 4,
        "4": 5,
        "5": 7,
        "6": 9,
        "7": 3,
        "8": 3,
        "9": None,
    },
    "canonical": {
        "1": 4, "2": 4, "3": 5, "4": 5, "5": 5,
        "6": 4, "7": 5, "8": 6, "9": 5,
    },
    "edge": {
        "1": None, "2": None, "3": None, "4": None,
        "5": 4, "6": 0, "7": 0, "8": 4, "9": 1,
    },
    "sunztone": {
        "1": None,
        "2": 2, "3": 3, "4": 4, "5": 5,
        "6": 10, "7": 10,
        "8": None, "9": None,
    },
    "absorption": {
        # Spindles: same terminus pscale on each floor; entry counts grow with floor.
        "1": 2, "2": 3, "3": 4,        # '1.' walk lengths: 1, 2, 3 (+1 for root)
        "4": 3, "5": 4, "6": 5,        # '9.1' walk lengths: 2, 3, 4
        "7": 4, "8": 4, "9": 4,        # disc at floor: 4 positions on each
    },
    "nesting": {
        "1": 2, "2": 2, "3": 3, "4": 2,
        "5": 2, "6": 3,
        "7": 3, "8": 3, "9": 3,
    },
}


# Canonical display address — verifies format_address output
EXPECTED_ADDRESS = {
    "canonical": {
        "1": "305", "2": "8", "3": "123.4", "4": "123.4", "5": "12.3",
        "6": "100", "7": "100.0", "8": "123.40", "9": "2.3",
    },
}


# Terminus pscale = floor − walk_length, computed per test
EXPECTED_TERMINUS_PSCALE = {
    "canonical": {
        "1": 0, "2": 0, "3": -1, "4": -1, "5": -1,
        "6": 0, "7": -1, "8": -2, "9": -1,
    },
}


MARKERS = {
    "spatial": {
        "1": ["THORNKEEP", "TAVERN", "KITCHEN", "HEARTH", "BELLOWS",
              "POT-HOOK", "IRON CHAIN", "FLOOR TERMINUS",
              "AT-FLOOR-VIA-ZERO-SPINE", "LAMP ROOM", "FISHMONGER",
              "MARKET", "LIGHTHOUSE", "HEADLAND", "COMMON ROOM",
              "ASH PIT", "STOVE"],
        "2": ["THORNKEEP", "FLOOR TERMINUS"],
        "3": ["THORNKEEP", "TAVERN", "KITCHEN", "FLOOR TERMINUS"],
        "4": ["THORNKEEP", "TAVERN", "KITCHEN", "HEARTH", "FLOOR TERMINUS"],
        "5": ["THORNKEEP", "TAVERN", "KITCHEN", "HEARTH",
              "POT-HOOK", "IRON CHAIN", "FLOOR TERMINUS"],
        "6": ["FLOOR TERMINUS", "AT-FLOOR-VIA-ZERO-SPINE", "TAVERN",
              "KITCHEN", "COMMON ROOM", "MARKET", "FISHMONGER",
              "LIGHTHOUSE", "LAMP ROOM"],
        "7": ["KITCHEN", "HEARTH", "STOVE"],
        "8": ["THORNKEEP", "TAVERN", "MARKET"],
        "9": ["KITCHEN", "HEARTH", "BELLOWS", "ASH PIT", "POT-HOOK", "STOVE"],
    },
    "canonical": {
        "1": ["HEADLAND"],
        "2": ["AT-FLOOR-VIA-ZERO-SPINE", "FLOOR TERMINUS"],
        "3": ["THORNKEEP", "TAVERN", "KITCHEN", "HEARTH"],
        "4": ["THORNKEEP", "TAVERN", "KITCHEN", "HEARTH"],
        "5": ["FLOOR TERMINUS"],
        "6": ["THORNKEEP", "FLOOR TERMINUS"],
        "7": ["THORNKEEP", "FLOOR TERMINUS"],
        "8": ["THORNKEEP", "TAVERN", "KITCHEN", "HEARTH"],
        "9": ["FLOOR TERMINUS"],
    },
    "edge": {
        # Error messages — markers are substrings of the exception text
        "1": ["decimal"],
        "2": ["non-digit"],
        "3": ["non-digit"],
        "4": ["floor"],
        # Non-error tests: content markers from the result
        "5": ["FLOOR TERMINUS"],
        "6": [],
        "7": [],
        "8": ["THORNKEEP"],
        "9": ["FLOOR TERMINUS"],
    },
    "sunztone": {
        "1": ["Sunztone", "Presence", "Geometry", "Number", "Function",
              "Voicing", "Growth", "Composition", "Substrate", "Design"],
        "2": ["Function", "ZAND"],
        "3": ["0+ deductive"],
        "4": ["Standard-form reading"],
        "5": ["Worked example", "100", "floor-3"],
        "6": ["Sunztone", "Presence", "Geometry", "Number", "Function",
              "Voicing", "Growth", "Composition", "Substrate", "Design"],
        "7": ["Sunztone", "Function", "Voicing"],
        "8": ["Number", "decimal", "floor", "Address forms",
              "Walk-with-empty", "Validation"],
        "9": ["0+ deductive"],
    },
    "star": {
        "1": ["other"],
        "2": ["OTHER ROOT", "first leaf of other", "second branch voicing"],
        "3": ["first leaf of other"],
        "4": ["first leaf of other"],
        "5": ["second branch voicing of other"],
        "6": ["second branch voicing of other", "deep leaf at other:2,3"],
        "7": ["just plain text"],
        "8": ["nonexistent:1"],
        "9": ["just plain text"],
    },
    "absorption": {
        "1": ["POSITION ONE"],
        "2": ["POSITION ONE"],
        "3": ["POSITION ONE"],
        "4": ["POSITION NINE-ONE"],
        "5": ["POSITION NINE-ONE"],
        "6": ["POSITION NINE-ONE"],
        "7": ["POSITION ONE", "POSITION FIVE", "POSITION NINE"],
        "8": ["POSITION ONE", "POSITION FIVE", "POSITION NINE"],
        "9": ["POSITION ONE", "POSITION FIVE", "POSITION NINE"],
    },
    "nesting": {
        "1": ["branch one leaf"],
        "2": ["branch one leaf"],
        "3": ["new content at 1,3"],
        "4": ["branch five leaf"],
        "5": ["POSITION ONE"],
        "6": ["POSITION ONE"],
        "7": ["root voicing", "POSITION ONE", "POSITION FIVE"],
        "8": ["root voicing", "POSITION ONE", "POSITION FIVE"],
        "9": ["root voicing", "branch one leaf", "branch five leaf"],
    },
    "reverse": {
        "1": ["KITCHEN"],
        "2": ["HEARTH"],
        "3": ["IRON CHAIN", "POT-HOOK"],
        "4": ["POSITION ONE"],
        "5": ["Standard-form reading"],
        "6": ["Sunztone", "Presence", "Geometry", "Number", "Function",
              "Voicing", "Growth", "Composition", "Substrate", "Design"],
    },
    # Writes markers apply to the VERIFY-READ result (branch.3 call output)
    "writes": {
        "1": ["updated"],
        "2": ["deep"],
        "3": ["verydeep"],
        "4": ["new5"],
        "5": ["new leaf at 3,4"],
        "6": ["ring sib 1"],
        "7": ["leaf at 5"],
        "8": ["roundtrip"],
        "9": ["new leaf one"],
    },
}


# Expected status sequences for spindles — verifies walk-with-empty
EXPECTED_STATUSES = {
    "spatial": {
        "2": ["voiced", "voiced", "voiced", "absent"],
        "3": ["voiced", "voiced", "voiced", "voiced"],
        "4": ["voiced", "voiced", "voiced", "voiced", "voiced"],
        "5": ["voiced", "voiced", "voiced", "voiced", "voiced", "voiced", "voiced"],
    },
}


def parse_call(call_str):
    """Extract number, attention, and star from a call.

    Handles number forms: 'X', X (int), '' (empty)
    Detects star=True (case-insensitive).
    """
    number = None
    attention = None
    star = False
    m = re.search(r"number=(?:['\"]([^'\"]*)['\"]|([^,)\s]+))", call_str)
    if m:
        number = m.group(1) if m.group(1) is not None else m.group(2)
    m = re.search(r"attention=(-?\d+)", call_str)
    if m:
        attention = int(m.group(1))
    if re.search(r"star=(True|true)", call_str):
        star = True
    return number, attention, star


def parse_content(call_str):
    """Extract content= from a write call. Supports quoted strings, flat
    dicts, lists (via ast.literal_eval). Returns None if no content."""
    m = re.search(r"content=(\{[^}]*\}|\[[^]]*\])", call_str)
    if m:
        try:
            return ast.literal_eval(m.group(1))
        except (ValueError, SyntaxError):
            return None
    m = re.search(r"content=['\"]([^'\"]*)['\"]", call_str)
    if m:
        return m.group(1)
    return None


def extract_content_strings(result):
    """Recursively walk any nested structure (including star-resolved zand
    sub-results carried in point/ring/disc text fields) for string content."""
    out = []

    def collect(v):
        if isinstance(v, str):
            out.append(v)
        elif isinstance(v, dict):
            for vv in v.values():
                collect(vv)
        elif isinstance(v, list):
            for vv in v:
                collect(vv)

    mode = result.get("mode")
    if mode == "whole":
        collect(result.get("block", {}))
    elif mode == "spindle":
        for e in result.get("entries", []):
            collect(e.get("text"))
    elif mode == "point":
        collect(result.get("text"))
    elif mode == "ring":
        for s in result.get("siblings", []):
            collect(s.get("text"))
    elif mode == "directory":
        collect(result.get("subtree"))
    elif mode == "disc":
        for n in result.get("nodes", []):
            collect(n.get("text"))
    elif mode == "error":
        collect(result.get("message"))
    return out


def count_entries(result):
    mode = result.get("mode")
    if mode == "spindle":
        return len(result.get("entries", []))
    if mode == "disc":
        return len(result.get("nodes", []))
    if mode == "ring":
        return len(result.get("siblings", []))
    return None


def status_sequence(result):
    if result.get("mode") == "spindle":
        return [e.get("status") for e in result.get("entries", [])]
    return None


def main():
    total = 0
    passes = 0
    for tezt_file, default_fixture, label in BATTERIES:
        print(f"\n=== Battery: {label} (tests in {tezt_file}) ===")
        with open(os.path.join(HERE, tezt_file)) as f:
            tests = json.load(f)

        for branch in sorted(k for k in tests if k.isdigit() and k != "0"):
            test = tests[branch]
            if not isinstance(test, dict):
                continue
            total += 1
            # Per-branch fixture override (for batteries spanning multiple fixtures)
            fixture_file = FIXTURE_OVERRIDE.get(label, {}).get(branch, default_fixture)
            with open(os.path.join(HERE, fixture_file)) as f:
                fixture = json.load(f)
            call = test.get("1", "")
            number, attention, star = parse_call(call)

            # Writes battery: parse content, run write, then run verify-read
            if label == "writes":
                content = parse_content(call)
                try:
                    write_result = zand(
                        fixture, number=number, attention=attention,
                        content=content, star=star,
                        block_loader=block_loader if star else None,
                    )
                except InvalidAddressError as e:
                    write_result = {"mode": "error", "message": str(e)}

                problems = []
                expected_write_mode = EXPECTED_MODE["writes"].get(branch)
                actual_write_mode = write_result.get("mode")
                if expected_write_mode and actual_write_mode != expected_write_mode:
                    problems.append(
                        f"write mode '{actual_write_mode}', expected '{expected_write_mode}'"
                    )
                if not write_result.get("ok"):
                    problems.append(f"write returned ok={write_result.get('ok')}")

                # Verify-read at branch.3
                verify_call = test.get("3", "")
                if verify_call:
                    vnum, vatt, vstar = parse_call(verify_call)
                    try:
                        verify_result = zand(
                            fixture, number=vnum, attention=vatt,
                            star=vstar,
                            block_loader=block_loader if vstar else None,
                        )
                    except InvalidAddressError as e:
                        verify_result = {"mode": "error", "message": str(e)}
                    content_strs = extract_content_strings(verify_result)
                    joined = "\n".join(content_strs)
                    missing = [m for m in MARKERS["writes"].get(branch, [])
                               if m not in joined]
                    if missing:
                        problems.append(f"verify missing: {missing}")

                if not problems:
                    passes += 1
                    print(f"  branch {branch}: PASS (write={actual_write_mode})")
                else:
                    print(f"  branch {branch}: FAIL ({'; '.join(problems)})")
                continue

            try:
                result = zand(
                    fixture, number=number, attention=attention,
                    star=star, block_loader=block_loader if star else None,
                )
            except InvalidAddressError as e:
                result = {"mode": "error", "message": str(e)}

            content = extract_content_strings(result)
            mode = result.get("mode", "?")
            problems = []

            joined = "\n".join(content)
            missing = [m for m in MARKERS.get(label, {}).get(branch, [])
                       if m not in joined]
            if missing:
                problems.append(f"missing markers: {missing}")

            expected_mode = EXPECTED_MODE.get(label, {}).get(branch)
            if expected_mode and mode != expected_mode:
                problems.append(f"mode '{mode}', expected '{expected_mode}'")

            expected_count = EXPECTED_COUNT.get(label, {}).get(branch)
            if expected_count is not None:
                actual = count_entries(result)
                if actual != expected_count:
                    problems.append(
                        f"count {actual}, expected {expected_count}"
                    )

            expected_statuses = EXPECTED_STATUSES.get(label, {}).get(branch)
            if expected_statuses is not None:
                actual = status_sequence(result)
                if actual != expected_statuses:
                    problems.append(
                        f"statuses {actual}, expected {expected_statuses}"
                    )

            expected_address = EXPECTED_ADDRESS.get(label, {}).get(branch)
            if expected_address is not None:
                actual = result.get("address")
                if actual != expected_address:
                    problems.append(
                        f"address {actual!r}, expected {expected_address!r}"
                    )

            expected_pscale = EXPECTED_TERMINUS_PSCALE.get(label, {}).get(branch)
            if expected_pscale is not None and mode == "spindle":
                entries = result.get("entries", [])
                if entries:
                    actual_pscale = entries[-1].get("pscale")
                    if actual_pscale != expected_pscale:
                        problems.append(
                            f"terminus pscale {actual_pscale}, expected {expected_pscale}"
                        )

            if not problems:
                passes += 1
                print(f"  branch {branch}: PASS (mode={mode})")
            else:
                print(f"  branch {branch}: FAIL ({'; '.join(problems)})")

    print(f"\n=== Summary: {passes}/{total} tests passed ===")
    return 0 if passes == total else 1


if __name__ == "__main__":
    sys.exit(main())
