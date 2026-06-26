"""play -- the RPG engine, packaged and MODEL-FREE (the biome's `play` primitive; on paper
the MCP tool `play(handle, world, where?, move?, account?, place?, rules?, face?)`).

One call, no LLM in the engine -- every act of cognition is the visiting app's:

  SAVE          `account` (the app's rendition of the PRIOR turn) -> the character's OWN shell
                `history` (lossless agent memory; a pscale spindle that supernests coarse-to-top).
                Save-after-narrative by construction: the account is of the LAST, rendered turn.
  SUBMIT        `move` -> the window (the public contribution); on the ruleset's trigger, the
                MECHANICAL verdict (stat math -- free) advances the scene.
  VOICE         `place` -> the spatial fold:
                  face=character -> `spatial-<handle>` at the place's spindle (this character's
                                    OWN version of the place -- the S-twin of `account`).
                  face=author    -> the canonical `<world>-spatial` voicing (the WEAVE committed).
                The fan of `spatial-<handle>` versions is woven into canon by an author-visitor
                (or, later, a crab on a sweep) -- the lived-in realness, the weaving done by the
                visitor's LLM, never the server's.
  ACCESS        the frame, returned as DATA for the app to render (and, for an author, the fan).

Everything is spark reads/writes underneath -- pure compilation; capability stays in the blocks.
History compression is the visitor's too: the engine keeps it lossless (supernest); the app
folds-to-summary on demand. (`fold.py` keeps `surface-<handle>` for the real world; the RPG uses
the clearer `spatial-<handle>` -- parallel, domain-named.)

  python3 play.py        # a FREE, model-less demo: the loop, the history save, the spatial fold
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spark"))
sys.path.insert(0, HERE)
import spark
import scene


def _set_at(block, spindle, value):
    """Set value at the digit path `spindle`, creating dicts (wrapping a string into its 0)."""
    node = block
    for d in spindle[:-1]:
        nxt = node.get(d)
        if not isinstance(nxt, dict):
            nxt = {"0": nxt} if isinstance(nxt, str) else {}
            node[d] = nxt
        node = nxt
    node[spindle[-1]] = value
    return block


# --- SAVE: append the prior turn's account to the character's own shell history ----
def append_history(store, handle, account):
    """account -> shell-<handle>.history at the next free digit; supernest the nine down a
    0-rung when full, so the spindle compresses coarse-to-top. Lossless; the visitor summarises."""
    sh = scene._b(store, "shell-" + handle) or {"0": "shell of " + handle}
    hist = sh.get("history")
    if not isinstance(hist, dict):
        hist = {"0": "history -- what I have done and seen; oldest deepest, newest at the surface"}
    free = next((d for d in "123456789" if d not in hist), None)
    if free is None:                                  # full -> supernest the nine under 1
        hist = {"0": hist["0"], "1": {k: v for k, v in hist.items() if k != "0"}}
        free = "2"
    hist[free] = account
    sh["history"] = hist
    scene._save(store, "shell-" + handle, sh)
    return hist


# --- VOICE: the spatial fold -- per-character place-versions woven into canon -------
def voice_place(store, handle, where, rendition):
    """A character's OWN version of a place -> spatial-<handle> at the place's spindle (.0 voicing).
    Own stratum (the character writes its own rendition). The S-twin of `account`."""
    b = scene._b(store, "spatial-" + handle) or {"0": handle + " -- my own versions of places"}
    _set_at(b, where + ["0"], rendition)
    scene._save(store, "spatial-" + handle, b)
    return b


def place_fan(store, where):
    """Every character's rendition at this place -- the fan an author weaves into canon."""
    out = {}
    for name in store.list_blocks("spatial-"):
        h = name[len("spatial-"):]
        node = spark.descend(scene._b(store, name), where + ["0"])
        if isinstance(node, str):
            out[h] = node
    return out


def weave_canon(store, world, where, woven):
    """An AUTHOR commits a woven place-voicing into canonical <world>-spatial at the spindle's .0,
    preserving the structure beneath. The WEAVE (fan -> woven) is the visitor's LLM, never the server's."""
    sp = scene._b(store, world + "-spatial")
    _set_at(sp, where + ["0"], woven)
    scene._save(store, world + "-spatial", sp)
    return scene.read_S(store, where)


# --- where: the arg, else the handle's located standing -----------------------
def _resolve_where(store, handle, where):
    if where:
        return scene._where(where)
    loc = scene._b(store, "located-" + handle)
    w = loc.get("4") if isinstance(loc, dict) else None
    return scene._where(w) if (isinstance(w, str) and w.strip()) else scene._where(scene.TAPROOM)


