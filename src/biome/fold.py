"""fold -- the FRAME layer over the real-world patchwork (the engagement / S*T*I fold).

The substrate stays coordinate-pure: `locate.walk(address)` reads a block at a
coordinate and knows nothing of who is reading or when. This module is the layer
above it -- the reader's aperture -- and it is where identity and time live:

  frame(where, when, who)
      opens a window and binds three registers AT THE FLOOR into one moment:
        S  the public place      (the shared spine -- the view-from-nowhere, 1^0)
        T  its now               (the place's rhythm + the actual now, bound live)
        I  the who's account     (this reader's own voicing of the place)

The corrected layering (ruled with David, 2026-06-21): `who` and `when` are NOT
parameters of the walk -- the walk is coordinate-only. They are the reader's
FRAME. `who` selects whose account to fold with the place; `when` selects the T
read. A wall-clock timestamp is never the lived-moment T; it is either valid-time
(which version) or provenance on a grounded mark (see PRESENCE below) -- and the
project already settled that "when" enters as a parallel block, not a field
(the cadence / last-touched work).

PERSONAL = the I-register, in the inhabitant's OWN SHELL. Each person keeps their
rendition in their shell surface (block surface-<handle>) at the SAME absolute spindle
as S -- the SHELL stratum (sovereign, readable by all, writable only by its owner), not
the WORLD. Reading I-at-X is reading their surface at X; VOICING (the write, `voice()`)
is a spark point-write into surface-<handle> at X -- already the spark primitive, gated
at the door by the identity membrane (you may write only your own surface). So renditions
CORRELATE across shells at one address, and the fan/social-fold reads across them. A
written rendition is a SOLID (settled), the counterpart to the relay's vapour (presence).
(Converges with the interface session's agency-blocks -- personal renditions in shells,
one spindle, folded to social -- which adopts this fan-and-fold; that session supplies the
VLS over it: "the fold has no interface" is the seam between us.)

SOCIAL = the fold of the I-fan. Gather every handle's account at one address (the
fan) and synthesise a collective voicing. Per sti-function branch 8 the synthesis
is reader-side ("no central resolver; each reader's LLM produces its own"), so it
is DERIVED, never stored as truth -- the same discipline as the gazetteer and the
derived lighthouse. The shared map at the top is 1^0; this social synthesis at the
floor is 1^9; folding the fan can in turn regenerate the map's public voicing.

PRESENCE (the actual / projected sign). A presence is a frame's `who` marked at a
floor address. Whether it MIRRORS a real-world fact or PROJECTS onto the map is a
sign the reader applies -- orthogonal to real/fantasy, and like it, never stored
as a boolean. What the substrate carries is GROUNDING (provenance: who attested,
how, valid-when), kept frame-side beside the blocks (like the gazetteer), not in
them. grounded -> mirror (usable for real meetings, supply chains); ungrounded ->
projection (a window onto the map). The reader filters by it.

The SAME sign governs T: when='now' grounds the floor to the actual clock (mirror-T);
any other when is an imagined time (projection-T). So a moment COORDINATES -- a real
meeting, a supply hop -- only when it mirrors reality on EVERY axis: S mapped, T the
actual now, I grounded. `frame` reports this as `coordinatable`. That is the real
world's gift over a fantasy: it can be checked against the thing it mirrors.

  python3 fold.py            # the worked demonstration (seeds fixtures, runs the fold)
  python3 fold.py seed       # (re)write the demo's per-handle identity fixtures
"""
import os
import re
import sys
import json
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spark"))
sys.path.insert(0, HERE)
import spark
import locate

ROOT_PSCALE = locate.ROOT_PSCALE                       # Sol, +11
EARTH = locate.EARTH                                    # the shared S spine (read-only here)
SHELLS = os.environ.get("BIOME_SHELLS") or os.path.join(HERE, "world", "shells")  # I-register: SHELL surfaces (surface-<handle>) — the inhabitant's stratum
TIME = os.environ.get("BIOME_TIME") or os.path.join(HERE, "world", "time")   # the T spine (place rhythm)
# grounding lives BESIDE the blocks, never inside them -- a frame-side index, like the gazetteer
ATTEST = os.environ.get("BIOME_ATTEST") or os.path.join(os.path.dirname(SHELLS), "identity-attestations.json")


