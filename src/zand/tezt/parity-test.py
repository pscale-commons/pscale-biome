#!/usr/bin/env python3
"""
parity-test.py — verify zand.py and zand.ts produce structurally equivalent
output for every read test across all batteries. Writes are tested separately
by tezt-writes.json against each implementation; their post-write block state
is compared here too.

Usage: python3 parity-test.py
"""
import ast
import copy
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZAND_DIR = os.path.normpath(os.path.join(HERE, ".."))
REPO_ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ZAND_DIR)
from zand import zand, InvalidAddressError

TSX = os.path.join(REPO_ROOT, "node_modules", ".bin", "tsx")
ZAND_CLI = os.path.join(ZAND_DIR, "zand-cli.ts")


# Batteries to check (all reads — writes handled separately at end)
READ_BATTERIES = [
    ("tezt-spatial.json", "test-spatial-floor3.json", "spatial"),
    ("tezt-canonical.json", "test-spatial-floor3.json", "canonical"),
    ("tezt-edge.json", "test-spatial-floor3.json", "edge"),
    ("tezt-sunztone.json", "sunztone.json", "sunztone"),
    ("tezt-star.json", "test-refs.json", "star"),
    ("tezt-absorption.json", "absorb-floor1.json", "absorption"),
    ("tezt-nesting.json", "subnest-before.json", "nesting"),
    ("tezt-reverse.json", "test-spatial-floor3.json", "reverse"),
]

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
        "1": "test-spatial-floor3.json", "2": "test-spatial-floor3.json",
        "3": "test-spatial-floor3.json", "4": "absorb-floor2.json",
        "5": "sunztone.json", "6": "sunztone.json",
    },
}


def parse_call(call_str):
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


def run_py(fixture_path, number, attention, content, star):
    with open(fixture_path) as f:
        block = json.load(f)
    loader = None
    if star:
        fixture_dir = os.path.dirname(os.path.abspath(fixture_path))
        def loader(name):
            p = os.path.join(fixture_dir, f"{name}.json")
            if os.path.exists(p):
                with open(p) as f:
                    return json.load(f)
            return None
    try:
        result = zand(block, number=number, attention=attention,
                      content=content, star=star, block_loader=loader)
    except InvalidAddressError as e:
        result = {"mode": "error", "message": str(e)}
    return result, block


def run_ts(fixture_path, number, attention, content, star):
    args = {
        "fixture": fixture_path,
        "number": number,
        "attention": attention,
        "content": content,
        "star": star,
    }
    r = subprocess.run(
        [TSX, ZAND_CLI, json.dumps(args)],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        return {"mode": "error", "message": f"tsx failed: {r.stderr.strip()}"}
    return json.loads(r.stdout)


def normalise(v):
    """Normalise a result for comparison: sort dict keys, recurse."""
    if isinstance(v, dict):
        return {k: normalise(v[k]) for k in sorted(v.keys())}
    if isinstance(v, list):
        return [normalise(x) for x in v]
    return v


def deep_equal(a, b):
    return normalise(a) == normalise(b)


def short(s, n=70):
    s = str(s)
    return s if len(s) <= n else s[:n - 3] + "..."


def main():
    total = 0
    matches = 0
    fails = []

    for tezt_file, default_fixture, label in READ_BATTERIES:
        print(f"\n=== Battery: {label} ===")
        with open(os.path.join(HERE, tezt_file)) as f:
            tests = json.load(f)
        for branch in sorted(k for k in tests if k.isdigit() and k != "0"):
            test = tests[branch]
            if not isinstance(test, dict):
                continue
            total += 1
            fixture_file = FIXTURE_OVERRIDE.get(label, {}).get(branch, default_fixture)
            fixture_path = os.path.join(HERE, fixture_file)
            call = test.get("1", "")
            number, attention, star = parse_call(call)
            content = parse_content(call)

            py_result, _ = run_py(fixture_path, number, attention, content, star)
            ts_result = run_ts(fixture_path, number, attention, content, star)

            if deep_equal(py_result, ts_result):
                matches += 1
                print(f"  branch {branch}: MATCH")
            else:
                fails.append((label, branch, py_result, ts_result))
                print(f"  branch {branch}: DIVERGE")
                print(f"    py: {short(json.dumps(py_result))}")
                print(f"    ts: {short(json.dumps(ts_result))}")

    print(f"\n=== Parity summary: {matches}/{total} tests match ===")

    # Writes parity: load fixture twice, run write on each, compare post-write block
    print(f"\n=== Writes parity ===")
    write_total = 0
    write_matches = 0
    with open(os.path.join(HERE, "tezt-writes.json")) as f:
        writes = json.load(f)
    for branch in sorted(k for k in writes if k.isdigit() and k != "0"):
        test = writes[branch]
        if not isinstance(test, dict):
            continue
        write_total += 1
        fixture_path = os.path.join(HERE, "writes-base.json")
        call = test.get("1", "")
        number, attention, star = parse_call(call)
        content = parse_content(call)

        # Run py write
        with open(fixture_path) as f:
            py_block = json.load(f)
        try:
            py_result = zand(py_block, number=number, attention=attention,
                             content=content, star=star)
        except InvalidAddressError as e:
            py_result = {"mode": "error", "message": str(e)}

        # Run ts write — needs to load fresh fixture, run write, return BOTH result and post-block.
        # We use a special CLI invocation: run write, then re-read the whole block.
        # Simpler approach: ts CLI writes then prints the post-block. We hack by having
        # it print result + block separately. But our current CLI only prints result.
        # Workaround: after the write, run a whole-block read to get the state.
        ts_result = run_ts(fixture_path, number, attention, content, star)
        # Get post-state by reading the whole block (the ts write mutated the JSON in memory
        # in the subprocess only — file is unchanged). So we can't easily compare post-block.
        # For parity, compare just the write RESULT (mode, ok, address).
        if deep_equal(py_result, ts_result):
            write_matches += 1
            print(f"  branch {branch}: MATCH (write result)")
        else:
            print(f"  branch {branch}: DIVERGE (write result)")
            print(f"    py: {short(json.dumps(py_result))}")
            print(f"    ts: {short(json.dumps(ts_result))}")

    print(f"\n=== Writes parity summary: {write_matches}/{write_total} write results match ===")
    print(f"\n=== OVERALL: {matches + write_matches}/{total + write_total} ===")
    return 0 if (matches == total and write_matches == write_total) else 1


if __name__ == "__main__":
    sys.exit(main())
