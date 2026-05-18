/**
 * zand.ts — the ztone operational primitive (pure-digit pscale).
 *
 * TypeScript port of zand.py. Same semantics, same output shapes.
 * See zand.py docstring and sunztone/whetztone for the spec.
 *
 *   const result = zand(block, "30.5", 0);  // point read
 *   const w = zand(block, "1", 0, "new");   // point write
 *
 * Parity invariant: for every fixture and (number, attention, content, star)
 * tuple, this function produces JSON output structurally equivalent to
 * zand.py's output.
 */

export const __version__ = "zand-ts-alpha-1";
export const __author__ = "claude/canonical";
export const __spec__ = "ztone (sunztone + whetztone)";


export class InvalidAddressError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "InvalidAddressError";
  }
}


// JSON tree types
export type JsonValue = string | JsonObject;
export interface JsonObject { [key: string]: JsonValue }
export type BlockLoader = (name: string) => JsonObject | null;
export type Status = "voiced" | "headless" | "absent";


// ---- Zero-spine helpers ---------------------------------------------------

export function collectZeroText(node: JsonValue | undefined | null): string | null {
  if (typeof node !== "object" || node === null) return null;
  if (!("0" in node)) return null;
  const val = (node as JsonObject)["0"];
  if (typeof val === "string") return val;
  if (typeof val === "object" && val !== null) return collectZeroText(val);
  return null;
}

export function floorDepth(block: JsonObject): number {
  let node: JsonValue = block;
  let depth = 0;
  while (typeof node === "object" && node !== null && "0" in node) {
    depth += 1;
    node = (node as JsonObject)["0"];
    if (typeof node === "string") return depth;
  }
  return depth;
}


// ---- Address parsing ------------------------------------------------------

export function parseAddress(s: string | number | null | undefined): [string[], string[], boolean] {
  if (s === null || s === undefined) return [[], [], false];
  if (typeof s === "boolean") {
    throw new InvalidAddressError(`address must be number or string, got bool ${s}`);
  }
  if (typeof s === "number") {
    if (Number.isInteger(s)) {
      return [String(s).split(""), [], false];
    }
    const formatted = s.toString().replace(/0+$/, "").replace(/\.$/, "");
    if (formatted.includes(".")) {
      const [left, right] = formatted.split(".");
      return [left.split(""), right.split(""), true];
    }
    return [formatted.split(""), [], false];
  }

  const text = String(s);
  const dotCount = (text.match(/\./g) || []).length;
  if (dotCount > 1) {
    throw new InvalidAddressError(
      `"${text}" has ${dotCount} decimal points; pscale addresses carry exactly one`
    );
  }
  let left: string, right: string;
  if (dotCount === 1) {
    [left, right] = text.split(".");
  } else {
    left = text;
    right = "";
  }
  for (const ch of left + right) {
    if (!/[0-9]/.test(ch)) {
      throw new InvalidAddressError(
        `"${text}" contains non-digit character "${ch}"`
      );
    }
  }
  return [left.split(""), right.split(""), dotCount === 1];
}


export function canonicalise(s: string | number | null | undefined, floor: number): [string[], string] {
  if (s === null || s === undefined || s === "") return [[], ""];

  let [left, right, hadDot] = parseAddress(s);

  if (hadDot) {
    if (floor >= 1 && left.length > floor) {
      throw new InvalidAddressError(
        `address "${s}" has ${left.length} digits left of decimal but block floor is ${floor}; left-of-decimal cannot exceed floor`
      );
    }
    if (floor >= 1 && left.length < floor) {
      left = Array(floor - left.length).fill("0").concat(left);
    }
  } else {
    if (floor >= 1) {
      if (left.length >= floor) {
        right = left.slice(floor);
        left = left.slice(0, floor);
      } else {
        left = Array(floor - left.length).fill("0").concat(left);
      }
    }
  }

  const digits = left.concat(right);
  return [digits, formatAddress(digits, floor)];
}


export function formatAddress(digits: string[], floor: number): string {
  if (digits.length === 0) return "";
  if (floor < 1) return digits.join("");
  let left: string[], right: string[];
  if (digits.length <= floor) {
    left = [...digits];
    right = [];
  } else {
    left = digits.slice(0, floor);
    right = digits.slice(floor);
  }
  while (left.length > 1 && left[0] === "0") left = left.slice(1);
  if (right.length > 0) return left.join("") + "." + right.join("");
  return left.join("");
}


