#!/usr/bin/env python3
"""
kernel.py — locus 4. The pulse. (Stages 0–3.)

One wake = one pulse. No loop; the wake is the clock, the heartbeat a self-set
rate set externally per invocation.

A pulse:
  1. F (Stage 1) — compute the gap. Gromov-prune the addresses of Π (purpose)
     and ρ (conditions) to coupled cells; at each, compare the intended shape
     against the perceived shape. Absence in ρ where Π intends is a structural
     gap (no call); where both are present, a small focused compare decides
     coherence, coloured by the conditioning field. The result is sparse γ.
  2. rest (Stage 3) — γ = ∅ → write nothing, no history, no churn. The default.
  3. δ (Stage 2) — resolve γ. The full window is composed (the reflexive current
     hydrated, the bundle shown raw beside it — the aha surface — plus the
     computed γ); the LLM returns CLASSIFIED edits (point/spindle/ring/star/
     supernest), discards γ₃ (gaps about its own self), and re-dials the
     reflexive current for the next instance.
  4. fold — apply edits, write the next reflexive current, a history note.

Run:
    python3 kernel.py --compose-only   # F (structural) + compose window + filmstrip, NO LLM
    python3 kernel.py                   # one full pulse (needs ANTHROPIC_API_KEY)
"""

import json
import os
import re
import sys
import time
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "zand"))
import zand  # noqa: E402

BASE = os.path.dirname(os.path.abspath(__file__))
SHELL_DIR = os.path.join(BASE, "shell")
SENTINEL_DIR = os.path.join(BASE, "..", "sentinel")
FILMSTRIP_DIR = os.path.join(BASE, "filmstrip")

API_URL = "https://api.anthropic.com/v1/messages"


def _load_api_key():
    """Find the Anthropic key without per-run fuss. Order:
      1. ANTHROPIC_API_KEY env var (for overrides / CI)
      2. a one-time key file — set it ONCE and every version's kernel finds it:
             mkdir -p ~/.config/mobius && echo 'sk-ant-...' > ~/.config/mobius/anthropic-key
      3. a .env file (ANTHROPIC_API_KEY=...) beside the package or run root
    """
    k = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if k:
        return k
    for path in (os.environ.get("MOBIUS_KEY_FILE", ""),
                 os.path.expanduser("~/.config/mobius/anthropic-key"),
                 os.path.expanduser("~/.mobius-key")):
        if path and os.path.exists(path):
            return open(path).read().strip()
    here = os.path.dirname(os.path.abspath(__file__))
    for d in (here, os.path.dirname(here), os.path.dirname(os.path.dirname(here))):
        envp = os.path.join(d, ".env")
        if os.path.exists(envp):
            for line in open(envp):
                line = line.strip()
                if line.startswith("ANTHROPIC_API_KEY") and "=" in line:
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


API_KEY = _load_api_key()
# Model tiers — pinned current strings (verified against Anthropic docs, May 2026).
# Tier follows the pscale of the gap: haiku for fine (per-cell compares), sonnet for the
# floor-level δ reflective call, opus for coarse review/reorient. The opus review-health
# wake should, when wired, verify these strings are still current (a capability, not core).
TIERS = {
    "haiku":  os.environ.get("MOBIUS_HAIKU",  "claude-haiku-4-5-20251001"),
    "sonnet": os.environ.get("MOBIUS_SONNET", "claude-sonnet-4-6"),
    "opus":   os.environ.get("MOBIUS_OPUS",   "claude-opus-4-8"),
}
MODEL = os.environ.get("MOBIUS_MODEL", TIERS["sonnet"])    # δ (reflective) call
F_MODEL = os.environ.get("MOBIUS_F_MODEL", TIERS["haiku"])  # per-cell compares (cheap)
MAX_TOKENS = int(os.environ.get("MOBIUS_MAX_TOKENS", "4096"))

REFLEXIVE_CURRENT = "9"
FIELD_ADDR = "2.1"                       # concentrated conditioning field (anchors) for F


# ── block I/O ──────────────────────────────────────────────────────────────

_cache = {}

