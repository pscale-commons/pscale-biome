"""scene -- the Track B RPG beat-engine (biome-native; authority DEFERRED).

The loop, per beat at a location, all over plain 0-9 spark blocks in a store:

  perceive(handle) -> the bespoke 2nd-person EXPERIENCE (soft; a player or a character-LLM
                      reads exactly this -- the seam where HITL == NHITL).
  submit(handle)   -> the character's 1st-person INTENTION, written into the WINDOW (liquid);
                      returns the pool (the probe is in the primitive).            [CHARACTER act]
  resolve()        -> the DESIGNER RULE applied to the window -> a MECHANICAL verdict, woven from
                      the actual submissions -> committed as a SOLID beat into the scene (T
                      advances) -> the window clears.                              [AUTHOR act, mechanical]
  echo(handle)     -> each character's 1st-person narration of the one committed beat (personal).

Outcome shared (the mechanical verdict -> coherence, no central LLM); narrative personal (echoes
-> the magic trick). submit = character/liquid; resolve+commit = author/solid. Authority gating
(who may write which axis) is DEFERRED to the passphrase membrane; here writes are open.

Reuses the Upperton S/T/I triad as spark blocks and fold._call as the one LLM seam.

  python3 scene.py            # seed a bench store from the Upperton files and play 2 NHITL beats
"""
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spark"))
sys.path.insert(0, HERE)
import spark
import fold

DIGITS = "123456789"
TAPROOM = "1121"                       # the Millstone taproom -- the dice-game scene
WORLD_DEFAULT = os.path.expanduser("~/Downloads/upperton-world")
STORE_DEFAULT = os.path.expanduser("~/Desktop/biome-runs/trackB-rpg")


# --- store + block helpers ----------------------------------------------------

def _b(store, name):
    p = os.path.join(store, name + ".json")
    return spark.load(p) if os.path.isfile(p) else None


def _save(store, name, block):
    spark.save(os.path.join(store, name + ".json"), block)


def leaves(node):
    if node is None:
        return []
    if isinstance(node, str):
        return [node]
    return [x for d in "0123456789" if d in node for x in leaves(node[d])]


def _where(addr):
    return [c for c in str(addr) if c.isdigit()]


def _next(block):
    for d in DIGITS:
        if d not in block:
            return d
    return "9"


def _latest(block):
    ds = [d for d in DIGITS if d in (block or {})]
    return block[ds[-1]] if ds else None


def _descend(block, where):
    return spark.descend(block, where) if isinstance(block, dict) else None


# --- character stats parsed from the shell (author-data: shell.2 = nomad stats) ----

def parse_stats(shell):
    n = (shell or {}).get("2") or {}
    out = {}
    for d in DIGITS:
        v = n.get(d)
        if isinstance(v, str) and ":" in v:
            k, val = v.split(":", 1)
            try:
                out[k.strip()] = int(val)
            except ValueError:
                pass
    return out


# --- reads: the S/T/I triad + the live scene ----------------------------------

def read_S(store, where):
    return " | ".join(leaves(_descend(_b(store, "upperton-spatial"), where)))


def read_T(store, where):
    back = " ".join(l for l in leaves(_descend(_b(store, "upperton-temporal"), where)) if "gone" not in l)
    latest = _latest(_b(store, "scene"))
    return back + (("  || just now: " + latest) if isinstance(latest, str) else "")


def read_I(store, where, sp):
    idb = _b(store, "upperton-identity")
    return _descend(idb, where + [sp]), _descend(idb, where + ["0"])


# --- the window (liquid fan) --------------------------------------------------

def submissions(store):
    w = _b(store, "window") or {}
    return [(w[d].get("0"), w[d].get("1")) for d in DIGITS if isinstance(w.get(d), dict)]


def submit_write(store, handle, intention):
    w = _b(store, "window") or {"0": "the liquid window at the taproom"}
    w[_next(w)] = {"0": handle, "1": intention}
    _save(store, "window", w)


def clear_window(store):
    _save(store, "window", {"0": "the liquid window at the taproom"})


# --- the loop -----------------------------------------------------------------

