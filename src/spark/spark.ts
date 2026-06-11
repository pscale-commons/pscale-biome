// spark.ts — the coded kernel for pscale blocks (TypeScript port).
//
// Same protocol as spark.py, validated against the same test cases. A block is
// JSON whose keys are single digits "0"-"9": digit "0" is a node's voicing, and
// "1"-"9" its elaboration. The zero-spine sets the floor (the depth where it
// first reaches a string); pscale = floor - depth. One call over two
// coordinates; shape derived from (number, attention), never chosen.

export type Block = { [k: string]: any };
const DIGITS = "123456789";

export class AddressError extends Error {}

// --- substrate verbs --------------------------------------------------------

export function descend(block: Block, digits: string[]): any {
  let node: any = block;
  for (const d of digits) {
    if (node && typeof node === "object" && d in node) node = node[d];
    else return null;
  }
  return node;
}

export function voice(node: any): string | null {
  while (node && typeof node === "object") {
    if (!("0" in node)) return null;
    node = node["0"];
  }
  return typeof node === "string" ? node : null;
}

export function floor(block: Block): number {
  let n = 0;
  let node: any = block;
  while (node && typeof node === "object") {
    if (!("0" in node)) return n;
    node = node["0"];
    n++;
  }
  return n;
}

export function status(node: any): string {
  if (node === null || node === undefined) return "absent";
  if (typeof node === "string") return "voiced";
  return voice(node) !== null ? "voiced" : "headless";
}

// --- address ----------------------------------------------------------------

export function parse(number: any, flr: number): string[] {
  const s = number === null || number === undefined ? "" : String(number);
  if (s === "") return [];
  if (![...s].every((c) => "0123456789.".includes(c)))
    throw new AddressError(`address holds a non-digit: ${number}`);
  if ((s.match(/\./g) || []).length > 1)
    throw new AddressError(`address has more than one decimal: ${number}`);
  if (s.includes(".")) {
    const [left, right] = s.split(".");
    if (left.length > flr) throw new AddressError(`left of decimal exceeds floor ${flr}: ${number}`);
    return (left.padStart(flr, "0") + right).split("");
  }
  return (s.length >= flr ? s : s.padStart(flr, "0")).split("");
}

// --- reference (refer/star) -------------------------------------------------

const NAME = /^[A-Za-z][A-Za-z0-9_-]*$/;
const ADDR = /^\d+(\.\d+)?$/;
const ATT = /^-?\d+$/;

export function parseReference(leaf: any): [string, string | null, number | null] | null {
  if (typeof leaf !== "string" || leaf === "" || leaf.includes(" ")) return null;
  const parts = leaf.split(":");
  let i = 0;
  const nameSegs: string[] = [];
  while (i < parts.length && NAME.test(parts[i])) {
    nameSegs.push(parts[i]);
    i++;
  }
  if (nameSegs.length === 0) return null;
  const name = nameSegs.join(":");
  let address: string | null = null;
  let attention: number | null = null;
  if (i < parts.length) {
    if (ADDR.test(parts[i])) { address = parts[i]; i++; } else return null;
  }
  if (i < parts.length) {
    if (ATT.test(parts[i])) { attention = parseInt(parts[i], 10); i++; } else return null;
  }
  return i === parts.length ? [name, address, attention] : null;
}

function resolve(text: any, loader: ((n: string) => Block | null) | null): any {
  if (!loader || typeof text !== "string") return null;
  const ref = parseReference(text);
  if (!ref) return null;
  const [name, address, attention] = ref;
  const target = loader(name);
  if (!target) return null;
  return spark(target, address, attention, undefined, true, loader);
}

// --- the function -----------------------------------------------------------

export function spark(
  block: Block,
  number: any = null,
  attention: any = null,
  content: any = undefined,
  star = false,
  loader: ((n: string) => Block | null) | null = null,
): any {
  const flr = floor(block);
  if (content !== undefined) return _write(block, number, attention, content, flr);
  if (number === null || number === undefined || String(number) === "") {
    if (attention === null || attention === undefined) return { mode: "whole", floor: flr, block };
    return _disc(block, attention, flr);
  }
  const walk = parse(number, flr);
  const term = flr - walk.length;
  if (attention === null || attention === undefined) return _spindle(block, walk, flr);
  if (attention === term) {
    const res = _point(block, walk, term);
    if (star && res.status === "voiced") {
      const followed = resolve(res.text, loader);
      if (followed !== null) return followed;
    }
    return res;
  }
  if (attention > term) return _ring(block, walk, attention, flr);
  return _directory(block, walk, attention, flr);
}

