"""rules -- read the island's editable policy (the `spine` block) into plain
values, so the resolver and grower consult DATA a Designer edits via spark (the D
of CADO), not Python constants.

The interpreter (the spark function -- parse, descend, fold, voice) and the effects
(file I/O, the LLM call, the HTTP door) stay code: something has to run, and blocks
are inert, interpreted. But the RULES the interpreter consults are data, and data
wants to be a block. This module is the one place that turns the spine block into
values; everything else reads them from here. Built-in fallbacks keep the system
working if the block is absent, so adopting this is a pure relocation of the source
of truth -- from Python literals to a block anyone can edit through the door.

Convention: where the code needs a value, the spine leaf LEADS with it and the prose
follows ' -- ' (the same voicing-head split places use). So:
  spine.1  the size/population ladder, whole (the cartographer voices from it)
  spine.2  "+5 -- ..."            the pscale at which a place becomes its own block
  spine.3  "<root> +11 -- ..."    the cosmology root block and its pscale
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spark"))
import spark

SPINE = os.environ.get("BIOME_SPINE") or os.path.join(HERE, "world", "spine.json")

# built-in fallbacks (the founding real-world cut) -- used only if the block is absent
_ROOT, _ROOT_PSCALE, _SHARD = "real-world-original", 11, 5
_LADDER = ("room/1-person 0, building/10 +1, street-or-village/100 +2, town/1k +3, "
           "large-town-or-valley/10k +4, smaller-city/100k +5, city/1m +6, "
           "region-or-megacity/10m +7, country/100m +8, continent/1b +9, Earth +10")


def _int(s, default):
    m = re.search(r"[+-]?\d+", str(s))
    return int(m.group()) if m else default


def _head(leaf):
    return str(leaf).split(" -- ")[0].strip() if leaf is not None else ""


def read(path=None):
    """(root, root_pscale, shard_pscale, ladder) from the spine block, with fallback.
    Re-reads on each call, so a live edit to the block takes effect without a restart."""
    root, root_ps, shard, ladder = _ROOT, _ROOT_PSCALE, _SHARD, _LADDER
    try:
        b = spark.load(path or SPINE)
    except Exception:
        b = None
    if isinstance(b, dict):
        if isinstance(b.get("1"), str) and b["1"].strip():
            ladder = b["1"].strip()
        h2 = _head(b.get("2"))
        if h2:
            shard = _int(h2, shard)
        h3 = _head(b.get("3")).split()
        if h3:
            root = h3[0]
            for tok in h3[1:]:
                if re.search(r"[+-]?\d+", tok):
                    root_ps = _int(tok, root_ps)
                    break
    return root, root_ps, shard, ladder


ROOT, ROOT_PSCALE, COUNTRY_PSCALE, LADDER = read()