def perceive(store, where, handle, char):
    i_self, i_room = read_I(store, where, char["sp"])
    others = "\n".join("    - %s: %s" % (h, t) for h, t in submissions(store) if h != handle) or "    (nothing yet)"
    prompt = ("Narrate what THIS character perceives now -- second person ('you'), 2-3 sentences, only "
              "what they could sense; a covert act by another may escape them. Do not decide what they do.\n"
              "  place: %s\n  happening: %s\n  your standpoint: %s\n  the room: %s\n"
              "  what you can see others doing:\n%s"
              % (read_S(store, where), read_T(store, where), i_self, i_room, others))
    return fold._call(prompt, 200)


def submit(store, where, handle, char, experience):
    prompt = ("You ARE the %s. You experience:\n  %s\nWho you are -- %s\n"
              "SUBMIT your intention: the move you mean to make (you are also feeling out the table). "
              "First person ('I ...'), ONE concrete action." % (handle, experience, char["purpose"]))
    move = fold._call(prompt, 140)
    submit_write(store, handle, move)
    return move, submissions(store)


def _roll(spec):
    """Roll a dice spec like '1d10' -> (total, 'r1+r2'); no/blank spec -> (0, '')."""
    m = re.match(r"\s*(\d+)\s*[dD]\s*(\d+)", spec or "")
    if not m:
        return 0, ""
    rolls = [random.randint(1, int(m.group(2))) for _ in range(int(m.group(1)))]
    return sum(rolls), "+".join(str(r) for r in rolls)


def _dice_spec(store, rules):
    """The ruleset's dice, read from its resolution node (e.g. nomad.2 carries 'dice: 1d10').
    This is the engine EXECUTING the block -- edit the block (Designer face), change the roll."""
    rb = _b(store, rules) if rules else None
    node = spark.descend(rb, ["2"]) if isinstance(rb, dict) else None
    text = " ".join(leaves(node)) if node is not None else ""
    m = re.search(r"\d+\s*[dD]\s*\d+", text)
    return m.group(0) if m else None


def resolve(store, where, chars, rules="nomad"):
    """AUTHOR commit by the DESIGNER RULE -- mechanical (no LLM), the dice READ from the ruleset.
    Contesters vie by (stat-sum + a dice roll); ambient moves ([] stats) land. The roll is cast
    ONCE here and committed into the scene, so the verdict is settled for all, never re-rolled."""
    subs = submissions(store)
    if not subs:
        return None, {}
    contesters = [(h, m) for h, m in subs if chars[h]["contest"]]
    ambient = [(h, m) for h, m in subs if not chars[h]["contest"]]
    dice = _dice_spec(store, rules)

    totals, note = {}, {}
    for h, _ in contesters:
        base = sum(chars[h]["stats"].get(k, 0) for k in chars[h]["contest"])
        r, rs = _roll(dice)
        totals[h] = base + r
        note[h] = ("%d+%s=%d" % (base, rs, base + r)) if dice else str(base)

    parts = []
    if len(contesters) >= 2:
        ranked = sorted(contesters, key=lambda s: totals[s[0]], reverse=True)
        parts.append("%s prevails -- %s" % (ranked[0][0], ranked[0][1]))
        parts += ["%s's move is interrupted (%s)" % (h, m) for h, m in ranked[1:]]
    elif len(contesters) == 1:
        parts.append("%s acts unopposed -- %s" % contesters[0])
    parts += ["%s: %s" % (h, m) for h, m in ambient]
    if note:
        parts.append("[" + ", ".join("%s %s" % (h, note[h]) for h in note) + "]")
    verdict = "  |  ".join(parts)
    sc = _b(store, "scene") or {"0": "resolved beats at the taproom"}
    sc[_next(sc)] = verdict
    _save(store, "scene", sc)
    clear_window(store)
    return verdict, totals


def echo(store, where, handle, char, verdict):
    prompt = ("You ARE the %s. What HAPPENED this beat (the settled outcome):\n  %s\n"
              "Narrate it as YOU live it -- first person, 1-2 sentences, aperture-bound (you know your own "
              "part; another's intent you read only as far as you could perceive)." % (handle, verdict))
    return fold._call(prompt, 160)