# --- small helpers ----------------------------------------------------------

def _digits(address):
    return locate._digits(address)


def _nest_into(root, spindle, value):
    """Set value at the digit path `spindle` in dict `root`, creating dicts."""
    node = root
    for d in spindle[:-1]:
        node = node.setdefault(d, {})
    node[spindle[-1]] = value
    return root


def _key():
    k = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if k:
        return k
    p = os.path.expanduser("~/.config/mobius/anthropic-key")
    if os.path.isfile(p):
        t = open(p, encoding="utf-8").read().strip()
        return t.split("=", 1)[1].strip().strip('"').strip("'") if t.startswith("ANTHROPIC") else t
    return ""


def _call(prompt, max_tokens=400):
    """The soft-LLM synthesis (sti-function branch 4 / 8). No key -> None, and the
    caller emits the prompt for a reading LLM to fold by hand."""
    import urllib.request
    import urllib.error
    key = _key()
    if not key:
        return None
    body = json.dumps({"model": os.environ.get("FOLD_MODEL", "claude-sonnet-4-6"),
                       "max_tokens": max_tokens,
                       "messages": [{"role": "user", "content": prompt}]}).encode("utf-8")
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, method="POST",
        headers={"content-type": "application/json", "x-api-key": key,
                 "anthropic-version": "2023-06-01"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.loads(r.read().decode("utf-8"))
        return "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text").strip()
    except Exception as e:
        return "(synthesis call failed: %s)" % e


# --- the I-register: per-handle SHELL surfaces (surface-<handle>) ------------
# A personal rendition lives in the inhabitant's OWN shell surface (the SHELL stratum,
# not WORLD): sovereign, readable by all, writable only by its owner. Addressed by the
# SAME absolute spindle as S, so renditions correlate across shells at an address --
# which is what the fan/social-fold reads, and what `voice()` writes.

def personal_loader(directory=SHELLS):
    """load(handle) -> that handle's shell surface (block surface-<handle>), or None.
    Same shape as locate.fs_loader / federate.loader -- here the axis is identity."""
    cache = {}

    def load(handle):
        if handle not in cache:
            p = os.path.join(directory, "surface-" + handle + ".json")
            cache[handle] = spark.load(p) if os.path.isfile(p) else None
        return cache[handle]
    return load


def account_at(block, spindle):
    """A handle's voicing at an absolute address in their own block, or None."""
    if block is None:
        return None
    node = spark.descend(block, _digits(spindle))
    if node is None:
        return None
    return node if isinstance(node, str) else spark.voice(node)


def handles(directory=SHELLS):
    if not os.path.isdir(directory):
        return []
    return sorted(f[len("surface-"):-5] for f in os.listdir(directory)
                  if f.startswith("surface-") and f.endswith(".json"))


# --- grounding (frame-side; the reader applies the sign) --------------------

def attestations(path=ATTEST):
    return spark.load(path) if os.path.isfile(path) else {}


def grounding(who, address, att=None):
    att = attestations() if att is None else att
    return (att.get(who) or {}).get("".join(_digits(address)))


def sign(ground):
    """The reader's sign -- never a stored field. Grounded -> mirror; bare -> projection."""
    return "mirror" if ground else "projection"


# --- resolving `where` ------------------------------------------------------

def _where(where, earth_loader, root=None):
    """A place name OR an absolute address -> {address, spindle, pscale, name}.
    `root` is the cosmology root to walk from (None -> the spine's default). A served
    biome SENSES this from its own store (serve `_roots()`), so frame is world-generic
    -- the engagement layer over ANY island's S-spine, not bound to the real world."""
    root = root or locate.ROOT
    s = str(where).strip()
    if s and all(c in "0123456789.," for c in s):              # an absolute address
        spindle = _digits(s)
    else:                                                       # a name -> the gazetteer
        import grow
        hits = grow.lookup(where)
        if not hits:
            raise ValueError("where=%r is neither an address nor a mapped place" % where)
        spindle = [d for d in hits[0]["spindle"].split(",") if d]
    res = locate.walk(spindle, earth_loader, root=root)
    return {"address": locate.to_address(spindle), "spindle": spindle,
            "pscale": ROOT_PSCALE - len(spindle),
            "name": (res.get("voice") or "").split(" -- ")[0] or None, "walk": res}


