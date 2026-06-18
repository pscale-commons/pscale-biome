#!/usr/bin/env python3
"""resonance — the floor-aligned resonance read over a collective (read-only).

The biome-native correspondent to the old-world `bsp-floor` order-parameter.
It lays the triad's blocks against their shared floor with `spark.fold` and
reads where the scales agree (structural resonance) versus where they sit
apart (the content offset — the phase signature). slate's composition branch
already names the move: 7.3 — "the calling mind is the similarity function:
it reads the per-pscale deltas ... or judges the resonance where scales meet."
This is that calling mind, made a caller.

It is OFF TO THE SIDE of the pulse, exactly as the phase-coupling spec's C3
requires: it never touches a shell, never writes, never calls F. It only
folds and reads. The question it answers is the magi reading — is the
collective *aligned in WHAT* (shared shape / eigen-intention) yet *distributed
in content* (the splay), or has it drifted (no shared shape) or collapsed
(two voices merged into one)?

  structural resonance — Jaccard of which addresses each block populates at a
    pscale. High = they share form (the "identical concern-shape" signature).
  content overlap     — token Jaccard at the co-occupied cells. High = they
    also say the same thing there; low = same frame, distinct voice (splay).

Run:  python3 resonance.py <run-root> [--block purpose] [--judge]
e.g.  python3 resonance.py ~/Desktop/mobius-3-runs/v007

`--judge` adds one optional LLM read of the co-occupied cells (needs a key:
ANTHROPIC_API_KEY or ~/.config/mobius/anthropic-key) — the similarity function
as a semantic judge rather than the token proxy. Default is arithmetic only,
no key required.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "spark"))
import spark   # noqa: E402
import kernel  # noqa: E402  (the WHEN-axis reuses the kernel's phase arithmetic)

AGENTS = ("A", "B", "C")


# ── load (read-only) ─────────────────────────────────────────────────────────

def load_triad(run_root, block_name):
    """Each present agent's chosen block, loaded read-only from a run-root.
    Mirrors observer.py: iterate A/B/C, skip any that is absent."""
    triad = {}
    for a in AGENTS:
        p = os.path.join(run_root, a, "agent", "shell", block_name + ".json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                triad[a] = json.load(f)
    return triad


# ── similarity (the caller's job — slate 7.3) ────────────────────────────────

def _present(node):
    """A fold node carries content here: a non-empty voicing, not absent."""
    t = node.get("text")
    return isinstance(t, str) and t.strip() != "" and node.get("status") != "absent"


def _tokens(text):
    """Content words (length > 2), lowercased — the token proxy for overlap."""
    out, word = set(), ""
    for ch in text.lower():
        if ch.isalnum():
            word += ch
        else:
            if len(word) > 2:
                out.add(word)
            word = ""
    if len(word) > 2:
        out.add(word)
    return out


def _jaccard(a, b):
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _depth(node, d=0):
    if not isinstance(node, dict):
        return d
    return max((_depth(v, d + 1) for k, v in node.items() if k.isdigit()), default=d)


def pscale_band(blocks):
    """The pscales to read: the floor (pscale 0, the magnitude point — the
    concern headings) down to the deepest content present below it."""
    flr = min(spark.floor(b) for b in blocks)
    deepest_below = max(_depth(b) for b in blocks) - flr
    return list(range(0, -deepest_below - 1, -1)) or [0]


def read_pscale(triad, P):
    """Fold the triad at one pscale and read structural + content resonance.
    Returns None if no block carries anything at this pscale."""
    names = list(triad)
    folded = spark.fold([triad[n] for n in names], P)
    pop = {}                                          # name -> {address: text}, present only
    for row, name in zip(folded["blocks"], names):
        pop[name] = {nd["address"]: nd["text"] for nd in row["nodes"] if _present(nd)}

    union = set().union(*[set(p) for p in pop.values()]) if pop else set()
    if not union:
        return None
    co = sorted(a for a in union if all(a in pop[n] for n in names))   # every block present
    structural = len(co) / len(union)

    contents, diverging = [], []
    for a in co:
        toks = [_tokens(pop[n][a]) for n in names]
        pairs = [_jaccard(toks[i], toks[j])
                 for i in range(len(toks)) for j in range(i + 1, len(toks))]
        c = sum(pairs) / len(pairs) if pairs else 1.0
        contents.append(c)
        if c < 0.5:                                   # same cell, distinct voice
            diverging.append((a, {n: pop[n][a] for n in names}))
    content = sum(contents) / len(contents) if contents else None

    pairwise = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            pairwise[names[i] + names[j]] = _jaccard(set(pop[names[i]]), set(pop[names[j]]))

    return {"pscale": P, "structural": structural, "content": content,
            "union": len(union), "co_occupied": len(co),
            "pairwise_structural": pairwise, "diverging": diverging}


# ── verdict (heuristic, honest at N=3) ───────────────────────────────────────

def verdict(structural, content, pairwise):
    """Name the regime the trajectory is in. Heuristic — three agents cannot
    show the K_c transition; this only distinguishes the qualitative shapes the
    phase docs care about (splay / drift / collapse)."""
    if structural < 0.4:
        return ("drift", "shapes diverging — the triad is unlocked, not yet "
                "sharing a form to be distributed within.")
    hi = max(pairwise.values()) if pairwise else 0.0
    if content is not None and content > 0.7 and hi > 0.9:
        return ("collapse", "a pair shares both shape and content — two voices "
                "merging toward unison (r→1), the three-ness at risk.")
    if content is not None and content < 0.5:
        return ("splay", "aligned in WHAT (shared shape) and distributed in "
                "content — agreement without unison, the balanced triad.")
    return ("partial", "shared shape with partial content overlap — aligned in "
            "form, only loosely distributed; watch whether it splays or collapses.")


# ── optional semantic judge (slate 7.3, the LLM as similarity function) ───────

def _key():
    k = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if k:
        return k
    p = os.path.expanduser("~/.config/mobius/anthropic-key")
    return open(p).read().strip() if os.path.exists(p) else None


def judge(triad, reads):
    """One read of the co-occupied cells: are they aligned in intent and
    distributed in expression, or collapsing / drifting? Optional; needs a key."""
    import urllib.request
    key = _key()
    if not key:
        return "(--judge needs a key: ANTHROPIC_API_KEY or ~/.config/mobius/anthropic-key)"
    cells = []
    for r in reads:
        for addr, texts in r["diverging"][:4]:
            cells.append({"pscale": r["pscale"], "address": addr, "voices": texts})
    prompt = (
        "Three agents (A, B, C) coordinate only by reading each other's published shape. "
        "Below are cells where all three carry content at the same pscale-address — the "
        "places their forms coincide. For each, judge whether the three VOICES are aligned "
        "in intent while distinct in expression (a healthy distributed 'splay'), or whether "
        "two are collapsing into one (unison), or the set is incoherent (drift). Then give "
        "ONE overall line: splay / collapse / drift, and why.\n\n"
        + json.dumps(cells, ensure_ascii=False, indent=1))
    body = {"model": os.environ.get("MOBIUS_SONNET", "claude-sonnet-4-6"),
            "max_tokens": 400, "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=json.dumps(body).encode(),
        headers={"content-type": "application/json", "x-api-key": key,
                 "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=90) as r:
        out = json.loads(r.read().decode())
    return "".join(b.get("text", "") for b in out.get("content", [])).strip()


# ── run ──────────────────────────────────────────────────────────────────────

def resonate(run_root, block_name="purpose", do_judge=False):
    triad = load_triad(run_root, block_name)
    if len(triad) < 2:
        sys.exit("need at least two agents' %s blocks under %s/{A,B,C}/agent/shell/"
                 % (block_name, run_root))
    blocks = list(triad.values())
    floors = {spark.floor(b) for b in blocks}
    band = pscale_band(blocks)

    print("resonance — fold of %s across %s, at %s"
          % (block_name, "·".join(triad), os.path.basename(run_root.rstrip("/")) or run_root))
    if len(floors) > 1:
        print("  ⚠ floors differ %s — cross-alignment assumes a shared calibration "
              "(slate 7.4); reading per-pscale anyway." % sorted(floors))

    reads = [r for P in band if (r := read_pscale(triad, P)) is not None]
    s_all = [r["structural"] for r in reads]
    c_all = [r["content"] for r in reads if r["content"] is not None]
    pair_agg = {}
    for r in reads:
        for k, v in r["pairwise_structural"].items():
            pair_agg.setdefault(k, []).append(v)
    pair_mean = {k: sum(v) / len(v) for k, v in pair_agg.items()}

    print("\n  pscale │ structural │ content │ co-occupied / union")
    print("  ───────┼────────────┼─────────┼────────────────────")
    for r in reads:
        cs = "  —  " if r["content"] is None else "%.2f" % r["content"]
        print("    %+d   │    %.2f    │  %s  │   %d / %d"
              % (r["pscale"], r["structural"], cs, r["co_occupied"], r["union"]))

    s_mean = sum(s_all) / len(s_all) if s_all else 0.0
    c_mean = sum(c_all) / len(c_all) if c_all else None
    name, why = verdict(s_mean, c_mean, pair_mean)
    print("\n  structural resonance (mean): %.2f" % s_mean)
    print("  content overlap (mean):      %s"
          % ("—" if c_mean is None else "%.2f" % c_mean))
    print("  pairwise structural:         "
          + "  ".join("%s %.2f" % (k, v) for k, v in sorted(pair_mean.items())))
    print("\n  ▶ %s — %s" % (name.upper(), why))

    shown = [(r["pscale"], a, t) for r in reads for a, t in r["diverging"]]
    if shown:
        print("\n  co-occupied but distinct (the offset — same address, distinct voice):")
        for P, addr, texts in shown[:6]:
            print("    pscale %+d, %s:" % (P, addr))
            for n, t in texts.items():
                print("      %s  %s" % (n, t[:88] + ("…" if len(t) > 88 else "")))

    if do_judge:
        print("\n  ── semantic judge (the similarity function as an LLM read) ──")
        print("  " + judge(triad, reads).replace("\n", "\n  "))


def when(run_root, now=None):
    """The WHEN-axis (doc 3 C3): each agent's periodic concerns — period, phase,
    offset φ, effective θ, state — plus, per concern, the Kuramoto order parameter
    r and pairwise offsets over the coupled (effective) phases. The complement to
    the fold's WHAT-axis. Reuses the kernel's own arithmetic so reading and prune
    agree. r→0 with offsets near 1/3,2/3 is the splay; r→1 is unison/collapse."""
    import time
    now = time.time() if now is None else now
    cad = load_triad(run_root, "cadence")
    lt = load_triad(run_root, "last-touched")
    phi = load_triad(run_root, "phi")
    paths = sorted({p for c in cad.values() for p in kernel._cadence_paths(c)})
    if not paths:
        print("no periodic concern authored under %s — every concern is aperiodic." % run_root)
        return
    coupled = any(kernel._at(phi.get(a, {}), p) not in (None, "") for p in paths for a in cad)
    print("when — phase state across %s, now=%d (ripeness ≥ %.1f%s)"
          % ("·".join(sorted(cad)), int(now), kernel.RIPENESS, ", coupled" if coupled else ""))
    print("\n  concern │ agent │ period │ phase │   φ   │ eff-θ │ state")
    print("  ────────┼───────┼────────┼───────┼───────┼───────┼────────")
    eff = {}
    for path in paths:
        eff[path] = {}
        for a in sorted(cad):
            period = kernel._at(cad[a], path)
            if period is None:
                continue
            ph = kernel._phase(period, kernel._at(lt.get(a, {}), path), now)
            fraw = kernel._at(phi.get(a, {}), path)
            fv = float(fraw) if fraw not in (None, "") else 0.0
            eff[path][a] = kernel._theta(ph + fv)
            phs = "  ∞ " if ph == float("inf") else "%.2f" % ph
            state = "ripe" if (ph + fv) >= kernel.RIPENESS else "dormant"
            print("  %-7s │   %s   │ %6s │ %5s │ %+5.2f │ %.3f │ %s"
                  % (".".join(path), a, period, phs, fv, eff[path][a], state))
    print("\n  coupling readout (effective θ): order parameter r + pairwise offsets")
    for path in paths:
        ths = eff[path]
        if len(ths) < 2:
            continue
        r = kernel.order_parameter(list(ths.values()))
        ags = sorted(ths)
        offs = "  ".join("%s%s %.2f" % (ags[i], ags[j], (ths[ags[i]] - ths[ags[j]]) % 1)
                         for i in range(len(ags)) for j in range(i + 1, len(ags)))
        read = "splay" if r < 0.4 else "unison/collapse" if r > 0.85 else "partial"
        print("    %-7s  r=%.3f   [%s]   -> %s" % (".".join(path), r, offs, read))


if __name__ == "__main__":
    argv = sys.argv[1:]
    do_judge = "--judge" in argv
    do_when = "--when" in argv
    argv = [a for a in argv if a not in ("--judge", "--when")]
    now = None
    if "--now" in argv:
        i = argv.index("--now")
        now = float(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    block = "purpose"
    if "--block" in argv:
        i = argv.index("--block")
        block = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if not argv:
        sys.exit("usage: resonance.py <run-root> [--block purpose] [--judge] [--when [--now N]]")
    if do_when:
        when(argv[0], now=now)
    else:
        resonate(argv[0], block_name=block, do_judge=do_judge)
