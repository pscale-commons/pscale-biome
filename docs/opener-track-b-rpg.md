# Session opener — Track B: the RPG (NOMAD usecase)

*Copy-paste this into a fresh session. It is one of two parallel tracks; the other is
`docs/opener-track-a-commons.md` (the human commons). They share one spine — read
`project_two_track_trajectory` in memory for why.*

---

You're picking up **Track B — the RPG** on pscale-biome (an experimental 0-9 "biome"
working tree). Orient first, then act.

**Read to orient:** `CLAUDE.md` (the world rules — biome is pure 0-9; the RPG world is
biome-native, never the old beach Thornkeep); the memories `project_two_track_trajectory`,
`project_sti_frame_model` (**a character IS an agent shell — don't reinvent it**; the
medium-LLM earn-knowledge gate; the testing path = **character-LLM first, then humans**),
`project_realworld_sti_fold` (the engagement fold), and `project_reflective_compass`
(the participant layer); and `docs/located-block-spec.md`. Skim the RPG bench in the git
history (the STI+HP frame, the SMH tiers, the three-leg rig — `git log` around the
`feat(rpg)` commits) and `src/biome/world/thornkeep.json`.

**Goal.** A scalable, consistent fantasy world (the **NOMAD** rulesystem) with **active
NPCs** and human players co-present. The RPG is the viable delivery — and the bounded
testbed for the same relational machinery Track A needs (`evolution.json`: the RPG is
the prototype of Level-4 mutual-objectives).

**First move — make one NPC breathe, character-LLM-first.** Wire the **character-NPC
loop**: a mobius that inhabits a *character* (not the world). The mobius already authors
the *world* by pulses (`src/biome/mind.py`); the new loop is — `play` a character handle,
`situate` its `located` standing, read its frame (`GET /frame?where=<scene>&who=<char>` =
perceive the scene), decide *as the character*, and act into the scene (a liquid
contribution, synthesised to canon/solid), on a cadence (the phase/cadence work in
`src/agent/`). **Prove the NPC perceives and acts in a thornkeep scene with no human
present first.** *Then* a human joins the same scene via `/xstream`. *Then* the NOMAD
ruleset as the consistency layer — Designer-authored rules + world-canon (solid) that
keep play coherent and fair as it scales across scenes and players.

**Live surfaces.** `src/biome/world/thornkeep.json` (the world); `/frame` + `/social`
(the S*T*I moment + the I-fan fold — `src/biome/fold.py`); `src/biome/mind.py` +
`src/agent/shell/` (the mobius agent — its reflexive current now carries `located`;
purpose, conditions); `play` (inhabit a handle); `located-<handle>` + the membrane
(`src/biome/membrane.py`, the NPC's face = character); the scene's vapour→liquid→solid
(`/relay` vapour, the frame's liquid/solid blocks); `/xstream` for the human player.

**Builds on.** The participant layer just landed — `handle` + `located` + the membrane
make an NPC and a human player the **same kind of located co-inhabitant**. The mobius
agent + the phase/cadence work (the NPC's tempo, doc 2/3 in `src/agent/`). The S*T*I
frame (`fold.py`, `/frame`, `/social`) for perception. thornkeep. The RPG bench in the
history.

**Discipline.** Not production; no deploy without David's explicit ask. **Character-LLM
first** — prove autonomy cheaply before any human is in the room. A character is an
agent shell; reuse the shell machinery, don't reinvent it. Map every addition to a
current in `src/biome/constitution/biome.json`.