# --- the three register reads -----------------------------------------------

def read_S(where, earth_loader):
    """S -- the public place: the shared spine's voicing at the address (1^0)."""
    w = where["walk"]
    return {"pscale": where["pscale"],
            "text": w.get("voice") if w.get("ok") else None,
            "status": "voiced" if (w.get("ok") and w.get("voice")) else "unmapped"}


def _now(clock=None):
    """The actual moment, from the system clock -- the real-world floor of T (the
    advantage Upperton never had). Northern-hemisphere seasons; that season turns on
    the place's hemisphere is a real T<-S coupling, kept simple here."""
    t = clock or datetime.datetime.now()
    season = ("winter", "winter", "spring", "spring", "spring", "summer",
              "summer", "summer", "autumn", "autumn", "autumn", "winter")[t.month - 1]
    daypart = ("night" if t.hour < 6 else "morning" if t.hour < 12
               else "afternoon" if t.hour < 18 else "evening")
    return t, season, daypart


def time_block(directory=TIME):
    """The shared T-spine (place rhythm), addressed by the SAME spindle as S."""
    p = os.path.join(directory, "earth-time.json")
    return spark.load(p) if os.path.isfile(p) else None


def read_T(where, when, tblock=None):
    """T -- the place's now, read at the SAME spindle as S (correspond by pscale).
    The T-spine voices a place's RHYTHM (season-scale); the floor's NOW is bound
    live: when='now' grounds it to the actual clock -> MIRROR-T; any other when is
    an imagined time -> PROJECTION-T. So the actual/projected sign governs T exactly
    as it governs presence (I). `when` selects the time; it is never a stored field."""
    tblock = time_block() if tblock is None else tblock
    rhythm = None
    if tblock is not None:
        node = spark.descend(tblock, _digits(where["spindle"]))
        if node is not None:
            rhythm = node if isinstance(node, str) else spark.voice(node)
    if str(when) == "now":
        t, season, daypart = _now()
        nowtext = "%s %s, %s (the actual now)" % (t.strftime("%A"), daypart, t.strftime("%d %B %Y"))
        sign, ground = "mirror", t.isoformat(timespec="minutes")
    else:
        nowtext, sign, ground = "(imagined: %s)" % when, "projection", None
    return {"pscale": where["pscale"], "when": when, "sign": sign, "grounding": ground,
            "status": "voiced", "text": (rhythm + " | " + nowtext) if rhythm else nowtext}


def read_I(where, who, ploader=None):
    """I -- the who's own account at the address (their personal version of the block)."""
    ploader = ploader or personal_loader()
    text = account_at(ploader(who), where["spindle"])
    return {"pscale": where["pscale"], "who": who, "text": text,
            "status": "voiced" if text else "silent"}


# --- the write: voice your rendition into your own shell (the SOLID) ---------

def voice(where, who, account, earth_loader=None, shells_dir=SHELLS, root=None):
    """An inhabitant VOICES their rendition of a place -- the I-axis write. It is already
    the spark primitive: a point-write of `account` into the writer's OWN shell surface
    (surface-<who>) at the place's absolute spindle. At the door this is exactly
    spark(block='surface-<who>', number=<address>, content=account, handle=<who>), gated
    by the identity membrane (you may write only your own surface, reads stay free); here
    we run the same write on the shell block directly. A rendition so written is a SOLID
    -- it settles into the fan, and the next social_fold folds it. Returns where it landed."""
    earth_loader = earth_loader or locate.fs_loader()
    w = _where(where, earth_loader, root)
    os.makedirs(shells_dir, exist_ok=True)
    path = os.path.join(shells_dir, "surface-" + who + ".json")
    block = spark.load(path) if os.path.isfile(path) else {}
    spark.spark(block, locate.to_address(w["spindle"]), content=account)   # point-write at the spindle
    spark.save(path, block)
    return {"who": who, "block": "surface-" + who, "wrote": account,
            "where": {k: w[k] for k in ("address", "pscale", "name")}}


