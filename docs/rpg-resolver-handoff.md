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

5. **settle** — code ref `play.persist_*`; the admin / "hard". The truth is
   recorded; each character's perceived slice → its own `perceived`. **Consequences
   (death, a move, a wound) are spark WRITES to world-blocks through the membrane**
   — not code-modelled state. Persistence + federation are then the biome's
   currents (storage + the door), not the RPG's code. This is the scaling pivot:
   a death persists because the world-block persists and federates, not because a
   server tracks it.

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
- **World-state mutation / persistence** — consequences must be **block-writes to
  the world** (the keeper struck from the identity fan) on a shared, federated
  substrate (the commons), so a death persists for a later player. Per-cut local
  worlds don't persist across players.
- **Violence / HP** — a status in the shell the medium resolves against, so death
  is determinate, not arbitrary narration.
- **Multi-PC** — the medium already resolves N acts together; multi-human needs
  round synchronisation (resolve once all PCs have acted) + per-player views (the
  aperture already filters per character).

## The kernel stays minimal
spark (walk) + a thin read → hand-to-LLM → route-the-writes loop + the digit-key
membrane. The kernel must **not** know "fold / resolve / render" — those are
blocks it loads. `src/agent/kernel.py` is most of that shape already.
