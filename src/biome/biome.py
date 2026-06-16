"""biome — the genome's single entry point: sense the rock, unfold the fit form, become it.

Drop the genome on a rock and run this. It senses what the rock affords, asks
the shell which form fits (unfold.resolve_role), and LAUNCHES that form —
closing the sense -> unfold -> become loop that biome-definition.json (branch
2.3) names as the biome's nature. Until now the pieces sensed and *reported*; a
human chose which script to run. This is the missing act-on-the-decision layer:
unfold resolves, biome.py becomes.

The genome's FORMS are beach / mind / interface (STABILISED NOMENCLATURE,
docs/xstream-session-handover.md). interface is served AT the beach's doors
(/mcp = biome-mcp for an LLM; /xstream for a human, when built), so becoming the
beach is what serves it — it is not a separate launch target. What launches
in-process today is therefore the beach (serve.py) or a mind; other rocks
resolve to no launchable form and are reported rather than faked: a rock with a
key resolves to a mind (the collective at src/agent, via its own scripts); a
removable surface relates by shared currents and serves nothing (courier is
retracted — there is no carry form); bare storage waits for a port.

Run:  python3 biome.py            # sense, unfold, and become the fit form
      python3 biome.py --dry-run  # sense and resolve only; launch nothing
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "spark"))
sys.path.insert(0, HERE)

import sense as sensor
import spark
import unfold as U

# The shell resolves a role; the launcher maps it to one of the genome's FORMS
# (beach / mind — interface is served at the beach's doors, not launched here).
# A role with no launchable form maps to None: courier is retracted (a removable
# surface relates by shared currents, it does not serve), and bare storage waits.
ROLE_TO_FORM = {
    "commons": "beach",      # durable storage + a free port → serve the substrate
    "substrate": "beach",    # durable storage → a beach, served once a port opens
    "mind": "mind",          # an LLM key → this rock animates a shell
}


def form_for(role):
    # None = no launchable form for this role (e.g. a retracted-courier removable
    # surface, or an unrecognised role). An absence, not a form.
    return ROLE_TO_FORM.get(role)


def become(cond=None, dry_run=False):
    """Sense -> unfold -> become. Returns the resolved form name, or None if the
    rock affords no launchable form."""
    cond = sensor.sense() if cond is None else cond
    shell = spark.load(U.SHELL)
    intention = U.resolve_role(cond, shell)
    role = intention["role"]
    form = form_for(role)
    port_free = cond["endpoints"]["port_free"]
    durable = cond["storage"]["filesystem_writable"] or bool(cond["storage"]["hosted_db"])
    if form == "beach" and not durable:
        form = None              # a beach needs a surface to hold blocks; without one there is no form to become

    print("biome — sense · unfold · become")
    print("  rock        : storage=%s  port_free=%s  key=%s" % (
        cond["storage"]["filesystem_writable"] or bool(cond["storage"]["hosted_db"]),
        port_free, cond["cognition"]["llm_key"]))
    print("  resolved    : role=%s  ->  form=%s" % (role, form or "none (nothing to become yet)"))
    print("  because     : %s" % "; ".join(intention["reasons"]))

    if dry_run:
        print("  --dry-run: nothing launched.")
        return form

    if form == "beach" and port_free:
        print("  becoming the beach — serving its doors (biome-beach; biome-mcp at /mcp; /xstream when built) ...")
        import serve
        serve.main()                                  # blocks: serve_forever
    elif form == "beach":
        print("  a beach with no free port — open one, then run: python3 serve.py")
    elif form == "mind":
        print("  a mind — this rock animates a shell. Run the collective:")
        print("    cd ../agent && ./new-collective.sh '<hypothesis>'  then  ./run-round.sh")
    else:
        print("  no form to become yet — this rock affords no servable beach and no key.")
        print("  (a removable surface relates by shared currents; bare storage waits for a port.)")
    return form


if __name__ == "__main__":
    become(dry_run="--dry-run" in sys.argv)