# --- the frame: bind S, T, I into one moment --------------------------------

MOMENT_PROMPT = """You are {who}, at this place. Speak your perceived moment in one or
two sentences, first person, using ONLY what is given -- nothing to add, nothing to ignore.

  the place (S): {s}
  its now  (T):  {t}
  your account (I): {i}"""


def frame(where, when, who, earth_loader=None, ploader=None, tblock=None, root=None, synth=True):
    """Open the reader's aperture (where / when / who) and bind the three registers
    at the floor into a moment. who and when live HERE, never on the walk."""
    earth_loader = earth_loader or locate.fs_loader()
    ploader = ploader or personal_loader()
    tblock = time_block() if tblock is None else tblock
    w = _where(where, earth_loader, root)
    s, t, i = read_S(w, earth_loader), read_T(w, when, tblock), read_I(w, who, ploader)
    g = grounding(who, w["spindle"])
    # the actual/projected sign across ALL THREE axes -- a moment is coordinatable (a
    # real meeting, a supply hop) only when it MIRRORS reality on each: the place is
    # mapped (S), the time is the actual now (T), the presence is grounded (I).
    mirror = {"S": s["status"] == "voiced", "T": t["sign"] == "mirror", "I": sign(g) == "mirror"}
    out = {"where": {k: w[k] for k in ("address", "pscale", "name")},
           "when": when, "who": who, "S": s, "T": t, "I": i,
           "presence": {"grounding": g, "sign": sign(g)},
           "mirror": mirror, "coordinatable": all(mirror.values())}
    prompt = MOMENT_PROMPT.format(who=who, s=s["text"] or "(unmapped here)",
                                  t=t["text"], i=i["text"] or "(you have not voiced this place)")
    out["moment"] = _call(prompt) if synth else None
    out["moment_prompt"] = prompt
    return out


# --- the fan and the social fold (1^0 -> 1^9) -------------------------------

def fan(where, earth_loader=None, ploader=None, att=None, root=None):
    """Every handle with an account at this address -- the I-fan. Each entry carries
    its grounding and the sign the reader would apply."""
    earth_loader = earth_loader or locate.fs_loader()
    ploader = ploader or personal_loader()
    att = attestations() if att is None else att
    w = _where(where, earth_loader, root)
    out = []
    for h in handles():
        text = account_at(ploader(h), w["spindle"])
        if text is None:
            continue
        g = grounding(h, w["spindle"], att)
        out.append({"who": h, "account": text, "grounding": g, "sign": sign(g)})
    return {"where": {k: w[k] for k in ("address", "pscale", "name")},
            "public": read_S(w, earth_loader)["text"], "fan": out}


SOCIAL_PROMPT = """These are the accounts people give of the same place. Synthesise the
collective sense of it -- what this place is to those who know it -- in one or two
sentences, using ONLY what they give.

  the place (public): {public}
{accounts}"""


def social_fold(where, mirror_only=False, synth=True, root=None, **kw):
    """Fold the I-fan into a collective voicing (the 1^9). mirror_only drops
    projections, so a coordination tool reads only grounded presence."""
    f = fan(where, root=root, **kw)
    members = [e for e in f["fan"] if (e["sign"] == "mirror" or not mirror_only)]
    lines = "\n".join("  - %s (%s): %s" % (e["who"], e["sign"], e["account"]) for e in members)
    prompt = SOCIAL_PROMPT.format(public=f["public"] or "(unmapped)", accounts=lines or "  (no accounts)")
    return {"where": f["where"], "public": f["public"], "members": members,
            "mirror_only": mirror_only,
            "synthesis": (_call(prompt) if (synth and members) else None),
            "synthesis_prompt": prompt}