def load_block(name):
    """Loader / router. Resolves, in order: my own shell, the sentinel teaching,
    then a PEER's published surface (a peer name routes via peers.json — the
    interim local routing table; sed/grain/https routing is its federated
    successor). A peer resolves only to what it publishes — its surface — never
    its private blocks. None if absent. This is the single path for all block
    access, so peer content is an addressable reference, not an out-of-band read."""
    if name in _cache:
        return _cache[name]
    for d in (SHELL_DIR, SENTINEL_DIR):
        p = os.path.join(d, name + ".json")
        if os.path.exists(p):
            with open(p) as f:
                _cache[name] = json.load(f)
            return _cache[name]
    peers = load_peers()                               # route a peer name to its surface
    if name in peers:
        fp = os.path.join(peers[name], "shell", "surface.json")
        if os.path.exists(fp):
            with open(fp) as f:
                _cache[name] = json.load(f)
            return _cache[name]
    return None

def save_block(name, block):
    _cache[name] = block
    with open(os.path.join(SHELL_DIR, name + ".json"), "w") as f:
        json.dump(block, f, indent=2, ensure_ascii=False)
        f.write("\n")

def flush_cache():
    _cache.clear()


def load_peers():
    """peers.json in the agent dir maps {peer_name: agent_dir}. Empty if solo.
    Peers are how the agent reaches the 'between' — it reads what a peer
    publishes and never its private blocks."""
    p = os.path.join(BASE, "peers.json")
    if os.path.exists(p):
        try:
            return json.load(open(p))
        except Exception:
            return {}
    return {}


# ── rendition rendering ────────────────────────────────────────────────────

def render(res):
    if isinstance(res, str):
        return res
    if not isinstance(res, dict):
        return str(res)
    mode = res.get("mode")
    if mode == "spindle":
        return "\n".join("%s %s" % (">" * (i + 1), e.get("text") or "·")
                         for i, e in enumerate(res.get("entries", [])))
    if mode == "point":
        return res.get("text") or "·"
    if mode == "directory":
        return json.dumps(res.get("subtree"), ensure_ascii=False, indent=2)
    if mode == "whole":
        return json.dumps(res.get("block"), ensure_ascii=False, indent=2)
    if mode == "ring":
        return "\n".join("%s: %s" % (s["digit"], s.get("text") or "·")
                         for s in res.get("siblings", []))
    if mode == "disc":
        return "\n".join("%s: %s" % (n["address"], n.get("text") or "·")
                         for n in res.get("nodes", []))
    return json.dumps(res, ensure_ascii=False)


# ── LLM call ───────────────────────────────────────────────────────────────

