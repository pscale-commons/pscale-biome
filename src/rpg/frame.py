"""frame.py -- the RPG frame-composer.

Binds one character's window from the shared world (S/T/I sibling blocks) and a
reused agent shell, apertured by face (CADO) and tier (SMH). A window is
shell-addresses (+) world-fold-addresses:

    HERE   -- space at the bound walk (the descent + the room's contents)
    NOW    -- time at the same walk
    WHO    -- identity at the X-1 pick (the standpoint) + the collective head
    SELF   -- the shell (purpose / conditions / history)

The fold is by pscale, never by walk-depth (sti-function): the three blocks are
read at the same walk; below the populated room they fork (space->objects,
time->seconds, identity->persons) and that fork is the fold doing its work.

Character face + medium tier is the honest-newcomer aperture: the character sees
their own standpoint and the collective head, NEVER the other whos' interiors --
so the frame needs no negative instructions. The hidden interiors are the
medium-gate's material (hidden_depth), not the character's.
"""
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (_HERE, os.path.join(_HERE, "..", "spark"), os.path.join(_HERE, "spark")):
    if os.path.exists(os.path.join(_p, "spark.py")):
        sys.path.insert(0, _p)
        break
import spark

WORLD = {"space": "upperton-space", "time": "upperton-time", "identity": "upperton-identity"}


def load_world(world_dir):
    return {k: spark.load(os.path.join(world_dir, nm + ".json")) for k, nm in WORLD.items()}


def load_shell(char_dir):
    shell = {}
    for comp in ("purpose", "history", "conditions", "surface", "bind"):
        p = os.path.join(char_dir, comp + ".json")
        if os.path.exists(p):
            shell[comp] = spark.load(p)
    return shell


def _voice(block, walk):
    return spark.voice(spark.descend(block, walk))


def _descent(block, walk):
    """Broad->specific voicings down the walk (the telescope: town to room)."""
    out = []
    for i in range(1, len(walk) + 1):
        v = _voice(block, walk[:i])
        if v:
            out.append(v)
    return out


def _contents(block, walk, maxdepth=3):
    """The voicings beneath the bound node -- the room's features, its objects."""
    node = spark.descend(block, walk)
    out = []

    def rec(n, depth):
        if not isinstance(n, dict) or depth > maxdepth:
            return
        for d in spark.DIGITS:
            if d in n:
                ch = n[d]
                v = ch if isinstance(ch, str) else spark.voice(ch)
                if v:
                    out.append(v)
                if isinstance(ch, dict):
                    rec(ch, depth + 1)

    rec(node, 1)
    return out


def _shell_line(comp, block):
    head = spark.voice(block) or ""
    branches = []
    for d in spark.DIGITS:
        if isinstance(block, dict) and d in block:
            v = spark.voice(block[d]) if isinstance(block[d], dict) else block[d]
            if v:
                branches.append(v)
    body = head + ((" -- " + " / ".join(branches)) if branches else "")
    return comp.capitalize() + ": " + body


def here_walk(shell):
    return shell["bind"]["2"].split(",")


def bind_window(shell, world, face="character", tier="medium", recent=None):
    """Compose the bound window. Returns {text, parts}. `recent` is the recent
    deposited scenes (the play's own T); once play has begun they replace the
    seed's scripted micro-beats as the NOW's events, so the world changes."""
    here, who = here_walk(shell), shell["bind"]["3"]
    S, T, I = world["space"], world["time"], world["identity"]

    here_lines = _descent(S, here) + _contents(S, here)
    now_lines = _descent(T, here) + (list(recent) if recent else _contents(T, here))
    standpoint = _voice(I, here + [who])
    collective = _voice(I, here)
    self_lines = [_shell_line(c, shell[c]) for c in ("purpose", "conditions", "history") if c in shell]

    def bullets(xs):
        return "\n".join("- " + x for x in xs)

    text = ("HERE -- space\n" + bullets(here_lines) +
            "\n\nNOW -- time\n" + bullets(now_lines) +
            "\n\nWHO -- your standpoint\n- " + (standpoint or "(none)") +
            "\n\nWHO -- the room, as it collectively feels\n- " + (collective or "(none)") +
            "\n\nSELF -- your shell\n" + "\n".join(self_lines))
    parts = {"here": here_lines, "now": now_lines, "standpoint": standpoint,
             "collective": collective, "self": self_lines, "face": face, "tier": tier}
    return {"text": text, "parts": parts}


def hidden_depth(shell, world):
    """The negative-I material the aperture excludes -- the OTHER whos present
    (the gate judges an act against these), plus the deep object truth in reach."""
    here, who = here_walk(shell), shell["bind"]["3"]
    I, S = world["identity"], world["space"]
    place = spark.descend(I, here)
    whos = []
    if isinstance(place, dict):
        for d in spark.DIGITS:
            if d in place and d != who:
                v = place[d] if isinstance(place[d], str) else spark.voice(place[d])
                if v:
                    whos.append(v)
    return {"whos": whos, "objects": _contents(S, here)}
