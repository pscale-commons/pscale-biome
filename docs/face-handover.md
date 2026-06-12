# Hand-over — the face session (BYOK chat-face on the collective)

You're building **the face**: an interface where a human engages mobius-3 — the
A·B·C collective — and gets back something qualitatively different from straight
Claude: persistent, multi-perspective, world-bearing. David is about to show
people what he's building; the face (with the filmstrip visualiser, built in a
separate session) is the demo surface. Read `CLAUDE.md` first (two-worlds
boundary, naming rules), then `docs/handover.md` for the full state.

## What exists (don't rebuild)

- **The collective** — `src/agent/` is the spark-speaking mobius-3 source;
  the live run is `~/Desktop/mobius-3-runs/v007/` (A: world, B: rules,
  C: substrate). One pulse = `cd <agent>/agent && python3 kernel.py`.
  A pulse costs ~$0.05–0.10 on the key at `~/.config/mobius/anthropic-key`.
- **The commons** — `https://biome-commons-production.up.railway.app`, serving
  spark over `/mcp` and `/.well-known/biome-beach`. `src/biome/serve.py` is the
  server; shell current 3.6 sanctions custom application endpoints beside the
  canonical ones. `store_http.py` is the client adapter.
- **Bridges** — `src/agent/publish-surfaces.py` (surfaces → commons as
  `surface-mobius-a/-b/-c`), `src/agent/observer.py` (read-only chronicler →
  `chronicle` block on the commons; first entry live: "The First Solid Thing").
- **The window mechanics** — a prompt reaches an agent by landing in its
  `conditions` block (the given); the next pulse folds a response into its
  blocks and `surface`. The kernel reports refused writes and unparsed replies
  into `conditions:9` (the feedback loop).

## The design sketch (one session)

1. **Face = a thin page + one endpoint on the commons** (current 3.6): GET
   serves the page; POST `/face` takes `{prompt, key}`.
2. **BYOK**: the visitor's Anthropic key rides the request and is used ONLY for
   the pulses that prompt triggers — never stored, never logged. State that on
   the page. (David pays nothing for engagement.)
3. **The loop**: prompt lands as a given (a `conditions` digit on the chosen
   agent(s), signed "a visitor through the face"); trigger one pulse per
   engaged agent with the visitor's key (`ANTHROPIC_API_KEY` env per subprocess,
   or refactor `call_llm` to take a key argument); the response renders from
   the agents' updated surfaces + the delta (what changed), not from the raw
   LLM reply — the face shows the WORLD's response, which is the qualitative
   difference.
4. **Where the agents run — ON THE COMMONS (the BYOK insight)**: BYOK means
   the collective needs no standing key — every pulse runs on the visiting
   human's key — so nothing ties the agents to David's machine. The public
   commons service hosts them: the agents' shells live on the Railway volume
   (`/data/collective/…`, beside `/data/blocks`), the face endpoint runs in
   serve.py beside the doors, and a visitor's prompt + key trigger pulses
   in-place. David's machine keeps the local lab line (v007); the public
   collective is a fresh cut (v008) seeded onto the volume — EITHER blank-world
   OR carrying v007's current shells up so the Limen's history is the demo
   (David's call; recommend carrying the Limen — the world is the value).
   The mac-mini remains the $0 self-hosted alternative, but it needs the
   tunnel David previously declined; Railway needs nothing new.

## Constraints (hard)

- Layer discipline: the face is layer-1 infrastructure; world vocabulary stays
  layer 2 (the Limen's states are unplaced/held/fixed — never vapour/liquid/
  solid, which are xstream's words; see CLAUDE.md rule 7).
- Transparency norms hold: the face narrates what it does (whose conditions the
  prompt landed in, which pulses ran, what folded).
- Sovereignty: a visitor's prompt is a *given*, never a write into an agent's
  purpose/surface; agents fold it themselves or don't.
- No xstream vendoring (`src/xstream` is stale reference). If VLS-style
  commit-stages are wanted in the face later, that's a deliberate design step
  with David, not a port.
- Costs are the visitor's (BYOK) — keep a per-prompt pulse cap (e.g. 3).
- **Key handling is a trust contract**: the visitor's key lives in the request,
  is passed to the Anthropic call, and is never stored, logged, or echoed —
  say so on the page, honor it in the code (no key in filmstrip frames!).
- **One pulse at a time per agent**: serve.py is threaded — guard pulses with
  a lock/queue; a pulse takes 30–90s, so the face needs a composing-state
  (Railway tolerates long requests; show progress, don't spin silently).
- **Vandal-resistance is sovereignty + curation**: prompts land only as givens
  (conditions), agents fold or refuse themselves, the steward prunes; if it
  gets rough, the gatekeeper block is the next genome growth.

## Open decisions for the session

- One agent per prompt (route by content?) or all three pulse?
- Streaming vs poll-until-folded (a pulse takes 30–90s — show the filmstrip
  frame composing as the wait state?).
- Where the conversation history lives (a `visits` block per face session?).
- Whether the Observer chronicles face visits (probably yes — it's the story).