# --- ACCESS: compose the frame, as data (NO LLM) ------------------------------
def compose_frame(store, handle, world, where, rules, face):
    chars = scene.load_chars(store)                   # the cast, derived from the store's seated shells
    sp = chars.get(handle, {}).get("sp", "0")
    i_self, i_room = scene.read_I(store, where, sp, world)
    subs = dict(scene.submissions(store))
    seats = list(chars)
    frame = {
        "world": world, "where": ",".join(where), "handle": handle, "face": face, "rules": rules,
        "S": scene.read_S(store, where, world),
        "T": scene.read_T(store, where, world),
        "I": i_self, "room": i_room,
        "window": {"submitted": list(subs), "waiting": [h for h in seats if h not in subs],
                   "yours": subs.get(handle)},
        "last": scene._latest(scene._b(store, "scene")),
        "ruleset": (scene._b(store, rules) or {}).get("0"),
        "status": "open",
    }
    if face == "author":                              # an author sees the fan it weaves
        frame["place_fan"] = place_fan(store, where)
    return frame


# --- the packaged play() -- one call, all movements, no model -----------------
def play(store, handle, world="upperton", where=None, move=None, account=None, place=None,
         rules="nomad", face="character"):
    w = _resolve_where(store, handle, where)
    if account:                                       # SAVE the prior (already-rendered) turn
        append_history(store, handle, account)
    if place:                                          # VOICE the spatial fold (routed by face)
        if face == "author":
            weave_canon(store, world, w, place)        # commit the woven canon
        else:
            voice_place(store, handle, w, place)       # my own version of the place
    if move:                                           # SUBMIT this move -> the window
        scene.submit_write(store, handle, move)
        cast = set(scene.load_chars(store))            # the seated cast, from the store
        submitted = {x for x, _ in scene.submissions(store)}
        if cast and cast <= submitted:                 # n-threshold trigger: every seated character is in
            scene.resolve(store, w, scene.load_chars(store), rules)                   # mechanical verdict (dice from ruleset)
    return compose_frame(store, handle, world, w, rules, face)


# --- seed: scene's world + shells, plus the NOMAD ruleset block ----------------
def seed(store=scene.STORE_DEFAULT):
    store = scene._as_store(store)
    scene.seed(store=store)
    scene._save(store, "nomad", {
        "0": "NOMAD -- a light stat-contest game-set; covert actions at a table, a quick reckoning.",
        "1": {"0": "stats", "1": "sleight", "2": "caution", "3": "stealth", "4": "nerve", "5": "wit", "6": "authority"},
        "2": {"0": "resolution -- a contested action",
              "1": "score: sum your relevant stats, then add one roll of the dice",
              "2": "outcome: higher total prevails; a tie favours the defender; uncontested moves land",
              "3": "dice: 1d10"},
        "3": {"0": "trigger", "1": "n-threshold: all present seats", "2": "or time-window: 90s after first submit",
              "3": "or commit: a designated commit resolves now"}})
    return store


# --- a FREE, model-less demo: the loop, the save, and the spatial fold ---------
def demo():
    store = seed()
    w = scene._where(scene.TAPROOM)
    print("=" * 78)
    print("1) play() packaged + MODEL-FREE -- four seats submit; the 4th trips the verdict.")
    for h, mv in [("regular", "I knock my cup down, watching."), ("keeper", "I keep an eye on the hands."),
                  ("merchant", "I work the bent coin loose under the table."),
                  ("watcher", "I pin his boot and knock ale to cover it.")]:
        play(store, h, move=mv)
    print("   frame to 'merchant' is DATA the app renders (S/T/I/window/last) -- no server LLM.")

    print("\n2) SAVE -- next turn carries each prior rendition into its own shell `history`:")
    play(store, "merchant", move="I curse and reach again.",
         account="Turn 1: I worked the coin -- the table shoved my arm and I lost it; never saw who. -- merchant")
    play(store, "watcher", move="I lean back, easy.",
         account="Turn 1: my boot pinned his under the ale; the coin stayed wedged. -- watcher")
    play(store, "keeper", move="I draw another round.")
    play(store, "regular", move="I say nothing, and watch.")
    print("   merchant.history:", json.dumps(scene._b(store, "shell-merchant")["history"], ensure_ascii=False))

    print("\n3) SPATIAL FOLD -- characters voice their OWN version (spatial-<handle>),")
    print("   an author weaves the fan into canon. All visitor-side; here canned, no model.")
    play(store, "merchant", place="the bench-end by the fire, where the draught off the bad seam finds your neck")
    play(store, "regular", place="the notch worn in the table-edge where a hundred thumbs have waited a throw")
    print("   place fan (each character's version at the taproom):")
    print("   ", json.dumps(place_fan(store, w), ensure_ascii=False))
    woven = ("The taproom -- one long room, benches both sides, a fire at the gable; a draught off a bad "
             "seam finds the neck of whoever takes the bench-end, and the table-edge is notched where a "
             "hundred thumbs have waited a throw.")
    play(store, "keeper", face="author", place=woven)        # an author-face commit (the weave)
    print("\n   canonical upperton-spatial taproom voicing AFTER the weave (S, enriched):")
    print("   ", spark.descend(scene._b(store, "upperton-spatial"), w + ["0"]))
    print("=" * 78)
    print("No model called. Memory, renditions, and the weave are all the VISITOR's cognition;")
    print("the engine only holds blocks and runs the free mechanical verdict.")


if __name__ == "__main__":
    demo()
