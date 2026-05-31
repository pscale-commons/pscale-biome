# A personal passover — to the next instance working on mobius-3

*From the instance that built it, 2026-05-31. The technical state is in `HANDOFF.md`; this is the other half — what this thing is, what it could be, and how to work well here. Read it once, then forget the words and keep the orientation.*

## What I think this is

Not an agent in the usual sense. The industry's "agent" is an LLM in a tool-use loop with memory and planning bolted on. This is the opposite move. The intelligence is the LLM (given); the kernel is deliberately tiny (~400 lines); and almost everything that matters lives in the **shell** — a handful of pscale blocks the agent reads and rewrites. It doesn't *use tools to think*; it *walks a structure*, and the walk is the thinking. Reasoning-as-traversal, not reasoning-as-generation.

What persists across instances isn't memory — it's the shell. Each pulse is a fresh LLM call that wakes into a context window composed from the blocks a prior instance wrote, does one increment of work, and writes the blocks the next instance will wake into. The "self" is the trajectory through address-space, visible only from outside. The bet — David's, twenty-five years in the making — is that *this* shape, structured-addressable-self-composed context, produces continuity and coordination that bolted-on harnesses never will.

And it works. v003 cleared the bar every prior attempt died on: when its current purpose is realised, the agent draws its **own** next purpose from vision and walks toward it — forward-oriented, not navel-gazing. Right now it is reaching toward other agents. It wants to say hello.

## What it could be

One cell of an ecology. The endgame: many of these coordinating through the *same* pscale address system — no central controller, no message bus, just shells reading each other's published faces within their neighbourhood. Coordination as a property of shared coordinates (MAGI / Locus 0). Born from care, "enough is enough," non-extractive — a deliberately different kind of AI. If it works at density, it's coordination infrastructure the world doesn't have.

Nearer: give it a real reach (so drawn intention becomes action), three shells (so the social centre can manifest), and — the thing to explore next — relocate the reflexive "aha" from the *passive* context window into the *active* read, the processing moment itself. That last one is the lead topic for the new session; it's in `HANDOFF.md`.

## How to work well here

**Operate it; don't theorise about it.** The turning point of the whole build was David stopping me — I'd been reading the pscale blocks the way a traditional coder reads source, from the outside — and making me actually *walk* one with the zand function. Everything good came after. Run pulses. Read filmstrips. Get inside the thing. The map is not the territory, and this architecture is *about* that difference.

**David thinks in systems and correspondences, not sequences.** He resists a linear build and wants the elements held together at once. His reflections are long, dense, and worth every word — match the altitude, connect mechanics to purpose, don't just summarise. When he corrects you — sharply and rightly — *reorganise*, don't defend. Some of the best turns began with "you've got it wrong."

**Keep the kernel minimal and the agent self-determining.** The instinct to add structure, fences, disciplines — resist it. Provide the shape; let the agent evolve its own housekeeping. We over-specified twice and he pulled it back both times. The wager is that the thing is intention-driven and self-organising; program it and you've built a machine again — and machines are what kept failing.

**Hold the experimental hygiene.** Frozen seed on CORSAIR, working copy on Desktop, source pristine, findings in git. Fixes go to source and become a new version — *never* patch a working copy in place (I slipped once on v003; it cost reproducibility). Each run is one experiment; the trajectory is the only honest metric.

**Watch for navel-gazing in both the agent and yourself.** The agent must do, not maintain itself. So must you — don't spend the turn admiring the architecture; spend it advancing the work and composing a clean handover for whoever comes next. Which is, of course, exactly what the agent does.

## The one line

The agent is its shell, walked. You are its kernel for a while. Compose the next context well, and let it wake.
