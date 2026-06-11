"""tezt_spark — regression battery for the coded spark kernel.

Run:  python3 tezt_spark.py     (exits nonzero on any failure)

Covers address parsing, floor discovery, every read shape, every write,
supernest invariance, fold, reference parsing, and star resolution.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import spark
from spark import AddressError

P = F = 0


def ok(label, got, exp):
    global P, F
    if got == exp:
        P += 1
        print("  pass", label)
    else:
        F += 1
        print("  FAIL", label, "\n    got", got, "\n    exp", exp)


def raises(label, fn):
    global P, F
    try:
        fn()
        F += 1
        print("  FAIL", label, "(no error raised)")
    except AddressError:
        P += 1
        print("  pass", label)


print("address parsing")
ok("bare >= floor", spark.parse("305", 2), ["3", "0", "5"])
ok("bare < floor", spark.parse("3", 2), ["0", "3"])
ok("bare == floor", spark.parse("35", 2), ["3", "5"])
ok("dotted left==floor", spark.parse("30.5", 2), ["3", "0", "5"])
ok("dotted left<floor", spark.parse("34.5", 4), ["0", "0", "3", "4", "5"])
ok("empty", spark.parse("", 1), [])
raises("multi-dot rejected", lambda: spark.parse("1.2.3", 1))
raises("non-digit rejected", lambda: spark.parse("1a", 1))
raises("exceeds-floor rejected", lambda: spark.parse("12.3", 1))
raises("ring write refuses non-object content",
       lambda: spark.spark({"0": "r", "1": "a"}, "1.1", 0, content="a string"))

print("floor")
ok("floor 1", spark.floor({"0": "r"}), 1)
ok("floor 2", spark.floor({"0": {"0": "r"}}), 2)
ok("floor 3", spark.floor({"0": {"0": {"0": "r"}}}), 3)

F1 = {"0": "root", "1": {"0": "A", "2": {"0": "A2", "3": "A23"}}}
print("read shapes (floor 1)")
ok("point 1@0", spark.spark(F1, "1", 0)["text"], "A")
ok("point absent", spark.spark(F1, "5", 0)["status"], "absent")
ok("directory 1@-1", spark.spark(F1, "1", -1)["subtree"], {"0": "A", "2": "A2"})
ok("spindle 1.2 texts", [e["text"] for e in spark.spark(F1, "1.2")["entries"]], ["A", "A2"])
ok("disc @0", [(n["address"], n["text"]) for n in spark.spark(F1, None, 0)["nodes"]],
   [("0", "root"), ("1", "A")])
ok("disc @-1", sorted((n["address"], n["text"]) for n in spark.spark(F1, None, -1)["nodes"]),
   [("10", "A"), ("12", "A2")])

RNG = {"0": "place", "1": "north", "2": "east", "3": "south"}
r = spark.spark(RNG, "2.5", 0)
ok("ring head (0 is the head)", r["head"], "place")
ok("ring digits (1-9 only)", [s["digit"] for s in r["siblings"]], ["1", "2", "3"])
ok("ring walked", [s["digit"] for s in r["siblings"] if s["is_walked"]], ["2"])

print("clean geometry (floor 2: 0,1 is an ordinary point)")
F2 = {"0": {"0": "deep", "1": "at01"}, "1": "top"}
ok("floor(F2)", spark.floor(F2), 2)
ok("bare 1 -> position 0,1", spark.spark(F2, "1", 0)["text"], "at01")

print("supernest invariance (a dotted address survives growth)")
ok("1.2 @ floor 1", spark.spark(F1, "1.2", -1)["text"], "A2")
SUP = {"0": {"0": "root", "1": {"0": "A", "2": {"0": "A2", "3": "A23"}}}}
ok("floor(SUP)", spark.floor(SUP), 2)
ok("1.2 @ floor 2 (same semantic)", spark.spark(SUP, "1.2", -1)["text"], "A2")

print("writes (conjugate of reads)")
W = {"0": "root", "1": "branch one"}
spark.spark(W, "1.234", content="deep")
ok("point-write + lift", W, {"0": "root", "1": {"0": "branch one", "2": {"3": {"4": "deep"}}}})
RW = {"0": "p", "1": "a", "2": "b"}
spark.spark(RW, "1.5", 0, content={"1": "x", "3": "z"})
ok("ring-write (0 kept as head)", RW, {"0": "p", "1": "x", "3": "z"})
DW = {"0": "x", "1": "y"}
spark.spark(DW, "1", -1, content={"0": "new", "3": "q"})
ok("directory-write", DW, {"0": "x", "1": {"0": "new", "3": "q"}})
WW = {"0": "old", "5": "gone"}
spark.spark(WW, content={"0": "new", "1": "leaf"})
ok("whole-write", WW, {"0": "new", "1": "leaf"})

print("fold (one address, aspects across blocks)")
B1 = {"0": "spatial", "1": "taproom"}
B2 = {"0": "caris", "1": "too loud"}
f = spark.fold([B1, B2], 0)
ok("fold @0", [[(n["address"], n["text"]) for n in b["nodes"]] for b in f["blocks"]],
   [[("0", "spatial"), ("1", "taproom")], [("0", "caris"), ("1", "too loud")]])

print("reference parsing")
ok("bare name", spark.parse_reference("kindling"), ("kindling", None, None))
ok("name:address", spark.parse_reference("kindling:5"), ("kindling", "5", None))
ok("name:address:attention", spark.parse_reference("kindling:5.1:-3"), ("kindling", "5.1", -3))
ok("namespaced", spark.parse_reference("sed:commons:13:-1"), ("sed:commons", "13", -1))
ok("prose -> none", spark.parse_reference("this is just text"), None)
ok("digit-led -> none", spark.parse_reference("123"), None)

print("star resolution")
TGT = {"0": "the target", "1": "deep value"}
loader = lambda n: {"tgt": TGT}.get(n)
REF = {"0": "idx", "1": "tgt:1:0", "2": "plain text here", "3": "missing:1:0"}
ok("star follows reference", spark.spark(REF, "1", 0, star=True, loader=loader)["text"], "deep value")
ok("no star -> verbatim", spark.spark(REF, "1", 0)["text"], "tgt:1:0")
ok("prose leaf verbatim", spark.spark(REF, "2", 0, star=True, loader=loader)["text"], "plain text here")
ok("missing block verbatim", spark.spark(REF, "3", 0, star=True, loader=loader)["text"], "missing:1:0")
A = {"0": "a", "1": "bref:1:0"}
B = {"0": "b", "1": "cref:1:0"}
C = {"0": "c", "1": "final"}
chain = lambda n: {"bref": B, "cref": C}.get(n)
ok("star chain A->B->C", spark.spark(A, "1", 0, star=True, loader=chain)["text"], "final")

print()
print("TOTAL: %d passed, %d failed" % (P, F))
sys.exit(1 if F else 0)
