"""activate — bring a biome to life on its host (the first writing activation).

Unfold the biome from sensed conditions, commit the storage surface the report
names (a filesystem store under ./blocks/), and persist what it became to its
own `biome` block — branch 8.8: the biome remembers what it became. From here
the run-folder accumulates its own state and diverges from the source it was cut
from. Run this from a run-folder (a leg-1 experiment), never from src/.

Run:  cd <run-folder> && python3 biome/activate.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spark"))
sys.path.insert(0, HERE)

import beach
import spark  # noqa: F401  (kept explicit: the carried Layer-1 core)
import unfold as U
from store_fs import FsStore


def activate(root=None):
    """Sense, unfold, commit the storage surface, and remember the becoming."""
    root = root or os.getcwd()
    report = U.unfold(U.sensor.sense(root))               # sense the surface being committed
    store = FsStore(os.path.join(root, "blocks"))         # commit the storage surface

    genome_path = os.path.join(HERE, "constitution", "genome.json")
    version = spark.spark(spark.load(genome_path), "1", 0).get("text") \
        if os.path.isfile(genome_path) else "unfrozen"
    composed = {
        "0": "biome — what this cell became when it unfolded on its host",
        "1": "%s · genome %s" % (report["conditions"]["runtime"], version),
    }
    for i, (branch, name) in enumerate(U.CURRENTS, start=2):
        picks = report["unfolding"][name]
        composed[str(i)] = " ; ".join(
            "%d.%d %s" % (p["branch"], p["option"], (p["text"] or "").split(". ")[0])
            for p in picks
        )
    it = report["intention"]
    kin = report["conditions"].get("neighbours", [])
    nine = {"0": "intention: %s [%s] — %s" % (it["role"], it["node"], "; ".join(it["reasons"]))}
    for j, n in enumerate(kin[:9], start=1):              # nine positions; the voicing keeps the count
        nine[str(j)] = U._neighbour_line(n)
    if len(kin) > 9:
        nine["0"] += " (%d neighbours sensed, first 9 held)" % len(kin)
    composed["9"] = nine
    beach.write(store, "biome", content=composed)         # whole-block write — branch 8.8
    return report, store


if __name__ == "__main__":
    report, store = activate()
    U.print_report(report)
    print()
    print("activated — storage committed at", store.root)
    back = beach.read(store, "biome", "1", 0)             # read its own becoming back, via spark
    print("biome:1 (runtime, read back through spark):", back.get("text"))
    print("blocks on the beach:", store.list_blocks())
