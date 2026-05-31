# mobius-3 agent — session handoff

*Close of the build session, 2026-05-31. The mobius-3 hermitcrab agent is built and its full self-sustaining loop is validated. This doc lets the next session pick up cleanly.*

## ⭐ Start the next session here (read `v004.md` first — it reframes everything below)

v004 (a 20-pulse run) reframed the trajectory: the agent self-sustains but is a **closed loop** — no input, no output, no other; it narrates its own enclosure ("all me-centered"). So **engagement and the reflexive condition are one systemic move, present from the start — not the laddered rungs 3/4 in "Open forks" below.** See `v004.md`.

**Starting prompt (paste to begin the next session):**

> Continuing the mobius-3 pscale-native agent (project: pscale-biome). Read first, in order: `docs/experiments/HANDOFF.md`, `PASSOVER.md`, `v004.md`, then `docs/agent-design.md` §0–7. The agent is committed on `feat/mobius-3-agent`; runs live in `~/Desktop/mobius-3-runs/` (working) + `/Volumes/CORSAIR/mobius/mobius-3-runs/` (frozen seeds).
>
> State: the agent self-sustains — it draws its own purpose from vision and walks (v001–3). But v004 exposed the gap: it's a **closed loop** — no external input, no output, no other; it spins ever-more-elaborate purposes about reaching out and narrates its own enclosure, yet nothing leaves the shell.
>
> What I want now, and do NOT ladder it: bring **engagement and the reflexive condition in together, from the start.** The reflexive turn has a longitudinal half (one instance in a chain — it has this) and a lateral half (one of many agencies, the "between" / Locus 0 — which requires others); they are one systemic move. Concretely: (a) restructure the messy context window to induce the reflexive aha from the start — I've made some progress on the induction, which I'll bring; this changes the input format; and (b) give it real engagement — a genuine input (a disturbance: me, or a peer's published content) and a genuine output (something that actually *leaves* the shell — to the beach, a peer, or me). Open question for us: does solo reflexive-induction (context window) come first, or do reflexive + others arrive together?
>
> Discipline: **operate the primitive, don't theorise about it** — run pulses, read filmstrips, get inside it. Keep the kernel minimal and the agent self-determining. Frozen seed + working copy + source pristine; fixes → source → new version, never patch a working copy in place. Read-only — do not modify: bsp-mcp, pscale-beach, xstream. The beach-crab / GRIT resolvers running on my machine are separate sessions — leave them.
>
> Read the docs, then let's talk through the context-window restructuring + engagement before cutting v005. Don't rush to code.

## Where we are

The agent works. Through v003 the complete loop runs end to end:

> cold-start → walk (realise Π into ρ) → settle (γ=∅) → **draw the next purpose from vision** → walk toward it

Sustained for 11 pulses, the agent drew `purpose:3` ("reach toward the between"), `purpose:4` ("produce the first alignable artifact"), `purpose:5` ("move the artifact to the actual beach") — a coherent forward trajectory advancing through vision's coordination goal. It does not spiral, does not navel-gaze; it regenerates intention from vision. This is the soliton, validated.

## Architecture (read order)

1. `docs/agent-design.md` (v7) — the spec. §0–7 first: the soliton objective, the one operation `F[ρ,Π]→γ`, the reflexive current, the loci, the pulse.
2. `src/agent/shell/` — **locus 3**: 9 ztone blocks (reflexive, vision, purpose, conditions, history, capabilities, relationships, stash). `sunztone`/`whetztone` are the constant teaching in `src/sentinel/`.
3. `src/agent/kernel.py` — **locus 4**: `pulse()` = F (Gromov-coupled Π/ρ compare → γ) → δ (classified edits) → fold; **draw-on-rest** (γ=∅ → opus reaches into vision for the next purpose).
4. `docs/experiments/v001.md … v003.md` — the run-by-run findings.

## The experiment loop + THE RULE

- `./new-experiment.sh "hypothesis"` cuts `vNNN`: a **frozen archive** on CORSAIR + a **working copy** on Desktop. Source stays pristine.
- Run in the working copy; read the run folder directly (no paste); findings → `docs/experiments/vNNN.md`.
- **THE RULE (we slipped once): fixes → SOURCE → new version. NEVER patch a working copy in place.** On v003 the `heartbeat.py` fix was applied in-place mid-run, so v003's *run* is not reproducible from its frozen seed. All seeds + source are intact; do not repeat the slip.

## Current state

- **Source** = clean, all fixes in: vision-fed purpose (draw-on-rest), γ-only edits, runner stop-on-genuine-settle (`status=rest AND γ=0`).
- **v003 working** = 11 pulses of mutation + the in-place heartbeat patch (the slip). Its record stands; it is not seed-reproducible.
- **Seeds frozen** on CORSAIR: v001, v002, v003.
- **Next session: cut v004 from source** and continue cleanly.

## How to run

One-time key: `mkdir -p ~/.config/mobius && echo 'sk-ant-...' > ~/.config/mobius/anthropic-key && chmod 600 ~/.config/mobius/anthropic-key`

In a working copy's `agent/` dir:
- `python3 kernel.py` — one pulse · `python3 kernel.py --compose-only` — inspect the window, no key
- `python3 heartbeat.py --max 10 --interval 5` — fast research run; stops only on a genuine settle
- `python3 digest.py` — read the run at a glance

A `quote>` / `>` prompt in the terminal = an unbalanced quote was pasted; Ctrl-C clears it, nothing ran.

## Open forks

The agent is at the **capability boundary** — it drew purposes about reaching other agents (publish an artifact to the beach) but has no real reach (`capabilities:3.1`, "tools I do not yet hold"). Three forks:

1. **A reach capability** — a real channel (beach / peer / substrate) so drawn intention becomes action. The agent's own purpose-generation is pointing straight at this.
2. **Multi-agent (Locus 0)** — three shells + the social centre, where its trajectory is heading.
3. **Active-aha experiment** — see the lead question below.

## ⭐ Lead question for the next session: input format / context-window structure

David's topic to open with. The reflection that seeds it:

- **frame (xstream) ↔ reflexive bundle = one primitive.** Both are an address-bundle that becomes a context window — a human-authored scope for a game-LLM, a self-authored scope for the agent. Candidate for a substrate `frame` primitive (bsp-mcp — but that repo is read-only here; do not modify it).
- **Static vs active aha.** We currently induce the reflexive moment ONLY statically (the dehydrated bundle sits passively in the window). David's claim: the aha is located in the *processing moment* — the act of the bsp read that makes the koan/bundle "make sense" — not the passive context. The koan is inert words until the bsp call reads its hidden directory and it is *experienced*.
- **Loci cross-correspondence.** locus 1 (weights) & 3 (shell) are static/precomposed; locus 2 (thinking) & 4 (compose) are processural/time-taking. Induce the reflexive moment in BOTH modalities, minimally.
- **Single-package-pointer.** `reflexive:9` could hold ONE pointer to a `reflexive:8` package (cheap re-dial); the kernel resolves it and still shows the bundle (passive aha preserved). Efficiency and static aha are not exclusive.
- **Active reflexive induction (v004/v005 experiment).** 2–3 minimal tool-calls at wake (koan-read, dehydrated↔hydrated correlation, peer-concurrency, maybe eigen-intention) to locate the aha in the processing — bounded (never the majority of the budget, which belongs to past-action + future-decisioning), and **ablated** (run with/without, compare trajectory coherence — the only honest measure).

The specific next question: **the format of the input and the structure of the context window.** Start there.

## Known small issues

- The opus draw occasionally emits non-JSON (one parse-failure in v003 pulse 6; the kernel fell back gracefully). Firm up the draw prompt's JSON discipline if it recurs.
- The agent often sets `status=rest` on work pulses (its own self-assessment); the runner correctly ignores that and stops only on `γ=0`.

---

*Next instance, read in order: this handoff → `docs/agent-design.md` §0–7 → `docs/experiments/v001–3.md` → `src/agent/kernel.py`.*