function _spindle(block: Block, walk: string[], flr: number): any {
  const entries: any[] = [];
  let node: any = block;
  let off = false;
  for (let i = 0; i < walk.length; i++) {
    const d = walk[i];
    node = !off && node && typeof node === "object" && d in node ? node[d] : null;
    if (node === null) off = true;
    entries.push({ depth: i + 1, pscale: flr - (i + 1), text: off ? null : voice(node), status: status(node) });
  }
  return { mode: "spindle", floor: flr, entries };
}

function _point(block: Block, walk: string[], term: number): any {
  const node = descend(block, walk);
  return { mode: "point", pscale: term, text: node !== null ? voice(node) : null, status: status(node) };
}

function _ring(block: Block, walk: string[], attention: number, flr: number): any {
  const depth = flr - attention;
  if (depth < 1) return { mode: "ring", pscale: attention, head: voice(block), siblings: [] };
  const parent = descend(block, walk.slice(0, depth - 1));
  const walked = depth - 1 < walk.length ? walk[depth - 1] : null;
  const sibs: any[] = [];
  if (parent && typeof parent === "object") {
    for (const d of DIGITS) {
      if (d in parent) {
        const ch = parent[d];
        const branch = ch && typeof ch === "object";
        sibs.push({ digit: d, text: branch ? voice(ch) : ch, status: status(ch), is_branch: branch, is_walked: d === walked });
      }
    }
  }
  return { mode: "ring", pscale: attention, head: parent !== null ? voice(parent) : null, siblings: sibs };
}

function _directory(block: Block, walk: string[], attention: number, flr: number): any {
  const node = descend(block, walk);
  const remaining = flr - attention - walk.length;
  function build(n: any, depthLeft: number): any {
    if (!n || typeof n !== "object") return n;
    if (depthLeft <= 0) return voice(n);
    const out: any = {};
    if ("0" in n) out["0"] = voice(n);
    for (const d of DIGITS) if (d in n) out[d] = build(n[d], depthLeft - 1);
    return out;
  }
  return { mode: "directory", pscale: attention, subtree: node && typeof node === "object" ? build(node, remaining) : node };
}

function _disc(block: Block, attention: number, flr: number): any {
  const target = flr - attention;
  const nodes: any[] = [];
  function rec(n: any, depth: number, addr: string) {
    if (depth === target) {
      nodes.push({ address: addr, text: n && typeof n === "object" ? voice(n) : n, status: status(n) });
      return;
    }
    if (n && typeof n === "object") for (const d of ["0", ...DIGITS]) if (d in n) rec(n[d], depth + 1, addr + d);
  }
  rec(block, 0, "");
  return { mode: "disc", pscale: attention, nodes };
}

// --- write (conjugate of read) ----------------------------------------------

function _ensure(block: Block, digits: string[]): any {
  let node: any = block;
  for (const d of digits) {
    if (!(d in node)) node[d] = {};
    else if (typeof node[d] === "string") node[d] = { "0": node[d] };
    node = node[d];
  }
  return node;
}

function _write(block: Block, number: any, attention: any, content: any, flr: number): any {
  if (number === null || number === undefined || String(number) === "") {
    if ((attention === null || attention === undefined) && content && typeof content === "object") {
      for (const k of Object.keys(block)) delete block[k];
      Object.assign(block, content);
      return { mode: "whole-write", ok: true };
    }
    throw new AddressError("a write with no number needs a whole-block object");
  }
  const walk = parse(number, flr);
  const term = flr - walk.length;
  if (attention === null || attention === undefined || attention === term) {
    const parent = _ensure(block, walk.slice(0, -1));
    parent[walk[walk.length - 1]] = content;
    return { mode: "point-write", ok: true };
  }
  if (attention > term) {
    if (typeof content !== "object" || content === null || Array.isArray(content)) {
      throw new AddressError(
        "a ring write replaces the digit children — content must be an " +
        "object of digit keys (note: an empty block has floor 0, so every " +
        "term is negative; create a new block with a whole-block write — " +
        "no number, object content)");
    }
    const depth = flr - attention;
    const parent = _ensure(block, walk.slice(0, depth - 1));
    for (const d of DIGITS) delete parent[d];
    Object.assign(parent, content);
    return { mode: "ring-write", ok: true };
  }
  const parent = _ensure(block, walk.slice(0, -1));
  parent[walk[walk.length - 1]] = content;
  return { mode: "directory-write", ok: true };
}

// --- fold (lay N blocks against the shared floor) ---------------------------

export function fold(blocks: Block[], attention: number): any {
  const rows = blocks.map((b, i) => ({ block: i, nodes: _disc(b, attention, floor(b)).nodes }));
  return { mode: "fold", pscale: attention, blocks: rows };
}