# --- seed the demo's per-handle identity fixtures ---------------------------

CEIDIO_ROOM = "3,1,1,1,0,1,0,0,1,1,1"          # confirmed by locate.py: pscale 0, the room
CEIDIO_P2 = "3,1,1,1,0,1,0,0,1"                 # the village node, pscale +2 (where rhythm lives)
NY_DELI = "3,4,1,1,1,1,1,1,1,1,1"               # North America (Earth digit 4), unmapped in S


def seed():
    """Write the per-handle SHELL surfaces (via voice() -- the same write the door runs)
    + the grounding index + the T-spine. Idempotent; local demo fixtures (off any island)."""
    os.makedirs(SHELLS, exist_ok=True)
    renditions = {
        "david": [(CEIDIO_ROOM,
                   "the room with the bad radiator and the window onto the yard -- "
                   "the stone holds the heat; I write from the table by the window. -- david")],
        "asha": [(CEIDIO_ROOM,
                  "the back room, cold of a morning, the good light at noon, and the "
                  "shelf of sea-glass by the sill. -- asha")],
        "happyseaurchin": [
            (CEIDIO_ROOM,
             "the idea of the room from afar -- the radiator's knock half-remembered, "
             "the yard I picture but cannot see. -- happyseaurchin"),
            (NY_DELI,
             "a corner deli off a wide avenue, coffee and the door's bell, where I sit "
             "to talk with others a world away from my body. -- happyseaurchin")],
    }
    for handle, entries in renditions.items():
        for addr, account in entries:
            voice(addr, handle, account)          # dogfood the write: every rendition is a voice()
    att = {
        "david": {"".join(_digits(CEIDIO_ROOM)):
                  {"by": "check-in", "method": "device-attested", "valid": "2026-06-21"}},
        "asha": {"".join(_digits(CEIDIO_ROOM)):
                 {"by": "check-in", "method": "host-vouched", "valid": "2026-06-21"}},
        "happyseaurchin": {},          # no grounding anywhere -> every presence is a projection
    }
    spark.save(ATTEST, att)
    # the T-spine: a place's rhythm at the SAME spindle as S (correspond by pscale);
    # the floor's NOW is bound live at read, not stored.
    os.makedirs(TIME, exist_ok=True)
    tb = {}
    _nest_into(tb, _digits(CEIDIO_P2), {"0": "the farming year on the Llyn -- lambing in "
                                        "spring, hay in July, gales off Cardigan Bay through winter"})
    spark.save(os.path.join(TIME, "earth-time.json"), tb)
    return sorted(renditions)


# --- demonstration ----------------------------------------------------------

def _line(reg, r):
    txt = r.get("text") or "(silent)"
    return "    %-2s p%+d [%-10s] %s" % (reg, r["pscale"], r.get("sign") or r["status"], txt)