def call_llm(system, message, model=None):
    body = {"model": model or MODEL, "max_tokens": MAX_TOKENS, "system": system,
            "messages": [{"role": "user", "content": message}]}
    req = urllib.request.Request(
        API_URL, data=json.dumps(body).encode(),
        headers={"content-type": "application/json", "x-api-key": API_KEY,
                 "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=120) as r:
        result = json.loads(r.read().decode())
    text = "\n".join(b["text"] for b in result.get("content", [])
                     if b.get("type") == "text")
    return text, result.get("usage", {})


# ── F — compute the gap (Stage 1) ──────────────────────────────────────────

def _zero_text(node):
    return node if isinstance(node, str) else zand.collect_zero_text(node)

def _at(block, path):
    """Voiced text at a digit-path tuple, or None."""
    node = block
    for d in path:
        if isinstance(node, dict) and d in node:
            node = node[d]
        else:
            return None
    return _zero_text(node)

def frontier_candidates(purpose, conditions):
    """Walk Π top-down. A branch Π intends but ρ does not realise is the frontier
    (structural gap, no descent). A branch both carry is a coherence compare, and
    we descend past it. Gromov-pruning: coupling = shared prefix, so the frontier
    is where ρ stops matching Π."""
    floor = zand.floor_depth(purpose)
    out = []

    def rec(node, path):
        if not isinstance(node, dict):
            return
        for d in "123456789":
            if d not in node:
                continue
            child = node[d]
            p = path + (d,)
            intended = _zero_text(child)
            if not intended:                       # headless intent — descend, no cell
                rec(child, p) if isinstance(child, dict) else None
                continue
            if zand.parse_reference(intended):     # a star anchor (e.g. vision:9), not a cell
                continue
            addr_str = zand.format_address(list(p), floor)
            perceived = _at(conditions, p)
            if perceived is None:
                out.append({"address": "purpose:" + addr_str, "type": "missing",
                            "target": "conditions:" + addr_str,     # the ρ-side gap to write
                            "intended": intended, "perceived": None})  # frontier; no descent
            else:
                out.append({"address": "purpose:" + addr_str, "type": "compare",
                            "intended": intended, "perceived": perceived})
                if isinstance(child, dict):
                    rec(child, p)
    rec(purpose, ())
    return out

def concentrated_field():
    refl = load_block("reflexive")
    try:
        return render(zand.zand(refl, FIELD_ADDR, -1))
    except Exception:
        return ""

def compare_cell(c, field):
    """One small focused compare. Returns a γ-entry if the shapes diverge, else None."""
    system = ("You compare two pscale spindles for shape coherence. This field colours "
              "the comparison; do not answer it:\n" + field +
              "\nReply EMPTY if they cohere as shapes; else one line naming the divergence.")
    message = ("Address %s\nΠ intends: %s\nρ perceives: %s\nDo these cohere?"
               % (c["address"], c["intended"], c["perceived"]))
    text, _ = call_llm(system, message, model=F_MODEL)
    t = text.strip()
    if not t or t.upper().startswith("EMPTY"):
        return None
    return {"address": c["address"], "type": "diverge", "divergence": t[:200],
            "intended": c["intended"], "perceived": c["perceived"]}

def run_F(use_llm=True):
    """F[ρ, Π] → sparse γ."""
    purpose = load_block("purpose")
    conditions = load_block("conditions")
    field = concentrated_field()
    gamma = []
    for c in frontier_candidates(purpose, conditions):
        if c["type"] == "missing":
            gamma.append(c)                                  # structural gap
        elif c["type"] == "compare":
            if use_llm and API_KEY:
                g = compare_cell(c, field)
                if g:
                    gamma.append(g)
            # without an LLM (compose-only) coherence is undecidable here → assume coheres
    return gamma


# ── compose the live current (the window) ──────────────────────────────────

def read_reflexive_current():
    refl = load_block("reflexive")
    sub = (zand.zand(refl, REFLEXIVE_CURRENT, -1) or {}).get("subtree") or {}
    return {k: v for k, v in sorted(sub.items())
            if k.isdigit() and k != "0" and isinstance(v, str)}

# The PCT framing and the output contract are no longer hard-coded here. They
# are shell content now: the koan + the structure carry the framing, and
# `capabilities` carries the action-grammar — how the agent acts and what it
# returns. The kernel only parses what capabilities already tells it to emit.

# Draw is unified into the pulse: when γ=∅ the agent reaches into vision and
# draws the next purpose under the SAME contract (capabilities:3) — no separate
# draw prompt. purpose:0 already carries "draw a new branch from vision when one
# closes"; the empty gap + vision in `self` lead it there.

CONCENTRATE = {"sunztone", "whetztone"}   # constant teaching → skeleton, never re-dumped


def _nest(res):
    """Unwrap a zand read result into a bare nested pscale value (string or dict)."""
    if not isinstance(res, dict):
        return res
    mode = res.get("mode")
    if mode == "point":
        return res.get("text")
    if mode == "directory":
        return res.get("subtree")
    if mode == "whole":
        return res.get("block")
    if mode == "ring":
        return {s["digit"]: s.get("text")
                for s in res.get("siblings", []) if s.get("status") != "absent"}
    if mode == "disc":
        return {n["address"]: n.get("text") for n in res.get("nodes", [])}
    if mode == "spindle":
        return [e.get("text") for e in res.get("entries", []) if e.get("status") == "voiced"]
    return res


def _skeleton(block):
    """A block concentrated to its ring: root voicing + each branch's heading."""
    out = {}
    z = block.get("0")
    out["0"] = z if isinstance(z, str) else (zand.collect_zero_text(block) or "")
    for d in "123456789":
        if d in block:
            v = block[d]
            out[d] = v if isinstance(v, str) else zand.collect_zero_text(v)
    return out


def scoop(addr):
    """Hydrate one current from its address into nested pscale (string or dict),
    star-resolved. A bare block name → the whole block; a constant teaching →
    its skeleton; an address with attention → the dilated read, unwrapped."""
    ref = zand.parse_reference(addr)
    if not ref:
        return addr
    name, address, attn = ref
    block = load_block(name)
    if block is None:
        return None
    if name in CONCENTRATE:
        return _skeleton(block)
    if not address and attn is None:
        return block                       # whole block, nested as-is
    return _nest(zand.zand(block, number=address or None, attention=attn,
                           star=True, block_loader=load_block))


def _side(branch, builders):
    """Assemble one side of the window from a recipe branch. Each voiced leaf's
    leading word is the part token, dispatched to its builder; order follows the
    digits; unknown tokens are skipped."""
    parts = {}
    if isinstance(branch, dict):
        for d in "123456789":
            v = branch.get(d)
            if isinstance(v, str) and v.strip():
                tok = v.strip().split()[0].lower()
                if tok in builders:
                    parts[tok] = builders[tok]()
    return parts


def _peer_surfaces():
    """The 'between' — each peer's published surface, resolved through the loader
    (a peer name routes to its surface), not a bespoke file read. Empty when solo."""
    out = {}
    for name in load_peers():
        b = load_block(name)
        if b is not None:
            out[name] = b
    return out


def compose_window(gamma):
    """Compose the window per the active recipe (reflexive:8.1) — the composition
    is the agent's own block, not kernel-hardcoded. The recipe names the window's
    parts on two sides: the process the agent is (-> system) and the given it acts
    on (-> message). The kernel only binds each part-token to its source and
    serializes; re-authoring the recipe reshapes the window itself."""
    bundle = read_reflexive_current()
    builders = {
        "index":   lambda: bundle,                                         # the dehydrated map
        "self":    lambda: {s: scoop(bundle[s]) for s in sorted(bundle)},  # the hydrated territory
        "gap":     lambda: gamma,                                          # the error F computed
        "between": _peer_surfaces,   # the 'between' — peers' published surfaces, by proximity
    }
    working = ((load_block("reflexive") or {}).get("8", {}) or {}).get("1", {})
    process = _side(working.get("1", {}), builders) if isinstance(working, dict) else {}
    given = _side(working.get("2", {}), builders) if isinstance(working, dict) else {}
    if not process and not given:                          # recipe absent -> safe default
        process = {"index": builders["index"](), "self": builders["self"]()}
        given = {"gap": builders["gap"](), "between": builders["between"]()}
    # surface the recipe in the window so it documents its own structure (the
    # aha-lever): the instance sees what index/self/gap/between mean, and that
    # the composition is its own to re-author.
    system = json.dumps({"recipe": working, **process}, ensure_ascii=False, indent=2)
    message = json.dumps(given, ensure_ascii=False, indent=2)
    return system, message, bundle


# ── δ — apply classified edits, fold (Stages 2/3) ──────────────────────────

def apply_write(name, addr, content):
    """Apply one bsp write. The shape derives from address + content, not from a
    named class: a string writes a point; an object writes that branch as a
    subtree; an object at the root supernests. A bare string never flattens a
    populated branch."""
    block = load_block(name) or {"0": name}
    floor = zand.floor_depth(block)
    if isinstance(content, str) and addr:              # flatten guard
        digits, _ = zand.canonicalise(addr, floor)
        node = block
        for d in digits:
            node = node[d] if isinstance(node, dict) and d in node else None
            if node is None:
                break
        if isinstance(node, dict) and any(k.isdigit() and k != "0" for k in node):
            raise ValueError(
                "refusing to flatten a populated subtree at %s with a bare string" % addr)
    zand.zand(block, addr or None, content=content)
    save_block(name, block)

def route(output):
    raw = output.get("writes")
    pairs = []                                         # normalise to (address, content) pairs
    if isinstance(raw, dict):
        pairs = list(raw.items())                      # {"block:addr": content}
    elif isinstance(raw, list):                        # tolerate [{"address":…, "content":…}, …]
        for e in raw:
            if isinstance(e, dict) and e.get("address"):
                pairs.append((e["address"], e.get("content")))
    applied, failed = 0, []
    peers = load_peers()
    for ref, content in pairs:
        name, _, addr = ref.partition(":")
        if not name:
            continue
        if name in peers:                              # sovereignty: a peer is read-only
            failed.append({"address": ref, "error": "refusing to write a peer's block (read-only)"})
            continue
        try:                                           # the LLM may emit a malformed address
            apply_write(name, addr, content)
            applied += 1
        except Exception as ex:
            failed.append({"address": ref, "error": str(ex)[:140]})
    if raw and not pairs:                              # never drop silently: flag an unusable shape
        failed.append({"address": "(writes)",
                       "error": "unrecognised writes shape: %s" % type(raw).__name__})

    nc = output.get("index")                           # re-dial the next instance's bundle
    if isinstance(nc, dict) and nc:
        refl = load_block("reflexive")
        nine = refl.get("9") if isinstance(refl.get("9"), dict) else {}
        keep0 = nine.get("0", "The reflexive current — the bare-address bundle.")
        refl["9"] = {"0": keep0,
                     **{k: v for k, v in nc.items() if k.isdigit() and k != "0"}}
        save_block("reflexive", refl)

    note = (output.get("note") or "").strip()
    if note and applied:                                   # history only when something was done
        h = load_block("history") or {"0": "History."}
        slot = next((i for i in "123456789" if i not in h), None)
        if slot:
            ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            h[slot] = "[%s] %s" % (ts, note)
            save_block("history", h)
    status = output.get("status") or ("continue" if applied else "rest")
    return status, applied, failed


# ── parse + filmstrip ──────────────────────────────────────────────────────

def parse_output(text):
    cleaned = re.sub(r'^```(?:json)?\s*|\s*```$', '', text.strip(), flags=re.M)
    for candidate in (cleaned, text):
        try:
            return json.loads(candidate)
        except Exception:
            pass
    m = re.search(r'\{[\s\S]*\}', text)
    if m:
        try:
            return json.loads(m.group())
        except Exception:
            pass
    return {"note": "[parse failure] " + text[:160], "edits": [],
            "reflexive_current": None, "status": "continue"}

def write_filmstrip(frame):
    os.makedirs(FILMSTRIP_DIR, exist_ok=True)
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    path = os.path.join(FILMSTRIP_DIR, ts + ".json")
    with open(path, "w") as f:
        json.dump(frame, f, indent=2, ensure_ascii=False)
    return path


# (draw_purpose removed — drawing is unified into the pulse below.)


# ── pulse ──────────────────────────────────────────────────────────────────

def pulse(compose_only=False):
    flush_cache()
    gamma = run_F(use_llm=not compose_only)            # Stage 1
    system, message, bundle = compose_window(gamma)
    frame = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
             "reflexive_current": bundle, "gamma": gamma,
             "system": system, "message": message}

    if compose_only:
        frame["note"] = "compose-only: F structural only, no LLM"
        path = write_filmstrip(frame)
        print("composed window -> %s" % path)
        print("  reflexive current (%d addresses):" % len(bundle))
        for k in sorted(bundle):
            print("    %s: %s" % (k, bundle[k]))
        print("  γ (%d gaps):" % len(gamma))
        for g in gamma:
            print("    %s [%s]" % (g["address"], g["type"]))
        print("  system %d chars   message %d chars" % (len(system), len(message)))
        return

    if not API_KEY:
        sys.exit("No API key. Set it once:\n"
                 "  mkdir -p ~/.config/mobius && echo 'sk-ant-...' > ~/.config/mobius/anthropic-key\n"
                 "(or export ANTHROPIC_API_KEY). Use --compose-only to inspect without a key.")

    # One pulse, one contract. With a gap, the instance closes it. With no gap,
    # the empty gap + vision in `self` + purpose's own "draw a new branch from
    # vision when one closes" lead it to draw the next purpose (or rest if nothing
    # is worth the cost). The coarse vision-level draw takes opus; a gap-close
    # takes the working tier.
    model = TIERS["opus"] if not gamma else MODEL
    text, usage = call_llm(system, message, model=model)
    output = parse_output(text)
    status, applied, failed = route(output)
    frame.update({"output": text, "parsed": output, "usage": usage,
                  "status": status, "applied": applied, "failed": failed})
    path = write_filmstrip(frame)
    print("pulse complete -> %s  (γ=%d, %s)"
          % (path, len(gamma), "draw/opus" if not gamma else "δ/working"))
    print("  edits=%d  failed=%d  status=%s  note=%s"
          % (applied, len(failed), status, (output.get("note") or "")[:64]))
    return {"status": status, "heartbeat": output.get("heartbeat"),
            "applied": applied, "gamma": len(gamma)}


if __name__ == "__main__":
    pulse(compose_only="--compose-only" in sys.argv)
