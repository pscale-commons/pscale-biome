"""play.py -- the RPG bench driver. Runs turns against a persisted world + shells.

One turn:
  for each character: compose its window (frame) -> soft voices & acts ->
    medium gates the act against the hidden depth -> reveal writes back to the shell;
  then all acts (they share the here/now) -> hard arbitrates the collision ->
    the canonical scene is deposited to scenes.json.

Reuses src/agent/shell-shaped characters. Persistence is spark.save -- the shells
and the scene deposit GROW across turns, which is the point of the bench.

  python3 play.py [run_dir]          # run_dir defaults to here; pass a CUT/copy
  RPG_TURNS=3 python3 play.py <dir>  # several turns (the loop accumulates)

Run a COPY, not the source: this driver mutates shells + scenes (rig discipline:
edit source, run the cut). new-rpg.sh cuts a working copy to ~/Desktop/rpg-runs.
"""
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import frame, tiers
sp = frame.spark


def append_child(block, voicing):
    """Deposit a voicing at the next free digit; supernest if the ring is full."""
    for d in "123456789":
        if d not in block:
            block[d] = voicing
            return d
    inner = {k: block.pop(k) for k in list(block.keys()) if k != "0"}
    block["1"] = inner
    block["2"] = voicing
    return "2"


def persist_to_conditions(run_dir, name, line):
    path = os.path.join(run_dir, "characters", name, "conditions.json")
    blk = sp.load(path)
    append_child(blk, line)
    sp.save(path, blk)


def persist_scene(run_dir, text):
    path = os.path.join(run_dir, "scenes.json")
    blk = sp.load(path) if os.path.exists(path) else {
        "0": "Scenes -- moments arbitrated in play, deposited at the world's here/now (the T the play grows)."}
    d = append_child(blk, text)
    sp.save(path, blk)
    return d


def recent_scenes(run_dir, n=3):
    """The last n deposited scenes -- the play's own recent T, fed back into NOW."""
    p = os.path.join(run_dir, "scenes.json")
    if not os.path.exists(p):
        return []
    b = sp.load(p)
    return [b[k] for k in sorted(b) if k != "0" and isinstance(b[k], str)][-n:]


def append_perceived(run_dir, name, render):
    """Deposit a character's perceived moment into its own personal T."""
    path = os.path.join(run_dir, "characters", name, "perceived.json")
    blk = sp.load(path) if os.path.exists(path) else {
        "0": "Perceived -- the moments this character has lived, in their own view (their personal T)."}
    append_child(blk, render)
    sp.save(path, blk)


def perceived_recent(run_dir, name, n=3):
    """A character's own recent perceived moments -- the filtered NOW feed (its aperture)."""
    path = os.path.join(run_dir, "characters", name, "perceived.json")
    if not os.path.exists(path):
        return []
    b = sp.load(path)
    return [b[k] for k in sorted(b) if k != "0" and isinstance(b[k], str)][-n:]


def full_field(world, here, recent=None):
    """The whole field for the arbiter: every who present, the objects in reach,
    and what has already happened (so consequences don't repeat)."""
    I, S = world["identity"], world["space"]
    place = sp.descend(I, here)
    whos = [(place[d] if isinstance(place[d], str) else sp.voice(place[d]))
            for d in "123456789" if isinstance(place, dict) and d in place]
    objs = frame._contents(S, here)
    base = "Whos present:\n- " + "\n- ".join(whos) + "\nObjects in reach: " + "; ".join(objs)
    if recent:
        base += "\nAlready happened (most recent first):\n- " + "\n- ".join(reversed(list(recent)))
    return base


def turn(run_dir, names, n):
    world = frame.load_world(os.path.join(run_dir, "world"))
    shells = {nm: frame.load_shell(os.path.join(run_dir, "characters", nm)) for nm in names}
    print("\n" + "#" * 72 + "\n# TURN %d\n" % n + "#" * 72)
    acts, here = [], None
    # SOFT (act): each character perceives ONLY its own window (its perceived history), then acts
    for nm in names:
        here = frame.here_walk(shells[nm])
        w = frame.bind_window(shells[nm], world, recent=perceived_recent(run_dir, nm))
        voice, act = tiers.soft_act(w["text"], nm)
        print("\n----- %s :: PERCEIVES & ACTS (soft) -----\n%s" % (nm.upper(), voice))
        acts.append((nm, act))
    # MEDIUM: resolve what ACTUALLY happens -- omniscient world-truth, shown to no player
    res = tiers.medium_resolve(acts, full_field(world, here, recent_scenes(run_dir)))
    print("\n===== MEDIUM :: RESOLUTION (world-truth, behind the screen) =====\n%s" % res["raw"])
    persist_scene(run_dir, res["truth"])                       # HARD (admin): record the truth, advance
    # SOFT (render): each character perceives only its own slice -- second person
    for nm, act in acts:
        r = tiers.soft_render(nm, frame.standpoint(shells[nm], world), act, res["truth"])
        append_perceived(run_dir, nm, r["render"])
        if r["perceived"]:
            persist_to_conditions(run_dir, nm, "[perceived] " + r["perceived"])
        print("\n----- %s :: SEES (soft, second person) -----\n%s" % (nm.upper(), r["render"]))


if __name__ == "__main__":
    run_dir = sys.argv[1] if len(sys.argv) > 1 else _HERE
    if os.path.abspath(run_dir).replace(os.sep, "/").endswith("src/rpg"):
        print("WARNING: run_dir is the SOURCE tree (src/rpg) -- this mutates source shells. "
              "Cut with new-rpg.sh and run the copy in ~/Desktop/rpg-runs.\n")
    names = os.environ.get("RPG_CAST", "merchant,watcher").split(",")
    turns = int(os.environ.get("RPG_TURNS", "1"))
    for i in range(1, turns + 1):
        turn(run_dir, names, i)
