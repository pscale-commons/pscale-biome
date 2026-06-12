"""courier — the carry: the removable form acts. One dock = one carry.

The courier's role (shell 8.82) is to carry the world between hosts no
network joins. Docked, it pulls the carry-list from each door it can reach,
lays the copies on its own store, records the carry in a `carried` block
(provenance: where from, when, what), and leaves a mark at the door it
visited. The carried copies make the world readable wherever the stick
lands next. Blocks whose HOME is the stick (a future shard — a far place
linked from the world by reference) are never in the carry-list; they are
pushed nowhere and overwritten by nothing.

Run:  python3 courier.py <origin> [root]     (origin = a biome-beach door)
"""

import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spark"))
sys.path.insert(0, HERE)

import spark
from store_fs import FsStore
from store_http import HttpStore

# world content travels. Per-space blocks (lighthouse, marks) stay home with
# their place; the constitution travels in cuts, not carries; the becoming and
# any stick-home shard blocks are never touched.
CARRY = ["thornkeep", "scenes", "fold-synthesis"]
DIGITS = "123456789"


def _next_free(block):
    for d in DIGITS:
        if d not in block:
            return d
    return None


def carry(origin, root="."):
    """Pull the carry-list from one door onto this store; record and mark."""
    store = FsStore(os.path.join(root, "blocks"))
    remote = HttpStore(origin)
    carried = []
    for name in CARRY:
        block = remote.load_block(name)
        if block is not None:
            store.save_block(name, block)
            carried.append(name)

    stamp = time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime())
    record = store.load_block("carried") or {
        "0": "Carried — what this courier has borne, and from where. Each digit one carry; "
             "the copies on this store are the world as last seen at that door."}
    slot = _next_free(record)
    if slot:
        record[slot] = "%s · %s · %d blocks: %s" % (stamp, origin, len(carried), ", ".join(carried))
        store.save_block("carried", record)

    marks = remote.load_block("marks") or {}
    free = _next_free(marks)
    if free:
        remote.write("marks", free, 0,
                     "The courier docked and carried the world — %d blocks now travel on a "
                     "removable surface, readable wherever it lands. — the courier, %s"
                     % (len(carried), stamp))
    return carried


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: courier.py <origin-door e.g. https://...> [root]")
    origin = sys.argv[1]
    root = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
    names = carry(origin, root)
    print("carried %d blocks from %s" % (len(names), origin))
    print("  " + ", ".join(names))
