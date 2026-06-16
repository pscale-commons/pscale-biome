# RPG resolver hand-off — the rig's rules → blocks (for the genome session)

This hands over the **resolver seam**: the RPG verbs the coded bench (`src/rpg`)
proved, stated as rules ready to become **flint** — blocks an LLM enacts via
spark — so the kernel can shrink to *spark + a thin loop + the membrane*.

The bench is the **behavioural reference**, not the substrate. It crystallised
the verbs into Python prematurely (the metabolism run backwards; assembled, not
derived). Read it for exact behaviour; **do not extend it** — this hand-off is
the de-crystallisation brief. Encode the rules in the genome's own 0-9 + minimal
kernel however fits; what follows is *what the verbs must do*, not how to write
them.

## The split
- **Nouns — already blocks, keep:** world S/T/I (`upperton-space/-time/-identity`),
  character shells (`characters/<name>/`: `purpose` `history` `conditions` `bind`
  `perceived`), the world-truth scene record.
- **Verbs — currently code, make them blocks:** compose-frame, soft-act,
  medium-resolve, soft-render, settle. `sti-function` (live on the commons) is the
  seed of compose-frame.

## The verbs as rules (each becomes a block the LLM reads + enacts)

1. **compose-frame** — seed `sti-function`; code ref `frame.bind_window`.
   One character's window at an address = **HERE** (space: the descent + the
   room's contents) + **NOW** (time: the descent + *the character's own recent
   perceived moments*, never the omniscient record) + **WHO** (identity: the
   standpoint = the X−1 pick + the collective head) + **SELF** (the shell:
   purpose / conditions / history). Fold by **pscale, not walk-depth**. Aperture
   (character face): own standpoint + the collective head + own perceived
   history — **never** another character's interior.

2. **soft-act** — code ref `tiers.soft_act`. A character (or human) perceives
   ONLY its window and chooses an intention, first person.

3. **medium-resolve** — code ref `tiers.medium_resolve`. Omniscient. Given all
   acts + the full field (every who at the place + objects in reach + the
   world-truth history), resolve what ACTUALLY happens; the more-grounded reading
   is authoritative where they conflict. Output: the TRUTH (world-truth, shown to
   no player) + each character's material outcome.

4. **soft-render** — code ref `tiers.soft_render`. Per character: **second
   person** ("you…"), ONLY what THIS character perceives of the truth — omit a
   stealthy act they didn't notice, omit others' interiors. **Discovery-by-action:**
   their act surfaces what it would let them notice, at no more certainty than it
   earns. Output: the render (shown to the player) + a perceived-note for the
   character's own record.

5. **settle** — code ref `play.persist_*` (the bench's local form). **SPECIFIED
   by the persistence probe (2026-06-16, scratch `/tmp/probe_settle.py`, real
   spark-writes to the world-blocks).** The resolution becomes the world by
   block-writes, on this rule:
   - The **medium**, resolving, declares two things beside the per-character truth:
     the **PUBLIC aftermath** (what anyone present would perceive) and the
     **PRIVATE circumstance** (who / why — latent).
   - **settle** (an LLM step) composes the writes from the PUBLIC aftermath and
     spark-writes them into the channels the **aperture exposes**, so a later
     character perceives the consequence *through the place itself*: **space/HERE**
     (a body, overturned stools, a cooling pint), the **collective identity head**
     (the room's public hush), the **time/NOW** (the aftermath), and the affected
     entity's own node (the keeper → dead) as the record.
   - The **PRIVATE circumstance** goes to **world-truth only** — never the public
     blocks.
   - **Proven end-to-end:** a newcomer binding the place later perceived the death
     (body + hush) but **not** who did it or why; those were **earned by
     discovery-by-action** (asking the regular gave a partial, hedged account — the
     public story plus a hint — not the full private truth).
   - **Coherence requirement (new finding):** a consequence usually touches **S, T
     and I** — settle must propagate to **every register it changes** or they
     contradict. The probe wrote the body (S) and the hush (I) but not the aftermath
     in time, and the newcomer's NOW still showed the live dice-game beside a silent
     corpse. *settle is not done until S, T and I agree* (this is where settle meets
     the world-NOW-advance work — the consequence must enter the NOW too).
   - **The load-bearing finding (aperture × persistence):** make a consequence
     *public* by writing it where the aperture **shows** (space, the collective
     head, the NOW), **not** into a private entity-node it hides; keep the private
     circumstance in world-truth; let discovery-by-action bridge them.
   - **Bench limit:** the *mechanism* (consequence → block-writes → coherent
     read-back → aperture-correct public perception + discovery) is proven;
     **federation is not** (single instance) — it only *distributes* the same
     writes, so it stays the biome's job (storage current + the door). "A later
     player passing through finds the keeper dead" is the same mechanism the probe
     ran directly as "a newcomer binds the mutated world."

## Proven (the bench validated, over the wire)
- **Perception-limiting holds** — the merchant never saw the theft.
- **Discovery-by-action works** — he learned of the loss by reaching for his hip.
- **NPC weaving works** — the watcher's full theft-and-escape resolved into every turn.
- **The SMH separation is right** — omniscient resolution behind the screen;
  per-character second-person perception in front.

## Gaps the rules must grow to address (from David's play of v005)
- **Agency-purchase / visible checks** — player acts couldn't shift a sealed
  outcome, and the check (the resolution) is invisible. Needs a check-rule with
  stakes the player can affect, surfaced as something perceptible.
- **Movement** — a character is pinned to one address. Movement = a **write to
  `bind.here`**, enacted per a move-rule. No move-function.
- **World-state mutation / persistence** — **now specified** (see verb 5; the
  persistence probe, 2026-06-16): consequences are spark-writes to the public
  channels (space/HERE + the collective head + time/NOW) plus the entity's node,
  the private circumstance to world-truth, propagated to every register the
  consequence changes. The open part is the **federated** substrate (the commons)
  so it persists *across players* — the bench proved the mechanism, not the
  federation.
- **Violence / HP** — a status in the shell the medium resolves against, so death
  is determinate, not arbitrary narration.
- **Multi-PC** — the medium already resolves N acts together; multi-human needs
  round synchronisation (resolve once all PCs have acted) + per-player views (the
  aperture already filters per character).

## The kernel stays minimal
spark (walk) + a thin read → hand-to-LLM → route-the-writes loop + the digit-key
membrane. The kernel must **not** know "fold / resolve / render" — those are
blocks it loads. `src/agent/kernel.py` is most of that shape already.
