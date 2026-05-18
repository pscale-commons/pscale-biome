#!/usr/bin/env python3
"""
migrate.py — convert an underscore-era pscale block to a ztone (pure-digit)
block. Walk the JSON tree and replace every "_" key with "0". Leaves digit
keys, non-digit keys, and value content unchanged.

This handles the structural migration only. Text content that explicitly
references the underscore convention (e.g. "address 1._" or "the _ chain")
is preserved verbatim — those references should be updated by hand if
they affect interpretation of the migrated block.

Usage:
    python3 migrate.py <input.json> [output.json]

If output is omitted, prints to stdout.

Examples:
    python3 migrate.py sunstone.json sunztone.json
    python3 migrate.py whetstone.json whetztone.json
"""
import json
import sys


def migrate(node):
    """Recursively convert '_' keys to '0' keys throughout a JSON tree."""
    if isinstance(node, dict):
        return {("0" if k == "_" else k): migrate(v) for k, v in node.items()}
    elif isinstance(node, list):
        return [migrate(x) for x in node]
    else:
        return node


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 migrate.py <input.json> [output.json]",
              file=sys.stderr)
        sys.exit(1)

    inp = sys.argv[1]
    with open(inp) as f:
        data = json.load(f)

    out = migrate(data)

    if len(sys.argv) >= 3:
        with open(sys.argv[2], "w") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"Migrated: {inp} -> {sys.argv[2]}")
    else:
        print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
