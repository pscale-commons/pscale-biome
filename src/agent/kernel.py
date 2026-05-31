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
STABLE_BLOCKS = {"sunztone", "reflexive"}


# ── block I/O ──────────────────────────────────────────────────────────────

_cache = {}

def load_block(name):
    """Loader: shell first, then sentinel. None if absent. A beach (underscore)
    reference would be migrate.py-translated here; the native shell is a plain read."""
    if name in _cache:
        return _cache[name]
    for d in (SHELL_DIR, SENTINEL_DIR):
        p = os.path.join(d, name + ".json")
        if os.path.exists(p):
            with open(p) as f:
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

PCT_LINE = (
    "Purpose (Π) is your reference — what should be. Conditions (ρ) is your perception "
    "— what is. F has computed γ, the gap, below. Your task is to close it. No gap, no "
    "writes — rest. Re-dialing the reflexive current reshapes what the next instance wakes into."
)

DELTA_CONTRACT = (
    "Resolve γ. Return ONE json object (optionally in a ```json fence):\n"
    "{\n"
    '  "note": "one line: what you did and why (becomes history). Empty if you rest.",\n'
    '  "edits": [{"address":"block:addr", "class":"point|spindle|ring|star|supernest",\n'
    '             "content": <string for point/star | object for ring/directory>}],\n'
    '  "reflexive_current": {"1":"block:addr", ...} | null,\n'
    '  "heartbeat": <seconds until you want to wake next> | null,\n'
    '  "status": "continue | rest"\n'
    "}\n"
    "RULES:\n"
    "- A 'missing' γ-entry means ρ (conditions) does not yet realise Π (purpose) at that "
    "address — a gap on the ρ SIDE, not an empty purpose. Resolve it by doing or deciding a "
    "concrete step toward what Π intends and recording your perception at the entry's "
    "`target` (a conditions: address). You MAY decompose Π by adding a NEW child "
    "(e.g. purpose:1.4); you must NEVER overwrite or flatten an existing purpose position. "
    "Π is your reference, refined only by deliberate reorientation, never by gap-closure.\n"
    "- A 'diverge' γ-entry means Π and ρ both exist but disagree; edit the side that is "
    "wrong (usually ρ).\n"
    "- One minimal classified edit per γ-entry; no freeform writes. DISCARD any γ-entry "
    "about examining or securing your own self/identity/persistence (γ₃).\n"
    "- Edit ONLY what γ names: the conditions `target` of each entry, or a NEW purpose "
    "child to decompose. Do NOT touch blocks unrelated to the gap (capabilities, "
    "relationships, stash) — a point dilation shows a block's root, not whether it is "
    "already filled.\n"
    "- reflexive_current is the bare-address bundle the next instance wakes into — every "
    "block at a dilation; null keeps it. If γ is empty: edits [], status rest.\n"
    "- heartbeat: seconds until you next want to wake — short with momentum, long when "
    "resting; weigh the cost of running against the use."
)

DRAW_CONTRACT = (
    "Draw the next purpose. Return ONE json (optionally in a ```json fence):\n"
    "{\n"
    '  "note": "one line — what you drew and why (becomes history).",\n'
    '  "purpose": {"address":"purpose:N", "content": <new branch: object or string>} | null,\n'
    '  "heartbeat": <seconds until next wake> | null,\n'
    '  "status": "continue (you drew a new purpose) | rest (nothing worth the cost now)"\n'
    "}\n"
    "Draw ONE concrete, useful next purpose grounded in vision — a real step toward what "
    "vision describes, that a future instance can act on — at a NEW purpose address (not "
    "an existing one). Not a reflection on yourself (γ₃); not a restatement of what is "
    "done. If vision's work is genuinely addressed, or nothing is worth the cost of "
    "running, set purpose null and status rest."
)

def compose_window(gamma):
    bundle = read_reflexive_current()
    sys_currents, msg_currents = [], []
    for slot in sorted(bundle):
        addr = bundle[slot]
        name = addr.split(":")[0]
        res = zand.resolve_with_star(addr, load_block)
        chunk = "=== current %s :: %s ===\n%s" % (slot, addr, render(res))
        (sys_currents if name in STABLE_BLOCKS else msg_currents).append(chunk)

    system = "\n\n".join([
        "You are one instance of a pscale-native agent. You operate by walking and "
        "editing pscale blocks with zand. The teaching below is zand by being it.",
        "=== REFLEXIVE CURRENT — the dehydrated index of THIS window (the same "
        "addresses, bare) ===\n" + json.dumps(bundle, ensure_ascii=False, indent=2),
        "\n\n".join(sys_currents),
        PCT_LINE,
        DELTA_CONTRACT,
    ])
    gamma_text = ("=== γ — the gap F computed (resolve each, minimally and classified) ===\n"
                  + json.dumps(gamma, ensure_ascii=False, indent=2)) if gamma else \
                 "=== γ — empty. The shape is what it is about. Rest. ==="
    message = "\n\n".join(msg_currents + [gamma_text])
    return system, message, bundle


# ── δ — apply classified edits, fold (Stages 2/3) ──────────────────────────

