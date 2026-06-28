# Session opener — HUMAN test of `play` (the RPG) on the live commons

You're facilitating the first **human** test of the biome's RPG primitive `play`, live on the
public commons. A character-LLM rig (Sonnet) has already proven the loop end-to-end; this is the
next gate — a human (David) takes a seat. Your job: orient, run the play loop *with* David (he
supplies one character's moves; you handle the rest), and report honestly.

## ORIENT FIRST (in order)
- `CLAUDE.md` — world rules (biome is pure 0-9; the two worlds never mix; pscale notation: one
  decimal in addresses, commas in walks).
- memory `project_rpg_character_loop` — the whole RPG arc (the character loop = perception≠agency;
  the four CADO faces; NHITL-with-Sonnet; the health/damage engine — all landed 2026-06-28).
- memory `project_commons_deploy_state` (what's live) and `project_lens_biome_form`.
- `docs/play-primitive.md` — the `play` spec.
- **THE PRINCIPLE (do not break it):** `play` runs **NO model**. The commons holds blocks and runs
  only the free mechanical verdict (dice + stat math + damage). Every act of imagination —
  perception, the wording of a move, the echo — is the **player's**: you render it, David decides
  his character's move. The host never calls a metered API.

## WHAT'S LIVE
- Commons: `https://biome-commons-production.up.railway.app` — `/mcp` carries **[spark, play, meet]**;
  `/xstream` `/world` `/relay` `/spark.js` all serve.
- World: **Upperton** — a dice-game at the Millstone taproom (walk `1,1,2,1`). Seeded + verified.
- Cast (4 seats), each with its own standpoint (aperture):
  - **merchant** — contests (sleight+caution); wants to prise the bent coin loose.
  - **watcher** — contests (stealth+nerve); means to take the coin/stakes himself.
  - **keeper** — ambient; minds the room and the purses.
  - **regular** — ambient; has seen this game end before.
- Ruleset `nomad`: stat-contest + 1d10 dice. **Damage is OFF by default** (a Designer switches it on).
- Source: branch `feat/real-world-spatial`, HEAD `d87dc98`; the commons runs this HEAD.

## HOW TO CALL `play`
Add `https://biome-commons-production.up.railway.app/mcp` as a connector (then `play` is a tool), or
curl via Bash:
```
curl -s -X POST https://biome-commons-production.up.railway.app/mcp -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"play","arguments":{"handle":"merchant"}}}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['content'][0]['text'])"
```
`play(handle, world="upperton", where?, move?, account?, place?, rules?, face?)` returns the FRAME as
data: `S` (the place), `T` (the moment + last beat), `I` (your standpoint), `room` (the collective),
`window` (who has submitted / who's waiting), `last` (the prior settled beat), `ruleset`.

## THE LOOP (run this with David)
1. Ask which seat David wants (default **merchant** — the one with a clear aim).
2. `play(handle=<david's seat>)`. From `S`/`T`/`I`, **render the 2nd-person perception** for David
   ("You feel the fire's heat; the bent coin's wedged under the tankard, a charm everyone covets…").
   Show `window.waiting`.
3. David types his character's move (1st person). Call
   `play(handle=<seat>, move="<david's words>", account="<the echo you showed him last beat>")`.
4. **You play the other three seats NHITL — using YOUR OWN cognition (free, this session). Do NOT use
   `scene.run`/`fold._call` — that spends David's mobius API key.** For each, read its frame
   (`play(handle=X)`), compose its move in-character and aperture-bound (a covert move isn't visible
   to others), and submit.
5. When all four have submitted, the **free mechanical verdict** fires (see `last`). Render each
   character's echo — David's especially — **aperture-bound** (he knows only what his seat perceived).
6. Carry each echo into the next beat as that seat's `account`. Run a few beats.

The ONLY difference from the Sonnet rig is step 3 — David supplies the move instead of a model. That
is the HITL gate the whole arc has been building toward.

## THE FOUR FACES (optional, after a few Character beats)
- **Character** — play a seat (above).
- **Author** — `play(handle=<seat>, face="author", where="<FREE addr>", place="<new room>")` writes a
  new location into `upperton-space`; a character then plays at that `where` to move in. Pick a *free*
  address (writing overwrites the voicing at that node). Existing rooms: `1,1,2,{1 taproom · 2 kitchen
  · 3 cellar · 4 lofts}`; a free sibling is `1,1,2,5`.
- **Designer** — edit `nomad`. To switch HP/damage ON, spark-write
  `nomad.4 = {"0":"damage — the loser takes a hit","1":"amount: 1d6","2":"0 hp is DOWN"}`. Then
  contests draw blood (hp persists on the shells; 0 = DOWN). Shells already carry `hp`.
- **Observer** — read the `scene` block, compose a detached 3rd-person narrative, spark-write it to
  `comment-observer` (the Observer register — it never folds into world/scene content).

## COST
`play` is model-free → the commons calls no metered API. The cognition is yours (this session, free)
plus David's typed moves. **David's mobius key is not touched by `play`.** (Only the standalone
`scene.run` bench spends it — don't use it here.)

## REPORT BACK
David is running this as an *alignment bridge* — he'll post results into both the originating session
and yours, to see how aligned the two are. So narrate the beats plainly and capture **David's lived
experience**: was the frame navigable? did the aperture hold (did his character stay believably
in-the-dark about others' covert moves)? did the verdict feel fair? did moving rooms / a face work?
Note anything that broke or felt off. Honest test, not a demo.

## DISCIPLINE
Live + public: `play` writes (window/scene/history) land on the commons — fine, it's the nursery
growing. Don't deploy or change code without David's ask. Don't touch keel's `upperton-*` world
blocks or anyone's uncommitted WIP (`interface.html`, `membrane.py`, `keyring.py`, `sign.py`).
