"""resolver-battery — the de-crystallised resolver (rules from the `mechanic`
block; the kernel only routes). Run: python3 resolver-battery.py

No LLM (RESOLVER_DRY=1): proves the rule is READ from the block — compose_prompt
carries the mechanic's branch 3, not a string baked into the kernel — and the
flow end-to-end: gather the committed acts, settle a scene to the record, spend
the acts. (Real synthesis needs a key; the flow does not.)
"""
import os
import sys
import shutil
import tempfile

os.environ["RESOLVER_DRY"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, "..", "..", "spark"))

import resolver
from store_fs import FsStore

P = F = 0


def ok(label, got, exp):
    global P, F
    if got == exp:
        P += 1
        print("  pass", label)
    else:
        F += 1
        print("  FAIL", label, "\n    got", got, "\n    exp", exp)


root = tempfile.mkdtemp(prefix="battery-resolver-")
store = FsStore(os.path.join(root, "blocks"))
store.save_block("mechanic", {"0": "Mechanic", "3": "RULE-FROM-THE-BLOCK: resolve what actually happens; the grounded reading wins."})
store.save_block("frame", {"1": {"1": {"1": "w-space"}, "2": {"1": "w-time"}, "3": {"1": "w-identity"}}, "2": "1,1"})
store.save_block("w-space", {"1": {"1": {"0": "the taproom", "1": "a scarred long table"}}})
store.save_block("w-time", {"1": {"1": {"0": "the dice are out"}}})
store.save_block("w-identity", {"1": {"1": {"0": "the room minds every hand", "1": "the hooded watcher waits"}}})
store.save_block("liquid-alice", {"0": "alice — committed", "1": "1,1", "2": "I stake low and watch the hooded hands"})
store.save_block("liquid-bron", {"0": "bron — committed", "1": "1,1", "2": "I drift to the merchant's blind side"})

try:
    print("the rule is read from the block, not coded into the kernel")
    acts = resolver.gather_acts(store, "1,1")
    ok("both committed acts gathered", sorted(n for n, _, _ in acts), ["alice", "bron"])
    field = resolver.field_text(store, store.load_block("frame"), ["1", "1"])
    prompt = resolver.compose_prompt(store.load_block("mechanic"), acts, field)
    ok("the prompt carries the mechanic block's rule (verb is a block)", "RULE-FROM-THE-BLOCK" in prompt, True)
    ok("the field is omniscient — names the whos present", "the hooded watcher waits" in prompt, True)
    ok("the field carries the place + the now", "the taproom" in prompt and "the dice are out" in prompt, True)

    print("the flow: gather -> settle a scene -> spend the acts (the witness, no mind)")
    line = resolver.resolve(root)
    ok("a scene was settled from both acts", isinstance(line, str) and "alice" in line and "bron" in line, True)
    scenes = store.load_block("scenes")
    ok("the scene landed in the record", any(isinstance(scenes.get(d), str) and "witnessed" in scenes[d]
                                             for d in "123456789"), True)
    ok("the acts were spent (liquid cleared)", store.load_block("liquid-alice")["2"], "")
    ok("a second resolve finds nothing to do", resolver.resolve(root), None)
finally:
    shutil.rmtree(root)

print()
print("TOTAL: %d passed, %d failed" % (P, F))
sys.exit(1 if F else 0)