def demo():
    print("seed:", seed(), "shell surfaces + the T-spine +", os.path.basename(ATTEST))
    earth = locate.fs_loader()
    ploader = personal_loader()
    tblock = time_block()

    # derive-don't-assume (the parallel session's locate fix): guard the room address
    derived = locate.to_walk(locate.find_prefix("wales", earth) + locate.floor_path("wales", earth))
    assert derived == CEIDIO_ROOM, "Ceidio room drifted to %s != %s -- reseed" % (derived, CEIDIO_ROOM)

    print("\n" + "=" * 74)
    print("1 -- THE FRAME: one address, three registers (S * T * I), per reader")
    print("    where = Ceidio's room (%s, pscale 0); when = 'now'" % locate.to_address(_digits(CEIDIO_ROOM)))
    for who in ("david", "asha"):
        fr = frame(CEIDIO_ROOM, "now", who, earth, ploader, tblock)
        print("\n  who = %s   [I:%s · T:%s · coordinatable:%s]"
              % (who, fr["presence"]["sign"], fr["T"]["sign"], fr["coordinatable"]))
        print(_line("S", fr["S"]));  print(_line("T", fr["T"]));  print(_line("I", fr["I"]))
        print("    -> moment: %s" % (fr["moment"] or "[no key -- a reading LLM folds the prompt]"))

    print("\n" + "-" * 74)
    print("    T IS NOW REAL (was a stub) -- it has SCALE and a mirror/projection SIGN:")
    wp2, wrm = _where(CEIDIO_P2, earth), _where(CEIDIO_ROOM, earth)
    print("      +2 rhythm    : %s" % read_T(wp2, "now", tblock)["text"])
    print("      p0 mirror    : %s" % read_T(wrm, "now", tblock)["text"])
    print("      p0 projection: %s" % read_T(wrm, "midwinter eve", tblock)["text"])

    print("\n" + "=" * 74)
    print("2 -- THE I-FAN -> THE SOCIAL FOLD (1^0 the public map  ->  1^9 the lived place)")
    f = fan(CEIDIO_ROOM, earth, ploader)
    print("    S, public (1^0): %s" % f["public"])
    for e in f["fan"]:
        print("      fan: %-14s (%-10s) %s" % (e["who"], e["sign"], e["account"][:46] + "..."))
    full = social_fold(CEIDIO_ROOM, mirror_only=False, earth_loader=earth, ploader=ploader)
    mir = social_fold(CEIDIO_ROOM, mirror_only=True, earth_loader=earth, ploader=ploader)
    print("\n    social fold, ALL accounts (1^9):\n      %s" % (full["synthesis"] or "[prompt only]"))
    print("\n    social fold, MIRROR-ONLY (coordination -- grounded presence drops the projection):")
    print("      members: %s\n      %s" % ([e["who"] for e in mir["members"]],
                                            mir["synthesis"] or "[prompt only]"))

    print("\n" + "=" * 74)
    print("3 -- THE SIGN ACROSS S * T * I: a moment COORDINATES only if it mirrors reality")
    print("    actual / projected is reader-applied (never a stored field), on every axis:")
    for label, args in [("david · here · now", (CEIDIO_ROOM, "now", "david")),
                        ("happyseaurchin · here · now", (CEIDIO_ROOM, "now", "happyseaurchin")),
                        ("david · here · midwinter", (CEIDIO_ROOM, "midwinter", "david")),
                        ("happyseaurchin · NY deli · now", (NY_DELI, "now", "happyseaurchin"))]:
        fr = frame(*args, earth_loader=earth, ploader=ploader, tblock=tblock, synth=False)
        m = fr["mirror"]
        print("    %-30s  S:%-8s T:%-10s I:%-10s -> coordinatable: %s"
              % (label, "mapped" if m["S"] else "unmapped",
                 fr["T"]["sign"], fr["presence"]["sign"], fr["coordinatable"]))

    print("\n" + "=" * 74)
    print("4 -- THE WRITE: an inhabitant VOICES a rendition -> the social fold grows")
    print("    (the I-write is the spark primitive: a point-write into your OWN shell")
    print("     surface -- surface-<handle> -- at the spindle, membrane-gated at the door.)")
    before = social_fold(CEIDIO_ROOM, earth_loader=earth, ploader=ploader, synth=False)
    print("    fan before:", [m["who"] for m in before["members"]])
    r = voice(CEIDIO_ROOM, "mira",
              "the room as I found it tonight -- the radiator silent, rain on the yard "
              "window, a kettle just boiled. -- mira", earth_loader=earth)
    print("    mira voices -> %s landed in block %s at %s (p%+d)"
          % ("rendition", r["block"], r["where"]["address"], r["where"]["pscale"]))
    after = social_fold(CEIDIO_ROOM, earth_loader=earth, ploader=personal_loader(), synth=True)
    print("    fan after :", [m["who"] for m in after["members"]])
    print("    re-folded social (1^9):\n      %s" % (after["synthesis"] or "[prompt only]"))
    print("=" * 74)


if __name__ == "__main__":
    if sys.argv[1:] and sys.argv[1] == "seed":
        print("seeded:", seed())
    else:
        demo()
