// tezt_spark.ts — TS parity battery for spark.ts (mirrors tezt_spark.py).
// Run:  node --experimental-strip-types tezt_spark.ts   (from src/spark/tezt)

import { spark, floor, parse, parseReference, fold, AddressError } from "../spark.ts";

let P = 0;
let F = 0;
const eq = (a: any, b: any) => JSON.stringify(a) === JSON.stringify(b);

function ok(label: string, got: any, exp: any) {
  if (eq(got, exp)) { P++; console.log("  pass", label); }
  else { F++; console.log("  FAIL", label, "\n    got", JSON.stringify(got), "\n    exp", JSON.stringify(exp)); }
}
function raises(label: string, fn: () => void) {
  try { fn(); F++; console.log("  FAIL", label, "(no error)"); }
  catch (e) {
    if (e instanceof AddressError) { P++; console.log("  pass", label); }
    else { F++; console.log("  FAIL", label, "(wrong error)"); }
  }
}

console.log("address parsing");
ok("bare>=floor", parse("305", 2), ["3", "0", "5"]);
ok("bare<floor", parse("3", 2), ["0", "3"]);
ok("dotted L<floor", parse("34.5", 4), ["0", "0", "3", "4", "5"]);
ok("empty", parse("", 1), []);
raises("multi-dot", () => parse("1.2.3", 1));
raises("non-digit", () => parse("1a", 1));
raises("exceeds-floor", () => parse("12.3", 1));

console.log("floor");
ok("floor1", floor({ "0": "r" }), 1);
ok("floor2", floor({ "0": { "0": "r" } }), 2);

const F1: any = { "0": "root", "1": { "0": "A", "2": { "0": "A2", "3": "A23" } } };
console.log("read shapes");
ok("point 1@0", spark(F1, "1", 0).text, "A");
ok("point absent", spark(F1, "5", 0).status, "absent");
ok("directory 1@-1", spark(F1, "1", -1).subtree, { "0": "A", "2": "A2" });
ok("spindle 1.2", spark(F1, "1.2").entries.map((e: any) => e.text), ["A", "A2"]);
ok("disc @0", spark(F1, null, 0).nodes.map((n: any) => [n.address, n.text]), [["0", "root"], ["1", "A"]]);

const RNG: any = { "0": "place", "1": "north", "2": "east", "3": "south" };
const r = spark(RNG, "2.5", 0);
ok("ring head", r.head, "place");
ok("ring digits", r.siblings.map((s: any) => s.digit), ["1", "2", "3"]);
ok("ring walked", r.siblings.filter((s: any) => s.is_walked).map((s: any) => s.digit), ["2"]);

console.log("clean geometry");
const F2: any = { "0": { "0": "deep", "1": "at01" }, "1": "top" };
ok("floor(F2)", floor(F2), 2);
ok("bare 1 -> 0,1", spark(F2, "1", 0).text, "at01");

console.log("supernest invariance");
ok("1.2@floor1", spark(F1, "1.2", -1).text, "A2");
const SUP: any = { "0": { "0": "root", "1": { "0": "A", "2": { "0": "A2", "3": "A23" } } } };
ok("floor(SUP)", floor(SUP), 2);
ok("1.2@floor2", spark(SUP, "1.2", -1).text, "A2");

console.log("writes");
const W: any = { "0": "root", "1": "branch one" };
spark(W, "1.234", null, "deep");
ok("point+lift", W, { "0": "root", "1": { "0": "branch one", "2": { "3": { "4": "deep" } } } });
const RW: any = { "0": "p", "1": "a", "2": "b" };
spark(RW, "1.5", 0, { "1": "x", "3": "z" });
ok("ring-write", RW, { "0": "p", "1": "x", "3": "z" });
const WW: any = { "0": "old", "5": "gone" };
spark(WW, null, null, { "0": "new", "1": "leaf" });
ok("whole-write", WW, { "0": "new", "1": "leaf" });

console.log("fold");
const B1: any = { "0": "spatial", "1": "taproom" };
const B2: any = { "0": "caris", "1": "too loud" };
ok("fold@0", fold([B1, B2], 0).blocks.map((b: any) => b.nodes.map((n: any) => [n.address, n.text])),
  [[["0", "spatial"], ["1", "taproom"]], [["0", "caris"], ["1", "too loud"]]]);

console.log("reference + star");
ok("ref bare", parseReference("sunztone"), ["sunztone", null, null]);
ok("ref full", parseReference("sed:commons:13:-1"), ["sed:commons", "13", -1]);
ok("ref prose", parseReference("this is text"), null);
const TGT: any = { "0": "the target", "1": "deep value" };
const loader = (n: string) => (n === "tgt" ? TGT : null);
const REF: any = { "0": "idx", "1": "tgt:1:0", "2": "plain text here" };
ok("star follows", spark(REF, "1", 0, undefined, true, loader).text, "deep value");
ok("no star verbatim", spark(REF, "1", 0).text, "tgt:1:0");
ok("prose verbatim", spark(REF, "2", 0, undefined, true, loader).text, "plain text here");
const A: any = { "0": "a", "1": "bref:1:0" };
const B: any = { "0": "b", "1": "cref:1:0" };
const C: any = { "0": "c", "1": "final" };
const chain = (n: string) => (({ bref: B, cref: C } as any)[n] ?? null);
ok("star chain A->B->C", spark(A, "1", 0, undefined, true, chain).text, "final");

console.log(`\nTOTAL: ${P} passed, ${F} failed`);
process.exit(F ? 1 : 0);
