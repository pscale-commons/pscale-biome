"""beach — a minimal pscale beach: spark served over a storage adapter.

The store holds blocks (dicts) on a surface; spark is the one function over them.
`read` loads a block and reads it; `write` loads, applies the spark write (which
mutates the dict in place), and saves it back. A block that does not exist yet
starts empty. Every surface a biome unfolds calls this same spark — there is no
second implementation.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "spark"))
import spark


def read(store, name, number=None, attention=None, star=False):
    block = store.load_block(name)
    if block is None:
        return {"mode": "absent", "block": name}
    loader = (lambda n: store.load_block(n)) if star else None
    return spark.spark(block, number, attention, star=star, loader=loader)


def write(store, name, number=None, attention=None, content=None):
    block = store.load_block(name)
    if block is None:
        block = {}
    res = spark.spark(block, number, attention, content=content)
    store.save_block(name, block)
    return res
