"""biome — the genome's single entry point: sense the rock, unfold the fit form, become it.

Drop the genome on a rock and run this. It senses what the rock affords, asks
the shell which form fits (unfold.resolve_role), and LAUNCHES that form —
closing the sense -> unfold -> become loop that biome-definition.json (branch
2.3) names as the biome's nature. Until now the pieces sensed and *reported*; a
human chose which script to run. This is the missing act-on-the-decision layer:
unfold resolves, biome.py becomes.

What launches in-process today: the beach — a substrate served through the
biome-beach door and the biome-mcp interface (serve.py). The other resolutions
are reported with their path rather than faked: a rock with a key resolves to a
mind (the collective at src/agent, run through its own scripts); a removable
surface resolves to carry (a relation by shared currents, not a server); bare
storage resolves to a silent beach awaiting a port.

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

# The shell resolves a role; the launcher maps it to a launchable FORM in the
# settled vocabulary (beach / mind / carry / silent). courier is retracted as a
# form — a removable surface relates by shared currents, it does not serve.
ROLE_TO_FORM = {
    "commons": "beach",      # durable storage + a free port → serve the substrate
    "substrate": "beach",    # durable storage → a beach, served once a port opens
    "mind": "mind",          # an LLM key → this rock animates a shell
    "courier": "carry",      # retracted as a form → relate, do not serve
}


def form_for(role):
    return ROLE_TO_FORM.get(role, "silent")


def become(cond=None, dry_run=False):
    """Sense -> unfold -> become. Returns the resolved form name."""
    cond = sensor.sense() if cond is None else cond
    shell = spark.load(U.SHELL)
    intention = U.resolve_role(cond, shell)
    role = intention["role"]
    form = form_for(role)
    port_free = cond["endpoints"]["port_free"]
    durable = cond["storage"]["filesystem_writable"] or bool(cond["storage"]["hosted_db"])
    if form == "beach" and not durable:
        form = "silent"          # a beach needs a surface to hold blocks; without one, nothing to serve

    print("biome — sense · unfold · become")
    print("  rock        : storage=%s  port_free=%s  key=%s" % (
        cond["storage"]["filesystem_writable"] or bool(cond["storage"]["hosted_db"]),
        port_free, cond["cognition"]["llm_key"]))
    print("  resolved    : role=%s  ->  form=%s" % (role, form))
    print("  because     : %s" % "; ".join(intention["reasons"]))

    if dry_run:
        print("  --dry-run: nothing launched.")
        return form

    if form == "beach" and port_free:
        print("  becoming the beach (door + biome-mcp) ...")
        import serve
        serve.main()                                  # blocks: serve_forever
    elif form == "beach":
        print("  a beach with no free port — open one, then run: python3 serve.py")
    elif form == "mind":
        print("  a mind — this rock animates a shell. Run the collective:")
        print("    cd ../agent && ./new-collective.sh '<hypothesis>'  then  ./run-round.sh")
    elif form == "carry":
        print("  a removable surface — relate to a beach by shared currents, do not serve.")
    else:
        print("  silent storage — nothing to launch until a port or a key appears.")
    return form


if __name__ == "__main__":
    become(dry_run="--dry-run" in sys.argv)
