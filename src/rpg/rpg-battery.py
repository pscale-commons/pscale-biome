"""rpg-battery.py -- conformance for the RPG bench (no LLM calls).

Tests the parts that must be exact regardless of any model: the world loads and
anchors, the frame composes faithfully, the aperture holds (the character's
window excludes the other whos' interiors while hidden_depth holds them), and a
write-back round-trips. The LLM tiers are exercised by play.py, not here.

  python3 rpg-battery.py
"""
import os, sys, shutil, tempfile
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import frame, play
sp = frame.spark

P = F = 0
def check(name, cond):
    global P, F
    if cond:
        P += 1; print("  ok   " + name)
    else:
        F += 1; print("  FAIL " + name)

world = frame.load_world(os.path.join(_HERE, "world"))
check("world: three sibling blocks", set(world) == {"space", "time", "identity"})
check("world: shared floor 4", all(sp.floor(b) == 4 for b in world.values()))
check("world: taproom (walk 1,1,2,1) lands at pscale 0",
      sp.floor(world["space"]) - len(["1", "1", "2", "1"]) == 0)

merch = frame.load_shell(os.path.join(_HERE, "characters", "merchant"))
w = frame.bind_window(merch, world)
t = w["text"]
check("window: includes the taproom (space descent)", "taproom" in t.lower())
check("window: includes the bent coin (public object)",
      "bent" in t.lower() or "worth nothing" in t.lower())
check("window: includes the merchant's standpoint (WHO)", "running my way" in t)
check("window: includes the collective head", "minding everyone" in t)
check("window: includes the shell purpose (SELF)", "carry" in t.lower())
check("aperture: EXCLUDES the keeper's interior", "every fool" not in t.lower())
check("aperture: EXCLUDES the watcher's interior", "won't be the merchant" not in t.lower())

hid = frame.hidden_depth(merch, world)
allhid = " ".join(hid["whos"]).lower()
check("hidden_depth: HOLDS the keeper's interior", "every fool" in allhid)
check("hidden_depth: HOLDS the watcher's interior", "won't be the merchant" in allhid)
check("hidden_depth: the merchant's own standpoint is NOT in the hidden set",
      "running my way" not in allhid)

watch = frame.load_shell(os.path.join(_HERE, "characters", "watcher"))
wt = frame.bind_window(watch, world)["text"]
check("watcher window: a different standpoint than the merchant",
      "won't be the merchant" in wt.lower() and "running my way" not in wt)

# persistence round-trip on a temp copy (never mutate source)
tmp = tempfile.mkdtemp()
shutil.copytree(os.path.join(_HERE, "characters", "merchant"), os.path.join(tmp, "merchant"))
cpath = os.path.join(tmp, "merchant", "conditions.json")
blk = sp.load(cpath)
play.append_child(blk, "[earned] the coin is false (suspected)")
sp.save(cpath, blk)
reloaded = sp.load(cpath)
check("persistence: write-back round-trips",
      any("the coin is false" in str(v) for v in reloaded.values()))
shutil.rmtree(tmp, ignore_errors=True)

fld = sp.fold([world["space"], world["time"], world["identity"]], 0)
check("fold: lays the three world blocks at one pscale", fld["mode"] == "fold" and len(fld["blocks"]) == 3)

print("\n%d ok, %d failed" % (P, F))
sys.exit(1 if F else 0)