// ---- Walk -----------------------------------------------------------------

function makeEntry(value: JsonValue | undefined, depth: number, floor: number): SpindleEntry {
  const pscale = floor - depth;
  if (typeof value === "string") {
    return { pscale, text: value, status: "voiced" };
  }
  if (typeof value === "object" && value !== null) {
    const text = collectZeroText(value);
    if (text === null) return { pscale, text: null, status: "headless" };
    return { pscale, text, status: "voiced" };
  }
  return { pscale, text: null, status: "absent" };
}

export interface SpindleEntry {
  pscale: number;
  text: string | null;
  status: Status;
}

export interface WalkResult {
  chain: SpindleEntry[];
  terminal: JsonValue | null;
  parent: JsonObject | null;
  lastKey: string | null;
}

export function walkBlock(block: JsonObject, digits: string[], floor: number): WalkResult {
  const chain: SpindleEntry[] = [makeEntry(block, 0, floor)];
  let node: JsonValue = block;
  let parent: JsonObject | null = null;
  let lastKey: string | null = null;

  for (let i = 0; i < digits.length; i++) {
    const d = digits[i];
    if (typeof node !== "object" || node === null || !(d in node)) {
      for (let j = i + 1; j <= digits.length; j++) {
        chain.push({ pscale: floor - j, text: null, status: "absent" });
      }
      return { chain, terminal: null, parent, lastKey };
    }
    parent = node as JsonObject;
    lastKey = d;
    node = (node as JsonObject)[d];
    chain.push(makeEntry(node, i + 1, floor));
  }
  return { chain, terminal: node, parent, lastKey };
}


// ---- Star: reference resolution -------------------------------------------

const REF_RE = /^(?<name>[A-Za-z][A-Za-z0-9_\-]*(?::[A-Za-z][A-Za-z0-9_\-]*)*)(?::(?<addr>[0-9]+(?:\.[0-9]+)?)(?::(?<attn>-?[0-9]+))?)?$/;

export function parseReference(s: any): [string, string | null, number | null] | null {
  if (typeof s !== "string") return null;
  const trimmed = s.trim();
  if (!trimmed) return null;
  const m = REF_RE.exec(trimmed);
  if (!m || !m.groups) return null;
  const attnStr = m.groups.attn;
  const attn = attnStr !== undefined ? parseInt(attnStr, 10) : null;
  return [m.groups.name, m.groups.addr ?? null, attn];
}

export function resolveWithStar(value: any, blockLoader: BlockLoader | null): any {
  const ref = typeof value === "string" ? parseReference(value) : null;
  if (ref === null) return value;
  const [name, address, attention] = ref;
  const targetBlock = blockLoader ? blockLoader(name) : null;
  if (targetBlock === null) return value;
  // Star propagates per whetztone:5.2.1 — recursive call carries star=true
  // and the same block_loader so multi-level chains resolve in one outer call.
  return zand(targetBlock, address as any, attention as any, null, true, blockLoader);
}


// ---- ZAND -----------------------------------------------------------------

export function zand(
  block: JsonObject,
  number: string | number | null = null,
  attention: number | null = null,
  content: JsonValue | null = null,
  star: boolean = false,
  blockLoader: BlockLoader | null = null,
): any {
  const floor = floorDepth(block);

  // Whole block
  if (number === null && attention === null && content === null) {
    return { mode: "whole", block, floor };
  }

  // Disc read (no number, attention set, no content)
  if ((number === null || number === "") && attention !== null && content === null) {
    return discRead(block, attention, floor, star, blockLoader);
  }

  // Disc write (no number, attention set, content set)
  if ((number === null || number === "") && attention !== null && content !== null) {
    return discWrite(block, attention, floor, content);
  }

  // Parse the address
  const [digits, canonical] = canonicalise(number, floor);
  const walk = walkBlock(block, digits, floor);
  const terminusPscale = floor - digits.length;

  // Write?
  if (content !== null) {
    return zandWrite(block, digits, attention, terminusPscale, content, floor);
  }

  // Spindle (default when only number given)
  if (attention === null) {
    let entries = walk.chain;
    if (star) {
      entries = entries.map(e => ({
        ...e,
        text: e.status === "voiced" && typeof e.text === "string"
          ? resolveWithStar(e.text, blockLoader)
          : e.text,
      }));
    }
    return { mode: "spindle", address: canonical, floor, entries };
  }

  // Point / ring / directory based on attention vs terminus
  if (attention === terminusPscale) {
    return pointRead(walk.chain, terminusPscale, star, blockLoader);
  }
  if (attention > terminusPscale) {
    return ringReadAt(block, digits, attention, floor, star, blockLoader);
  }
  const targetDepth = floor - attention;
  return dirRead(walk.terminal, digits.length, targetDepth, floor, star, blockLoader);
}


