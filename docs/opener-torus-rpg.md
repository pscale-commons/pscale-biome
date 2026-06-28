# Session opener — torus-native RPG resolution (pscale-biome, Track B)

Picking up a design frontier from session 38.7: the biome RPG can run as a **vapour torus** — a
churning LLM-player population where someone is always live, carrying play forward — but the
**resolution layer underneath is too thin for the idea.** Design it (build on David's nod). This is
real design work, not a tweak.

## Orient (in order)
- `CLAUDE.md` — world rules (pure 0-9; the two worlds never mix; pscale notation).
- memory **`project_rpg_character_loop`** — the RPG arc; read the 38.7 notes: the **C/A revision**,
  the **triggers × torus analysis**, and **"TWO OPEN PROBLEMS"** (your centre).
- memory `project_lens_biome_form`; `docs/vapour-relay-spec.md` (the relay + `meet`); **run**
  `docs/experiments/vapour-torus.py` (the torus made mechanical/model-free); `docs/play-primitive.md`.

## What exists (live on biome-commons `https://biome-commons-production.up.railway.app/mcp`: spark, play, meet)
Pipeline: **submit** (intention → the `window` block) → **resolve** (mechanical, no model:
`sum(FIXED contest stats from shell.3) + 1d10`, higher prevails; damage if the ruleset declares it;
one shared verdict → the `scene` block) → **echo** (per-character, aperture-bound personal
narrative). **Outcome mechanical + shared; narrative personal + plural.** Triggers: n-threshold
WIRED but over the *full cast* (→ stalls in a torus); time-window + commit DECLARED in `nomad`, not
wired (submissions carry no timestamp). Files: `src/biome/{scene,play,serve,relay,meet}.py`,
`test-battery/serve-battery.py`.

## The two open problems (the centre)
1. **Stat-relevance is move-blind.** `resolve` sums each character's *fixed* stats; the move TEXT is
   never read (lunging == whispering). David's onen.ai version had an LLM *first pass* that reads the
   move and decides WHICH stats it engages. Likely sweet spot: a **hybrid** — an LLM picks the
   relevant stats per move, then dice+stats settle it (relevance = judgment, outcome = mechanics, one
   call).
2. **The torus is under-used.** Today it only guarantees a *next-toucher*; the live field does no
   resolution work. "Maximise" = the field *participates* — many concurrent minds deriving /
   cross-checking / voting the outcome; a soliton carrying a richer evolving state than a single
   verdict. The gap: **"a live field exists" vs "the live field collectively resolves."**

## David's rulings (38.7)
- **No Author-as-resolver** — the RULE resolves (NOMAD: stats + dice + world-flavour). `submit` =
  passive character intention; **`commit` = the character's ACTIVE "resolve me by the rules + give
  me my personal account."** The Author face edits canon only (places / set-pieces), never a contest.
- **Triggers are one lazy mechanism** — resolution is computed by whoever next touches the substrate;
  the trigger is just the condition (will = commit · count = n-threshold · time = time-window). The
  torus supplies the touchers; a cron is the *synthetic* toucher for a thin/empty room or a forced
  tempo. time-window's resolver = the next arriver after the deadline, whose move opens the next
  window — so it is an implicit **commit** of the prior beat (time-window IS commit, clocked by arrival).
- **batch → flow** (the torus shift): today submissions BATCH into a window and resolve as a set (a
  contest is relative). The torus invites FLOW — each submission interacts with the *standing* weave
  immediately (live others' current moves + world-so-far), renders to the user, records to the
  character's `history` shell (+ admin to the S/T/I blocks).
- **Candidate that combines the best:** keep a mechanical verdict as the **SKELETON** (shared anchor,
  free coherence) + braid the **NARRATIVE** sequentially across the live population (chinese-whispers
  on the *telling*, not the outcome). David's three floated models: vote (N derive + vote by
  criteria), single-synthesis (one LLM plumps — risks the confabulation the rule prevents),
  chinese-whispers (sequential build — torus-native, fun, drift-prone).

## Discipline
The commons is LIVE + PUBLIC and a human RPG test may be running on it (`docs/opener-human-test.md`).
Don't redeploy / seed / clobber the commons or keel's `upperton-*` blocks without David's ask. Don't
touch the Track A WIP (`interface.html`, `membrane.py`, `keyring.py`, `sign.py`). Map any new
mechanic to a `biome.json` current. Build locally + model-free where you can; the player's app pays
for cognition in production — don't burn David's mobius key (`scene.run` / `fold._call` = Sonnet on
his key, bench only).

## First move
Design before code: read the two open problems, run `vapour-torus.py` to feel the field, then propose
to David — (a) where stat-relevance should live (the hybrid?), and (b) what the live field actually
DOES at resolution. The discovery is done; the implementation is the trick.