# --- seed a bench store from the Upperton files -------------------------------

def seed(world=WORLD_DEFAULT, store=STORE_DEFAULT):
    os.makedirs(store, exist_ok=True)
    for nm in ("upperton-spatial", "upperton-temporal", "upperton-identity"):
        _save(store, nm, spark.load(os.path.join(world, nm + ".json")))
    shells = {
        "merchant": {"0": "The visiting merchant -- a southern trader far from home; tonight the dice run your way.",
                     "1": "purpose: palm the bent coin off the table and carry your luck south",
                     "2": {"0": "nomad stats", "1": "sleight:5", "2": "caution:3", "3": "greed:7"}},
        "watcher": {"0": "The hooded watcher -- a local who works the inn's crowds.",
                    "1": "purpose: stop the merchant's hand and keep the table's coin in play for your own lift",
                    "2": {"0": "nomad stats", "1": "stealth:8", "2": "nerve:6", "3": "patience:7"}},
        "keeper": {"0": "The keeper -- a fat night's takings if the dice don't turn to knives.",
                   "1": "purpose: keep the night profitable and the peace; watch the merchant's purse, the hooded one, and your own bent-coin lure",
                   "2": {"0": "nomad stats", "1": "sharp:6", "2": "authority:5"}},
        "regular": {"0": "The old regular -- your bench, your name once carved in the oak and scratched out.",
                    "1": "purpose: hold your bench and your peace, and watch the road-folk's game play out as you know it will",
                    "2": {"0": "nomad stats", "1": "wit:5", "2": "patience:6"}},
    }
    for h, b in shells.items():
        _save(store, "shell-" + h, b)
    _save(store, "rules", {"0": "Contested covert action at the table -- a NOMAD reckoning.",
                           "1": "each actor scores their relevant stats; higher prevails; the loser's move is "
                                "interrupted; a tie favours the defender."})
    clear_window(store)
    _save(store, "scene", {"0": "resolved beats at the taproom"})
    return store


# --- the NHITL runner ---------------------------------------------------------

# contest stats per character; [] = AMBIENT (a free move that always lands -- social texture)
CONTEST = {"merchant": ["sleight", "caution"], "watcher": ["stealth", "nerve"],
           "keeper": [], "regular": []}
SPOT = {"merchant": "3", "watcher": "4", "keeper": "2", "regular": "1"}


def load_chars(store):
    chars = {}
    for h in CONTEST:
        sh = _b(store, "shell-" + h)
        chars[h] = {"sp": SPOT[h], "purpose": sh["1"], "stats": parse_stats(sh), "contest": CONTEST[h]}
    return chars


def run(store, beats=2, order=("regular", "keeper", "merchant", "watcher")):
    where = _where(TAPROOM)
    chars = load_chars(store)
    print("=" * 84)
    print("TRACK B -- NHITL RPG, the Millstone taproom (Upperton)  | store: %s" % store)
    print("characters: %s  | beats: %d  | nothing computed centrally but the verdict" % (", ".join(order), beats))
    for beat in range(1, beats + 1):
        print("\n" + "-" * 36 + "  BEAT %d  " % beat + "-" * 36)
        for h in order:
            exp = perceive(store, where, h, chars[h])
            mv, _ = submit(store, where, h, chars[h], exp)
            print("\n[%s] sees   : %s" % (h, exp))
            print("[%s] submits: %s" % (h, mv))
        verdict, scores = resolve(store, where, chars)
        print("\n  RESOLVE (designer rule, mechanical): %s"
              % "  ".join("%s=%d" % (h, s) for h, s in scores.items()))
        print("  SOLID  : %s" % verdict)
        for h in order:
            print("  [%s] echo: %s" % (h, echo(store, where, h, chars[h], verdict)))
    print("\n" + "=" * 84)
    print("Each beat: characters SUBMIT (liquid) -> designer rule COMMITS one solid -> echoes (personal).")
    print("Swap either seat for a human reading the same 'sees' and typing the submit -> HITL, unchanged.")
    print("=" * 84)


if __name__ == "__main__":
    s = seed()
    run(s, beats=2)
