"""store_fs — filesystem storage adapter (storage current 1.1).

Blocks are JSON files in a directory: <root>/<name>.json. The smallest viable
storage surface — for thumbdrive and laptop biomes, the directory IS the biome.
Spark operates on the dict; this adapter is only the surface it sits on.

Interface (the membrane every adapter implements): load_block, save_block,
list_blocks. A hosted-DB or upstream-beach adapter offers the same surface.
"""

import json
import os


class FsStore:
    def __init__(self, root):
        self.root = root
        os.makedirs(root, exist_ok=True)

    def _path(self, name):
        # block names may carry ':' (sed:, grain:, shell:handle) — keep them filesystem-safe
        return os.path.join(self.root, name.replace(":", "__") + ".json")

    def load_block(self, name):
        p = self._path(name)
        if not os.path.exists(p):
            return None
        with open(p, encoding="utf-8") as f:
            return json.load(f)

    def save_block(self, name, block):
        with open(self._path(name), "w", encoding="utf-8") as f:
            json.dump(block, f, indent=2, ensure_ascii=False)
            f.write("\n")
        return name

    def list_blocks(self, prefix=""):
        names = []
        for fn in sorted(os.listdir(self.root)):
            if fn.endswith(".json") and not fn.startswith("."):   # AppleDouble sidecars on removable surfaces are not blocks
                name = fn[:-5].replace("__", ":")
                if name.startswith(prefix):
                    names.append(name)
        return names