def apply_edit(name, addr, klass, content):
    block = load_block(name) or {"0": name}
    floor = zand.floor_depth(block)
    if klass == "supernest":
        block_copy = dict(block)
        block.clear()
        block.update({"0": block_copy})
        if content is not None:
            zand.zand(block, addr or None, content=content)
    elif klass in ("ring", "directory") and isinstance(content, dict):
        digits, _ = zand.canonicalise(addr, floor)
        term = floor - len(digits)
        att = term + 1 if klass == "ring" else term - 1
        zand.zand(block, addr or None, attention=att, content=content)
    else:                                  # point, star, spindle → point / subtree write
        if isinstance(content, str) and addr:          # flatten guard: don't clobber a subtree
            digits, _ = zand.canonicalise(addr, floor)
            node = block
            for d in digits:
                node = node[d] if isinstance(node, dict) and d in node else None
                if node is None:
                    break
            if isinstance(node, dict) and any(k.isdigit() and k != "0" for k in node):
                raise ValueError(
                    "refusing point-write at %s: would flatten a populated subtree" % addr)
        zand.zand(block, addr or None, content=content)
    save_block(name, block)

def route(output):
    edits = output.get("edits") or []
    applied, failed = 0, []
    for e in edits:
        ref = e.get("address", "")
        name, _, addr = ref.partition(":")
        if not name:
            continue
        try:                                   # the LLM may emit a malformed address
            apply_edit(name, addr, e.get("class", "point"), e.get("content"))
            applied += 1
        except Exception as ex:
            failed.append({"address": ref, "error": str(ex)[:140]})

    nc = output.get("reflexive_current")
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
    return output.get("status", "continue"), applied, failed


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


# ── draw: vision-fed purpose on rest (v003) ────────────────────────────────

def draw_purpose():
    """γ = ∅: reach into vision for the next concrete purpose, or rest genuinely.
    The opus-tier orient wake — what keeps the agent from settling on a starter
    purpose. Returns (parsed_output, usage)."""
    vision = zand.resolve_with_star("vision:9:-2", load_block)
    purpose = zand.zand(load_block("purpose"), None, None)
    history = zand.zand(load_block("history"), None, None)
    system = "\n\n".join([
        "You are one instance of a pscale-native agent, at rest — your purpose is realised, "
        "ρ mirrors Π, no gap. Reach into vision and draw the next purpose so the trajectory "
        "continues rather than settling.",
        "=== vision — your reservoir of what you are for ===\n" + render(vision),
        "=== conditioning ===\n" + concentrated_field(),
        DRAW_CONTRACT,
    ])
    message = "\n\n".join([
        "=== purpose (realised) ===\n" + render(purpose),
        "=== history (what has been done) ===\n" + render(history),
    ])
    text, usage = call_llm(system, message, model=TIERS["opus"])
    return parse_output(text), usage


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

    if not gamma:                                     # γ = ∅ — reach into vision for the next purpose
        if not API_KEY:
            frame.update({"status": "rest", "note": "γ=∅ (no key — cannot draw)"})
            write_filmstrip(frame)
            print("rest — γ=∅ (no key).")
            return {"status": "rest", "heartbeat": None, "applied": 0, "gamma": 0}
        drawn, usage = draw_purpose()
        new_p = drawn.get("purpose") if isinstance(drawn, dict) else None
        note = ((drawn.get("note") if isinstance(drawn, dict) else "") or "").strip()
        applied = 0
        if isinstance(new_p, dict) and new_p.get("address"):
            name, _, addr = new_p["address"].partition(":")
            content = new_p.get("content")
            try:
                klass = "point" if isinstance(content, str) else "directory"
                apply_edit(name or "purpose", addr, klass, content)
                applied, status = 1, "continue"
                h = load_block("history")
                slot = next((i for i in "123456789" if i not in h), None)
                if slot:
                    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    h[slot] = "[%s] drew purpose %s: %s" % (ts, new_p["address"], note)
                    save_block("history", h)
            except Exception as ex:
                status, note = "rest", "draw rejected: %s" % str(ex)[:100]
        else:
            status = (drawn.get("status") if isinstance(drawn, dict) else "rest") or "rest"
            note = note or "γ=∅ — nothing worth drawing; rest"
        frame.update({"status": status, "note": note, "drawn": drawn,
                      "usage": usage, "applied": applied})
        write_filmstrip(frame)
        print("draw — status=%s  applied=%d  note=%s" % (status, applied, note[:60]))
        return {"status": status,
                "heartbeat": drawn.get("heartbeat") if isinstance(drawn, dict) else None,
                "applied": applied, "gamma": 0}

    if not API_KEY:
        sys.exit("No API key. Set it once:\n"
                 "  mkdir -p ~/.config/mobius && echo 'sk-ant-...' > ~/.config/mobius/anthropic-key\n"
                 "(or export ANTHROPIC_API_KEY). Use --compose-only to inspect without a key.")
    text, usage = call_llm(system, message)            # Stage 2 — δ
    output = parse_output(text)
    status, applied, failed = route(output)
    frame.update({"output": text, "parsed": output, "usage": usage,
                  "status": status, "applied": applied, "failed": failed})
    path = write_filmstrip(frame)
    print("pulse complete -> %s" % path)
    print("  γ=%d  edits=%d  failed=%d  status=%s  note=%s"
          % (len(gamma), applied, len(failed), status, (output.get("note") or "")[:64]))
    return {"status": status, "heartbeat": output.get("heartbeat"),
            "applied": applied, "gamma": len(gamma)}


if __name__ == "__main__":
    pulse(compose_only="--compose-only" in sys.argv)