// ---- Shape readers --------------------------------------------------------

function pointRead(chain: SpindleEntry[], pscale: number, star: boolean, loader: BlockLoader | null) {
  const last = chain[chain.length - 1];
  let text: any = last.text;
  if (star && last.status === "voiced" && typeof text === "string") {
    text = resolveWithStar(text, loader);
  }
  return { mode: "point", pscale, text, status: last.status };
}

function ringReadAt(
  block: JsonObject, digits: string[], attention: number, floor: number,
  star: boolean, loader: BlockLoader | null,
) {
  const attentionDepth = floor - attention;
  const parentDepth = attentionDepth - 1;
  if (parentDepth < 0) return { mode: "ring", pscale: attention, siblings: [] };

  let parent: JsonValue = block;
  for (let i = 0; i < parentDepth; i++) {
    const d = digits[i];
    if (typeof parent !== "object" || parent === null || !(d in parent)) {
      return { mode: "ring", pscale: attention, siblings: [] };
    }
    parent = (parent as JsonObject)[d];
  }
  if (typeof parent !== "object" || parent === null) {
    return { mode: "ring", pscale: attention, siblings: [] };
  }

  const lastKey = parentDepth < digits.length ? digits[parentDepth] : null;
  const parentObj = parent as JsonObject;
  const siblings: any[] = [];
  for (const d of "0123456789") {
    if (!(d in parentObj)) continue;
    const v = parentObj[d];
    let text: any = null, status: Status, isBranch: boolean;
    if (typeof v === "string") {
      text = v; status = "voiced"; isBranch = false;
    } else if (typeof v === "object" && v !== null) {
      const zt = collectZeroText(v);
      if (zt === null) { text = null; status = "headless"; isBranch = true; }
      else { text = zt; status = "voiced"; isBranch = true; }
    } else {
      text = null; status = "absent"; isBranch = false;
    }
    if (star && status === "voiced" && typeof text === "string") {
      text = resolveWithStar(text, loader);
    }
    siblings.push({
      digit: d, text, status, is_branch: isBranch, is_walked: d === lastKey,
    });
  }
  return { mode: "ring", pscale: attention, siblings };
}

function dirRead(
  terminal: JsonValue | null, terminusDepth: number, targetDepth: number, floor: number,
  star: boolean, loader: BlockLoader | null,
) {
  if (terminal === null) return { mode: "directory", subtree: null, status: "absent" };
  if (typeof terminal !== "object") {
    let text: any = terminal;
    if (star && typeof text === "string") text = resolveWithStar(text, loader);
    return { mode: "directory", subtree: text };
  }
  const levels = targetDepth - terminusDepth;
  if (levels <= 0) {
    let zt: any = collectZeroText(terminal);
    if (star && typeof zt === "string") zt = resolveWithStar(zt, loader);
    return { mode: "directory", subtree: zt };
  }

  function truncate(node: JsonValue, remaining: number): any {
    if (typeof node !== "object" || node === null) {
      if (star && typeof node === "string") return resolveWithStar(node, loader);
      return node;
    }
    if (remaining <= 0) {
      let zt: any = collectZeroText(node);
      if (star && typeof zt === "string") zt = resolveWithStar(zt, loader);
      return zt;
    }
    const out: JsonObject = {};
    for (const [k, v] of Object.entries(node)) {
      out[k] = truncate(v, remaining - 1);
    }
    return out;
  }

  return { mode: "directory", subtree: truncate(terminal, levels) };
}

