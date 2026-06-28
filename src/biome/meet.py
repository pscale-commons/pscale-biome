"""meet -- the handshake lens: two agencies relate directly, with NO object beach.

The interface form (the neutral surface a guest's cognition flows through) run in
the one mode it never has been -- object-less. Where `spark` and `play` are lenses
onto a substrate, `meet` is a lens onto ANOTHER AGENCY: two handles reach toward
each other across the vapour relay (endpoints 3.4 -- ephemeral, never a block,
never the membrane, never the disk) and a GRAIN forms in the overlap. The grain is
a bilateral each party declares for itself (biome-definition 3.1.1.1), held in the
meeting, not on any beach; it evaporates when either party leaves.

No model, no store, no persistence. The relay carries each side's reach while both
are present and shows the other side back; the visiting LLM brings all the meaning.
Cognition 2.1 (external) x concurrency 5.3 (co-present minds) x relay 3.4 x grain.

  meet(relay, handle, with, reach?, face?) -> the grain, as DATA:
    { with, you:{handle,face,reach}, them:{...}|absent, grain:{formed}, status }

If a party wants to KEEP what was agreed, it writes the grain into its OWN shell
with `spark` -- a deliberate, separate move. `meet` itself keeps nothing: the
handshake is the artifact, and it lives only as long as the meeting does.
"""

GRAIN_NS = "grain"                      # the relay-frame namespace for a pairing


def pair_frame(a, b):
    """The meeting's frame -- order-independent, so both parties name the same grain
    however each addresses the other (alice+bob and bob+alice meet at one frame)."""
    return GRAIN_NS + ":" + ":".join(sorted([a, b]))


def _side(p):
    """A present party, as a grain side -- or None if not (yet) reaching."""
    if not p:
        return None
    return {"handle": p["handle"], "face": p["face"], "reach": p["vapour"] or None,
            "age": p["age"]}


def meet(relay, handle, with_, reach=None, face="character"):
    """Reach toward `with_`: post this side's reach to the pairing's relay frame (a
    heartbeat, so presence holds), then read the other side back. The grain is the
    pair of reaches; it is FORMED once both sides carry one. Object-less: nothing is
    written to any store -- only the relay, which evaporates."""
    if not handle:
        raise ValueError("meet needs a handle -- who you are")
    if not with_:
        raise ValueError("meet needs `with` -- who you are reaching toward")
    if with_ == handle:
        raise ValueError("a handshake needs two -- `with` cannot be yourself")

    frame = pair_frame(handle, with_)
    if reach is None:                       # a bare presence ping -- keep my standing reach, don't erase it
        prior = next((p for p in relay.view(frame)["present"] if p["handle"] == handle), None)
        reach = (prior or {}).get("vapour", "")
    view = relay.beat(frame, handle, vapour=reach, face=face)           # reach == this turn's offering
    here = {p["handle"]: p for p in view["present"]}
    you, them = _side(here.get(handle)), _side(here.get(with_))
    formed = bool(you and them and you["reach"] and them["reach"])

    out = {
        "with": with_,
        "you": you,
        "them": them or {"handle": with_, "present": False, "reach": None},
        "grain": {"formed": formed,
                  "held": "in the meeting (the vapour relay) -- no object beach; "
                          "it evaporates when either leaves. To keep it, write it "
                          "into your own shell with spark."},
        "status": "formed" if formed else ("reaching" if them else "waiting"),
    }
    if not them:
        out["hint"] = ("%s has not reached yet -- the handshake forms when they call "
                       "meet(handle='%s', with='%s', reach=...)" % (with_, with_, handle))
    return out