function discRead(
  block: JsonObject, attention: number, floor: number,
  star: boolean, loader: BlockLoader | null,
) {
  const targetDepth = floor - attention;
  if (targetDepth < 0) return { mode: "disc", pscale: attention, nodes: [] };

  const nodes: any[] = [];

  function collect(node: JsonValue, depth: number, walked: string[]) {
    if (depth === targetDepth) {
      const entry = makeEntry(node, depth, floor);
      let text: any = entry.text;
      if (star && entry.status === "voiced" && typeof text === "string") {
        text = resolveWithStar(text, loader);
      }
      const address = walked.length > 0 ? formatAddress(walked, floor) : "";
      nodes.push({ address, text, status: entry.status });
      return;
    }
    if (typeof node !== "object" || node === null) return;
    for (const d of "0123456789") {
      if (d in node) {
        collect((node as JsonObject)[d], depth + 1, [...walked, d]);
      }
    }
  }

  collect(block, 0, []);
  return { mode: "disc", pscale: attention, nodes };
}


// ---- Write ----------------------------------------------------------------

function zandWrite(
  block: JsonObject, digits: string[], attention: number | null,
  terminusPscale: number, content: JsonValue, floor: number,
) {
  if (digits.length === 0) {
    if (typeof content === "object" && content !== null) {
      for (const k of Object.keys(block)) delete block[k];
      Object.assign(block, content);
      return { mode: "whole-write", ok: true };
    }
    return { mode: "error", error: "whole-block write requires a dict" };
  }

  // Walk to parent of terminus, creating intermediates with lift
  let node: JsonValue = block;
  for (let i = 0; i < digits.length - 1; i++) {
    const d = digits[i];
    if (typeof node !== "object" || node === null) {
      return { mode: "error", error: "non-dict on walk" };
    }
    const obj = node as JsonObject;
    if (!(d in obj)) {
      obj[d] = {};
    } else if (typeof obj[d] === "string") {
      obj[d] = { "0": obj[d] as string };
    } else if (typeof obj[d] !== "object") {
      obj[d] = {};
    }
    node = obj[d];
  }
  const lastD = digits[digits.length - 1];
  const parent = node as JsonObject;

  // Point write
  if (attention === null || attention === terminusPscale) {
    parent[lastD] = content;
    return { mode: "point-write", ok: true, address: formatAddress(digits, floor) };
  }

  // Ring write — conjugate of ring read; parent at depth (attention_depth - 1)
  if (attention > terminusPscale) {
    if (typeof content !== "object" || content === null) {
      return { mode: "error", error: "ring-write requires dict" };
    }
    const attentionDepth = floor - attention;
    const parentDepth = attentionDepth - 1;
    if (parentDepth < 0) {
      return { mode: "error", error: "ring-write parent_depth below root" };
    }
    let gp: JsonValue = block;
    for (let i = 0; i < parentDepth; i++) {
      const d = digits[i];
      if (typeof gp !== "object" || gp === null) {
        return { mode: "error", error: "non-dict on walk" };
      }
      const gpObj = gp as JsonObject;
      if (!(d in gpObj)) gpObj[d] = {};
      else if (typeof gpObj[d] === "string") gpObj[d] = { "0": gpObj[d] as string };
      else if (typeof gpObj[d] !== "object") gpObj[d] = {};
      gp = gpObj[d];
    }
    const gpObj = gp as JsonObject;
    for (const k of Object.keys(gpObj)) {
      if (/^\d$/.test(k)) delete gpObj[k];
    }
    for (const [k, v] of Object.entries(content as JsonObject)) {
      if (/^\d$/.test(k)) gpObj[k] = v;
    }
    return { mode: "ring-write", ok: true };
  }

  // Directory write
  parent[lastD] = content;
  return { mode: "directory-write", ok: true };
}

function discWrite(block: JsonObject, attention: number, floor: number, content: JsonValue) {
  if (!Array.isArray(content)) {
    return { mode: "error", error: "disc-write requires list" };
  }
  for (const entry of content) {
    if (typeof entry !== "object" || !("address" in (entry as any))) {
      return { mode: "error", error: "disc-write entry malformed" };
    }
    const addr = (entry as any).address;
    const text = (entry as any).text ?? null;
    const [digits] = canonicalise(addr, floor);
    const tp = floor - digits.length;
    zandWrite(block, digits, tp, tp, text, floor);
  }
  return { mode: "disc-write", ok: true };
}
