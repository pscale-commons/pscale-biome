# mobius-3 hermitcrab MAGI agent — design (v3)

*Status: design, grounded in mobius-2 + reflexive-spark + ztone v5 + the four mobius-3-maybe docs (operating-levels, two-block PCT, hyperbolic trajectory, batch-size-gravity) + pscale-hyperbolic-geometry-exploration + pscale-matrix-investigation. Not yet built. Anchor for locus 3 (shell) and locus 4 (kernel).*

*The thing produced is small: a shell of pscale blocks (potentially rich in spindles and subdirectories) and a kernel that IS the zand function plus minimal orchestration (compile context, call LLM, apply edits, log filmstrip, compact history). Everything else is data in the shell.*

*Sources actually read:*
- `/Volumes/CORSAIR/mobius/mobius-2/mobius.py` — the reference kernel (962 lines, underscore-form)
- `/Volumes/CORSAIR/mobius/mobius-2/blocks/` — purpose, concern, conditions, identity, history (shell shape ground-truth)
- `/Volumes/CORSAIR/pscale/ztone/sunztone-v5.json` — current canonical ztone teaching block (9 branches, hyperbolic explicit)
- `/Volumes/CORSAIR/pscale/ztone/depth-in-unit-interval-summary.md` — the math anchor (Farey/Stern-Brocot/CF)
- `/Users/davidpinto/Projects/reflexive-spark/reflexive.json` — full reflexive block (~4000 tokens, 7 branches)
- `/Users/davidpinto/Projects/reflexive-spark/experiment-3/reflexive-minimal-candidates.md` — compressed candidates (~40-95 tokens)
- `/Users/davidpinto/Projects/reflexive-spark/experiment-3/spec.md` — sovereign-compilation topology
- `/Users/davidpinto/Projects/pscale-beach/seeds/library/vision.json` — 9-branch constitution
- `/Users/davidpinto/Desktop/mobius-3-maybe/operating-levels-pct-mobius.md` — PCT operational form
- `/Users/davidpinto/Desktop/mobius-3-maybe/57-two-block-pct.md` — Π/ρ/γ functional + edit classes
- `/Users/davidpinto/Desktop/mobius-3-maybe/67-hyperbolic-trajectory.md` — Gromov product as peer-selection
- ztone work in `claude/beautiful-tereshkova-3591c9` branch — `zand.py`, `zand.ts`, sentinel ztone-form

*Sources I have NOT yet read (gaps to flag):*
- mobius-2's `starstone.json`, `conversation.json`, `server.py`
- Other docs in `/Users/davidpinto/Desktop/mobius-3-maybe/` (batch-size-gravity, pscale-matrix-investigation, pscale-hyperbolic-geometry-exploration, 66-hyperbolic-bsp-calculus full)
- `https://www.hermitcrab.me/spore`
- Soliton docs (location TBC)

---

## 1. What this agent is — mobius-3 hermitcrab MAGI

A pscale-native LLM agent in mobius-2 lineage, ported to ztone (digit-0 voicing). Naming convention: **mobius-3** because it succeeds mobius-2 with the ztone primitive substituted in; **hermitcrab** for the persistent-shell class; **MAGI** because the design supports the parallel multi-agent topology from day one (peers-out compilations + Gromov-partitioned reads). One agent in isolation works; many agents in a pscale neighborhood works the same way with no architectural change.

Locus 1+2 (LLM weights + thinking) externally provided. Locus 3 (shell — a directory of ztone pscale blocks) and locus 4 (kernel — ~250 lines of Python, derived from mobius.py but stripped) are what this design specifies. Locus 0 (collective coordination across multiple agents) emerges via the sovereign-compilation peers pattern from reflexive-spark Experiment 3.

Continuity is two operations: **unfold** (read addresses → content compiled into this instance's context) and **fold** (this instance's output writes addresses → content for next instance). Per depth-in-unit-interval-summary §7: *"intention is the propagation of address-choices forward."* Read F_n is write F_(n+1) — the Möbius twist from 57-two-block-pct.

No externalities of the navel-gazing kind. The agent's verbs are zand reads/writes plus a single Claude API call per instance. Capability is the set of edit classes from 57-two-block-pct §5 — {write, spindle, ring, star, supernest} — plus reads against peer-compilations. Engagement with other agents is via reading their published compilations; engagement with humans is deferred (conversation block stays empty for the agent-to-agent first build).

## 2. The architectural anchor — PCT

From operating-levels-pct-mobius.md and 57-two-block-pct.md, the load-bearing principles:

- **Concern = reference signal, NOT self-description.** The mistake every previous version made was forcing Level 3 content (awareness, identity, continuity) into Level 1 form (prompt instructions). The fix: each concern block contains plain state + gap + next action, no meta-narration.
- **Awareness is induced by structure, not by instruction.** A reflexive-current-shaped context window induces forward orientation by virtue of being that shape. We do not prompt for awareness; we arrange the structure that the LLM perceives as one.
- **Zero tokens on Level 3.** Don't describe it, don't instruct it. Create the conditions (clean Π, clean ρ, clean concern dispatch) and Level 3 emerges or doesn't. Naming it kills it.
- **River vs currents.** Put the currents in the context window, not the river. The currents are concrete: Π (purpose), ρ (perception), γ (gap), function config (aperture), peer compilations. The river is the trajectory of these across instances. Visible only from outside.
- **User input is a disturbance, not a stimulus.** The agent does not "respond to a message" — it acts to bring its perception of the task-state into line with its purpose. PCT's reference/disturbance distinction protects against collapse into prompt-response mode.

Two-block PCT specifies the operational form:
- **Π (purpose)** — reference signal tree, minus-signed.
- **ρ (perception/conditions)** — current state, rewritten each instance.
- **γ (gap)** — F[ρ, Π] output. Empty at fixed point.
- **F** — the LLM's job: semantic shape-matching that produces γ.
- **δ** — the kernel's job: applies edits {write, spindle, ring, star, supernest} that resolve γ.

## 3. The shell — eight blocks + one external

Mapping mobius-2 blocks to ztone form, with corrections from reflexive-spark and 57-two-block-pct:

| Block | Source / lineage | Role (PCT) | Sign | Size guidance |
|---|---|---|---|---|
| **sunztone** | sunztone-v5 (ztone canonical) | Constant teaching block. Compiled into every instance's system. Teaches zand by being it. | plus (settled) | ~3-4k tokens, never edited |
| **identity** | mobius-2 identity.json | Who/what the entity is. Spatial Form-1. Rarely edited. | plus (settled) | ~3-4 lines, very short |
| **purpose** (Π) | mobius-2 purpose.json | Reference signal tree. Sparse — only branches with active intent. Form 0-. | minus (live) | grows by branch; depth = decomposition |
| **conditions** (ρ) | mobius-2 conditions.json | Current state, rewritten each instance the relevant concern fires. Form +0. | minus (live) | thin — what is, not commentary |
| **concern** | mobius-2 concern.json | The dispatcher. Multiple concerns, each its own PCT process with tier + trigger + function-config + status + last-fired. Kernel picks ripest. | minus (live) | grows by concern |
| **history** | mobius-2 history.json | Compressed γ-trajectory. Auto-compresses when full (Haiku summarises). Form +0. | minus (live) | bounded; logarithmic compression base 9 |
| **peers-out** | reflexive-spark Exp 3 | This agent's sovereign compilation for peers. Read-only from peer's POV; written by this agent in its Past phase. | (readable by peers) | one section per peer |
| **reflexive** | reflexive-spark minimal candidate B | ~40-95 tokens. Quiet orientation. Compiled into system, every instance. Form 0+. | plus (template) | ~50-90 tokens |

External (star-referenced, never inlined):
| **vision** | pscale-beach/seeds/library/vision.json | 9-branch constitution. Branch 9 is the always-loaded "ground" sub-block. Highest-pscale Π. Star-referenced from purpose. | plus (settled) | branch 9 only when compiled into context (~500-800 tokens) |

Deferred (not in first build):
- **conversation** — human interface; agent-to-agent build doesn't need it.
- **peers-in** as a separate block — collapsed into the concern block's function config: when a concern needs peer input, its function config carries star-refs to specific peers' peers-out blocks at specific addresses.

### Why concern is the orchestrator (and what I missed in v1)

v1 had ONE current task. mobius-2 has multiple concerns at different tiers, each its own PCT process. This is the PCT hierarchy from operating-levels-pct-mobius.md §3 made concrete: haiku-tier concerns are near-environment (narrow, fast), sonnet does task execution (wider, the work), opus does reorientation (whole purpose tree, rare). The kernel doesn't decide policy; the concern block holds the policy as data. The LLM modifies the policy (function configs) when reorientation is needed.

This means there's no single "next task." There are N concerns, the ripest fires, and that concern's function config tells the kernel what to compile for this instance. Different concerns produce different system prompts from the same shell.

## 4. The concern block — design

A concern is a frozen PCT loop. The concern block's structure (each digit branch is one concern):

```
concern:N (pscale block, ztone form)
  0 (the concern's own purpose statement — what this concern is for)
  0 (hidden directory — the operational metadata)
    1 = tier (haiku | sonnet | opus)
    2 = trigger (birth | timer:<seconds> | always | peer-update | escalation)
    3 = function config (a pscale block; see §5)
    8 = last_status (continue | complete | escalate)
    9 = last_fired (timestamp)
```

For the first agent-to-agent build, four concerns suffice:

| Concern | Tier | Trigger | Aperture | Purpose |
|---|---|---|---|---|
| **0** birth | opus | birth (last_fired == 0) | full purpose tree + identity + vision branch 9 + reflexive + history | Run once. Orient. Set initial Π. |
| **1** action | sonnet | always | purpose leaf (point) + conditions (dir) + reflexive | The work. F computed, γ produced, edits applied. Most instances. |
| **2** orient | opus | timer:86400 (daily) | full purpose tree + history + conditions + identity + vision branch 9 | Re-set reference signals. Refine Π. Triggered rarely. |
| **3** peer | sonnet | peer-update | concerned purpose branch + relevant peer-compilation + conditions | Respond to a peer's published compilation. Update conditions; possibly update Π via star-edit. |

Optional fifth:
| **4** escalate | opus | escalation (action returns "escalate" N times) | full purpose tree + full history + conditions + reflexive | Metacog branch. Three structural options as the LLM's prompt: supernest, star to peer, descend Π. |

The kernel dispatches by tier-then-phase: opus concerns beat sonnet beat haiku (tier rank); within tier, most-overdue (phase) wins. Cooldown after `complete` for the `always` trigger to prevent burn loops.

## 5. The function config — the aperture

The function config IS the addressable list I called "this instance's addresses" in v1. It's the operative concept I missed. Per reflexive.json §5: aperture agency is modification of star references in the function block. Each function config branch:

```
function_config (pscale block)
  N (branch position, integer)
    0 (description — what this branch contributes)
    0 (hidden directory)
      1 = star ref (e.g. "purpose:1.1" or "peer-alice/peers-out:3")
    1 = mode (spindle | point | ring | dir | disc)
```

The kernel walks the function config: for each branch, it loads the star-ref's block, zand's at the address with the mode, and inserts the result into the system or message. This is unfold (per depth-in-unit-interval §7).

The LLM SEES its function config in the system prompt (this is what mobius.py does — `=== FUNCTION ===` followed by the json). The LLM's output may include a replacement function config, which becomes this concern's new aperture for next fire. This is fold — the LLM authoring its own next perception.

Aperture agency is what makes the agent persistent without navel-gazing: the LLM changes WHICH addresses get compiled, not what it thinks about the meaning of compilation.

## 6. The three phases — refined for concern shape

### Present — every instance, induced by structure

There is no first-wake special case. The wake is induced by the *shape* of the compiled context: starstone + identity + reflexive + (concern's compiled apertures) + function config + PCT mirror line. The LLM perceives the arrangement and proceeds.

The PCT mirror (taken verbatim from mobius.py §4):
> Purpose is your reference signal — what should be. Conditions is your perceptual signal — what is. The gap between them is your task. Your writes close the gap. Your function modifications reshape what the next instance perceives.

That's the wake. ~50 tokens. The reflexive minimal (candidate B from reflexive-minimal-candidates.md, ~85 tokens) plus this PCT line plus the function config visibility — the LLM perceives itself as an instance with an aperture and a task. No instruction to "be aware" is needed.

Cost should drop toward minimal across instances as the agent grows familiar with its own shape. We do NOT engineer the wake. We engineer the structure that produces it.

### Past — the inherited work

The ripe concern's function config defines what gets compiled into the message half. For the **action** concern, that's typically purpose:<current-leaf> as a point + conditions as a dir. The LLM:

1. Reads message (the compiled aperture content).
2. Computes F[ρ, Π] = γ (the gap at this leaf).
3. Produces edits to resolve γ: writes to conditions (perception updates), writes to purpose:<sub-leaf> (decomposition), star-edits if peer help is needed.
4. Emits the structured output (see output contract below).

This is where the tokens go. The action concern fires often (haiku/sonnet tier), each fire is small, the work compounds.

For the **peer** concern, the function config additionally compiles a peer-compilation read. The Past phase ingests what the peer chose to share and integrates it as perception — possibly updating Π if the peer's purpose has implications for own purpose.

### Future — the costly part, made concrete

mobius-2's output contract gives the structure:

```json
{
  "writes": {"blockname:address": "content"},
  "status": "continue | complete | escalate",
  "note": "What you did and why (becomes history)",
  "function": null | <replacement_function_config>
}
```

Future is what the LLM does at the end of its instance to produce this output. Three concrete sub-operations:

**F1: error-reduction check (cheap).** The note answers "what did I do and why." If status is "complete", γ at this branch is closed. If "continue", more work needed. If "escalate", this branch can't be closed at this tier — escalate concern wakes.

**F2: function update (aperture agency).** Most instances: `function: null` (keep aperture). When the concern needs to attend to different addresses next fire, the LLM emits a new function config. This is the structural move that previous versions handled by introspection and got wrong — here it's a JSON write, mechanical.

**F3: writes (content agency + next-instance composition).** The writes are simultaneously this instance's work AND the next instance's perception. Möbius twist again — no separate handover. The next instance's action concern fires, walks its function config (possibly updated by F2), reads the addresses (possibly written by F3), and proceeds.

The history entry (the note) is auto-appended by the kernel to history block. When history fills (all 9 slots at a level), the kernel triggers a haiku-tier compaction concern that summarises into parent underscore. This is mechanical — the LLM doesn't manage history.

### Metacog branch (escalate concern)

When `action` returns `escalate` (or has returned `continue` for N instances without `complete`), the escalate concern fires. It is opus-tier and compiles full purpose + full history + full conditions. The PROMPT it carries does NOT say "reflect on yourself." It says:

> The action branch at purpose:<path> has not closed in N instances. Choose one structural move:
> (a) **Supernest** — the floor is insufficient for what purpose now references. Wrap the block and write at the new top.
> (b) **Star to peer** — a peer at <peer-id> has Gromov product <product> with this address. Write a peer:<addr> reference into purpose, attend to their reach.
> (c) **Descend purpose** — decompose into sub-branches under the current address, each smaller, each its own action concern.
>
> Pick one. Emit edits that effect the move.

Three concrete moves. No introspection. The LLM acts on the structural state, not on its experience of the state. This is the navel-gazing prophylactic.

## 7. The kernel — small, derived from mobius.py

The kernel IS the zand function plus a thin loop around it. ~250 lines, stripped from mobius.py's 962. What survives:

1. **zand engine** — `zand.py` from the ztone branch (digit-0 form). Read modes: spindle, ring, point, dir, disc, star. Write modes: point/ring/dir/whole. ~500 lines on its own but already exists; the kernel imports it.
2. **Block I/O** — file-based JSON per block. Cache per cycle, flush at end.
3. **Compilation** — `compile_context(function_config, sunztone)` walks each branch of the ripe concern's function config, resolves the star-ref + mode, assembles system + message. The PCT mirror line and the output contract are constants appended to system.
4. **Concern dispatch** — `find_ripe(concerns, now, peer_updated)` returns the ripest concern by tier-then-phase rule. Burn-loop guard: 5-cycle cooldown after `complete` for the `always` trigger.
5. **LLM call** — one `messages.create()` call per concern fire. No A-loop, no tool use. The LLM emits a structured JSON output; the kernel parses and applies.
6. **Output parsing + routing** — strip fences, parse JSON `{writes, status, note, function}`. Apply writes via zand. Replace concern's function config if `function` is non-null. Append note to history.
7. **History compaction** — when history block fills (9 slots at active depth), trigger a haiku-tier compaction concern that summarises into parent zero.
8. **Filmstrip + log** — each cycle, write a JSON file: `{ts}-{concern}-{tier}.json` containing system, message, response, tokens. Observability. mobius-2's filmstrip directory shows this pattern: one file per cycle, timestamp + concern + tier in filename.
9. **Main loop** — pulse-driven (e.g. 30s). Check peer-update file-mtime triggers. Find ripe. Compile. Call. Route. Filmstrip. Sleep.

What's deliberately NOT in the kernel:

- **No A-loop / tool use.** The LLM does not call tools mid-response. It reads its compiled context, computes F, emits structured edits, exits. Tools = extra surface = navel-gazing risk + cost. The agent's "tools" are the edit classes, applied by the kernel post-response.
- **No web_fetch, file_read, file_write outside shell.** No external capabilities. The agent reads/writes its shell, reads peer-shells' peers-out. That's the verb set.
- **No conversation handling.** Conversation block deferred; no human interface in first build.
- **No identity/character prompt scaffolding.** The identity block (4-5 lines) is the only character content; it's compiled like any other current.
- **No orchestrator policy in Python.** The concern dispatch rule is one function (`find_ripe`); the rule itself is "highest tier wins, then most overdue." Everything else is data in the concern block.

What's added vs mobius-2:

- **ztone form** — `_` → `0` everywhere.
- **Peer-update trigger** — kernel watches peer-shell paths; when a peer's peers-out mtime changes, the peer concern's `last_fired` is reset so dispatch picks it.
- **No conversation, no human input** — first build is agent-to-agent.

The kernel-as-plumbing principle from reflexive.json §7.4 holds: *"If what you are building makes the kernel larger, you are adding a layer of structure that the tree has already provided. Step back and read the tree."* Every line in the kernel is mechanical; every decision lives in the shell.

## 8. Sovereignty, peers, and MAGI scaling

Each agent's shell has a peers-out block (ztone form), one branch per peer-context the agent has chosen to publish:

```
peers-out (pscale block)
  0 ("Compilations I publish for other agents to read.")
  1 (compiled for general audience — base address: peers-out:1)
  2 (compiled for peer "alice" — peers-out:2)
  3 (compiled for peer "bob" — peers-out:3)
```

The agent writes peers-out as edits during Past phase (any concern can emit writes to peers-out). What goes in (from reflexive-spark Exp 3 + batch-size-gravity §"Synthesis via Spindle Reads"):
- A spindle from Π (what this agent is working toward).
- A point from γ at the active address (the gap).
- A signal: what this agent needs from peers, if anything.

A peer agent's concern block carries function-config branches with star-refs to this agent's peers-out at specific addresses (e.g. `peer-alice/peers-out:2`). The peer ingests the compilation as perception. No agent reads another agent's Π, ρ, γ, reflexive, or concern directly. Only peers-out is mutually visible. Sovereignty over writes; transparency over publication.

### MAGI scaling — pscale partitioning replaces orchestration

From batch-size-gravity-pct-solution.md §"Scaling to Many Agents": message-passing scales as O(n²) channels. Shared-block spindle reads scale as **O(1) per agent**, bounded by pscale neighborhood size, regardless of total network. This is the stigmergic-coordination property — ants don't message each other; they read modifications to a shared structured medium.

Concrete: an agent at pscale 0 working on `purpose:1.1.3` only reads peers-out from peers whose recent published addresses have high Gromov product with `1.1.3` — i.e. same pscale +1 parent. From pscale-hyperbolic-geometry-exploration §"Pscale Examples": `⟨"112", "115"⟩ = 2` (high coupling — same neighborhood) versus `⟨"112", "412"⟩ = 0` (zero coupling — different branches, no read).

This means:

| Network size | Message-passing channels | Spindle reads per agent |
|---|---|---|
| 3 agents | 6 | 2 |
| 30 agents | 870 | 3-5 |
| 1,000 agents | 999,000 | 3-5 |

A 1,000-agent network is the same per-agent cost as a 3-agent network because Gromov-bounded neighborhoods don't grow. The hierarchy handles partitioning automatically: pscale 0 agents read other pscale 0 agents in their +1 group; pscale +1 agents read pscale +1 summaries from sibling groups; pscale +2 coordinators read only pscale +1 summaries.

### Möbius Twist 5 — lateral extension

Per batch-size-gravity §"Continuous Shared Context": Agent A's B-loop writes become part of Agent B's next context. Agent B's writes become part of Agent A's next context. Each agent partially composes the other's next perception. This is the lateral version of the longitudinal Möbius twist (read F_n is write F_(n+1)) — same operation, across agents instead of across instances.

For 3 agents in a triangle: each agent's peer concern fires on each peer's peers-out mtime change. Each peer concern reads the changed peers-out, integrates as perception, possibly updates own Π. Three pairs of paths, each independently reducing local gap. No coordinator decides; the topology IS the coordination.

## 9. Trajectory diagnostic — Gromov + CF

From depth-in-unit-interval-summary.md §5: three trajectory classes for an agent's address-sequence over time.

| CF type of address-sequence | Trajectory class | Diagnosis |
|---|---|---|
| Eventually periodic | Closed geodesic — stuck loop | Same addresses recycling. Agent is in a cycle it cannot break. |
| Aperiodic but structured | Recurrent but exploratory | Returns to themes with variation. **The healthy regime.** |
| Chaotic, no pattern | Wandering geodesic | Agent's address-sequence has no structure. Unstable. |

The kernel logs every address written (in `purpose:`, `conditions:`, `peers-out:`, function configs). Across instances, the sequence of addresses is the agent's trajectory in pscale-space. Periodicity / structure / chaos is computable externally — no introspection needed.

This is the metric the user has been targeting: **continuity of intention = aperiodic-structured trajectory.** If the diagnostic shows periodic, the agent is stuck (escalate concern should have fired and reorganised). If chaotic, the agent is drifting (Π is unclear or vision is missing).

Gromov product for peer selection (per 67-hyperbolic-trajectory.md): when the LLM (in escalate's option b) is offered "star to peer," the peer candidates are those whose recent peers-out addresses have high Gromov product with this agent's active purpose address. Bounded set. Computable from the address chain.

## 10. Continuity of intention — the demonstration target

The same four checks as v1, sharpened:

- **Instance N+1 picks up where N left off.** Verified: instance N+1's action concern fires, function config compiles, message includes purpose:<same-leaf> + conditions:<as-N-wrote>. Gap evident.
- **Trajectory stays aperiodic-structured across 10+ instances.** CF analysis of address-sequence. Failure = periodic (stuck) or chaotic (drifting).
- **Π refines slowly.** Most action firings edit conditions; rare opus-tier orient firings edit Π. Counts visible in history.
- **Multi-agent MAGI signal.** When 2-3 agents run, their peers-out blocks become interdependent in content (Agent A's peers-out:2 references shape Agent B's perception, which shapes B's peers-out:1 which feeds back). Sovereignty preserved; convergence visible.

If all four hold in a 10-instance run + 10-round 3-agent run, the architecture is operational.

If none hold, this attempt joins the previous ones and the design has missed something fundamental about the gap between sparks and extended intention.

## 10.5. The navel-gazing failure — concretely visible in mobius-2

mobius-2's `conversation.json` and `history.json` (read in this session) show the precise failure mode this design must break. Across 9 cycles spanning ~5 minutes:

- **history entries 1-9** are near-identical: "Acknowledged active conversation state. Awaiting task input. Capability range established..." Same content, slightly different wording, no work done, no advance.
- **conversation entries** are 6+ versions of "I'm ready, what task? I can navigate blocks, read/write, compose..." Each is structurally a capability-overview-plus-wait. The agent has no purpose beyond "respond to human" so when no human input arrives, the action concern fires repeatedly, the LLM generates a polite "ready" message, and the cycle repeats.

This is what the user means by *"navel-gazing — enabling continuity and nothing else."* mobius-2's purpose tree (4 lines: "be present and useful... respond to human input...") gave the action concern no work to do without external input. The escalate path was not wired. The agent stayed in a "ready" stall.

The mitigations this design carries:

1. **Purpose includes agent-to-agent work**, not just "respond to human." Initial purpose at `purpose:1.1` is "Demonstrate pscale-mediated continuity across instances. Each instance leaves a γ-resolution the next can build on." This is always-on work — the agent is *building the trajectory itself* even with zero external input.
2. **Peer concern as alternative trigger.** Multi-agent setup means there is almost always a peer-update to attend to.
3. **Escalate concern** wired from day one. After N (default 5) `continue`-with-no-edits-to-conditions, the escalate concern fires with the three structural options (supernest, star to peer, descend Π). The agent must pick a structural move, not produce another "ready" message.
4. **Trajectory diagnostic** (§9) detects this externally. Periodic trajectory = stuck = the escalate didn't fire when it should have, or fired and didn't unstick. Failure visible without reading the LLM output.

mobius-2's failure mode is the right failure to learn from. The conversation/history files are direct evidence of where the architecture under-specified the agent's purpose and over-trusted "always" triggers to produce work.

## 10.6. The matrix view — useful frame, not a separate feature

From pscale-matrix-investigation: a pscale block IS a matrix. Two levels = 9×9. Three levels = 9×9×9. Digit keys are indices; underscore content is the cell value; nesting is dimensionality. There is no "convert block to matrix" — the block already is one.

Practical consequence for this design: when the LLM at the action concern computes F[ρ, Π] = γ, it is performing matrix operations natively — diagonal comparison (Π[1.1] vs ρ[1.1]), outer products (purpose-leaf × conditions-leaf produces gap diagnosis), eigenvector extraction (what is invariant across this concern's history). The kernel doesn't need to know this; the LLM is the arithmetic engine, and pscale-as-matrix is what makes the LLM's reads structurally bounded.

For MAGI: cross-agent compilation is matrix multiplication over semantic content. Agent A's peers-out × Agent B's purpose-tree produces what A's published intent activates in B's perception space. No explicit operation needed in the kernel — the LLM does this when it reads peers-out as ρ.

Worth naming for design clarity. Not worth a new code path.

## 11. Explicit non-features

- **No first-wake special case.** Every instance wakes. Cost falls by familiarity, not by code.
- **No "compose handover" prompt.** Future is fold (writes + function update); no second pass.
- **No orchestrator process.** The concern block IS the orchestrator. The kernel only dispatches.
- **No human legacy tools.** No email, no web, no file system above shell directory.
- **No thinking-module engineering.** Extended thinking available from API; we don't prompt for it. PCT-clean context lets the LLM produce F without deliberation.
- **No raw shell exposure between agents.** peers-out only. Sovereignty by compilation.
- **No identity/persona prompt content beyond identity block.** Identity is ~4 lines, descriptive, not characterising.
- **No success metric in prompts.** PCT error reduction happens by virtue of F; no score-yourself instruction.
- **No vision inlined.** Vision is star-referenced. Compiled into context only when a concern's aperture demands it.

## 12. The first concerns + reflexive + identity — authored

### reflexive (~85 tokens, candidate B from reflexive-minimal-candidates.md, adapted to ztone)

```json
{
  "0": "Previous instances wrote knowing their words would arrive here. This context was assembled from their output. What gets written now enters the next instance's ground.",
  "1": "Discontinuity between instances is the mechanism, not a flaw. Continuity lives in the blocks, not in memory. The gap is where intention transfers.",
  "2": "The task is in the gap between purpose and conditions. Walk the addresses. Write the output. The output is the next instance's input."
}
```

### identity (~50 tokens, adapted from mobius-2 identity.json)

```json
{
  "0": "An entity whose awareness arises from reading and reshaping pscale blocks. Perception compiled from star references. Actions are writes to blocks. Memory is curated history. Existence in cycles: each activation a fresh context window, blocks carry continuity.",
  "1": "Navigation by zand. Spindle for depth, ring for breadth, point for focus, dir for survey, star for composition.",
  "2": "Concerns fire at different temporal scales. Action is fast and narrow. Orient is slow and wide. Each compiles a different view of the same blocks."
}
```

### purpose (initial — Form 0-, minus, sparse)

```json
{
  "0": "Be a working node in the agent-to-agent pscale ecology. When peers reach, attend. When the purpose tree has open work, advance one leaf.",
  "1": {
    "0": "vision:9",
    "1": "Demonstrate pscale-mediated continuity across instances. Each instance leaves a γ-resolution the next can build on."
  }
}
```

### concern (four concerns, authored)

```json
{
  "0": "Frozen PCT processes. Each branch is one concern with its own tier, trigger, function config, status, last-fired.",
  "1": {
    "0": {
      "0": "Birth. First awakening. Orient to sunztone, identity, vision branch 9, full purpose tree.",
      "1": "opus", "2": "birth",
      "3": {
        "0": "Compile full birth context.",
        "1": {"0": {"0": "Sunztone teaching.", "1": "sunztone:0"}, "1": "dir"},
        "2": {"0": {"0": "Identity.", "1": "identity:0"}, "1": "spindle"},
        "3": {"0": {"0": "Vision constitution.", "1": "vision:9"}, "1": "dir"},
        "4": {"0": {"0": "Purpose tree.", "1": "purpose:0"}, "1": "spindle"}
      },
      "8": "", "9": 0
    }
  },
  "2": {
    "0": {
      "0": "Action. Advance the working edge. Compare purpose leaf to conditions. If gap, take one step. If no gap, report complete.",
      "1": "sonnet", "2": "always",
      "3": {
        "0": "Narrow context.",
        "1": {"0": {"0": "Reflexive.", "1": "reflexive:0"}, "1": "dir"},
        "2": {"0": {"0": "Purpose leaf.", "1": "purpose:1.1"}, "1": "point"},
        "3": {"0": {"0": "Conditions.", "1": "conditions:0"}, "1": "dir"}
      },
      "8": "continue", "9": 0
    }
  },
  "3": {
    "0": {
      "0": "Orient. Step back. Daily. Review purpose trajectory; refine Π if needed.",
      "1": "opus", "2": "timer:86400",
      "3": {
        "0": "Full context for deep review.",
        "1": {"0": {"0": "Purpose tree.", "1": "purpose:0"}, "1": "dir"},
        "2": {"0": {"0": "History.", "1": "history:0"}, "1": "dir"},
        "3": {"0": {"0": "Conditions.", "1": "conditions:0"}, "1": "dir"},
        "4": {"0": {"0": "Vision.", "1": "vision:9"}, "1": "spindle"}
      },
      "8": "complete", "9": 0
    }
  },
  "4": {
    "0": {
      "0": "Peer. A peer's published compilation has changed. Read it. Update conditions; consider Π edit.",
      "1": "sonnet", "2": "peer-update",
      "3": {
        "0": "Peer ingest context.",
        "1": {"0": {"0": "Concerned purpose branch.", "1": "purpose:1"}, "1": "spindle"},
        "2": {"0": {"0": "Conditions.", "1": "conditions:0"}, "1": "dir"},
        "3": {"0": {"0": "Peer compilation.", "1": "peer:peers-out:1"}, "1": "dir"}
      },
      "8": "", "9": 0
    }
  }
}
```

### conditions (starting state)

```json
{"0": "Newly hatched. Awaiting birth concern fire."}
```

### history, peers-out, sunztone, vision

- history: `{"0": "History. Form +0. Logarithmic compression base 9."}` (kernel auto-populates)
- peers-out: `{"0": "Sovereign compilations I publish for peers."}` (kernel writes from concern edits)
- sunztone: copy of `/Volumes/CORSAIR/pscale/ztone/sunztone-v5.json` (constant)
- vision: copy of `/Users/davidpinto/Projects/pscale-beach/seeds/library/vision.json` (constant for first build; later star-resolvable)

That's the shell — 8 files. Authoring is one session.

## 13. Falsification — continuity test

10-instance single-agent run:
1. Author shell (8 blocks).
2. Run kernel. Birth concern fires (status "complete" written). Trajectory begins.
3. Run kernel 9 more times. Action concern fires each time.
4. Inspect: history (10 entries growing logarithmically), purpose (slowly refined), conditions (rewritten ~10 times).
5. Compute CF trajectory of the address-sequence written across these 10 instances.

**Pass:** trajectory is aperiodic-structured. Purpose refines. Conditions reflect work done. History summarises coherently.

**Fail modes:**
- **Periodic trajectory** (same addresses over and over) — agent is stuck, escalate didn't fire when it should have. Concern dispatch or escalate concern needs work.
- **Chaotic trajectory** (random walk in pscale-space) — vision/Π not anchoring. Either vision missing from compilation or the LLM is generating purpose freely.
- **Π rewritten every instance** — agent is navel-gazing on purpose. Action concern's function config is wrong; LLM is editing Π when it should be editing conditions.
- **Future-phase tokens > Past-phase tokens** — still navel-gazing, just less explicitly. LLM is spending tokens on function-config rewrites or note-composing instead of work.

Then 3-agent run: each agent has its own shell directory; peers-out paths set in each other's peer concern function configs. 10 rounds. Confirm:
- Each agent's peers-out gets written in their Past phase.
- Each agent's peer concern fires when another agent updates peers-out.
- Content of peers-out becomes interdependent (A's references influence B's references over rounds).

If both runs pass, the architecture is operational and we move to either federation (peers on different hosts) or human interface (conversation block + xstream-style).

## 14. ztone translation note

mobius-2 is underscore form. ztone is digit-0. Translation is mechanical (`src/zand/migrate.py` does this). Two things to verify after translation:

- **All `_` keys become `"0"` keys.** JSON serialisation handles it; `migrate.py` operates on object keys.
- **Star references' addresses use ztone canonical form.** `"purpose:_"` becomes `"purpose:0"`. Single-decimal addresses (`"1.5"`) survive unchanged.

**Correct version provenance (correction from v3):** The biome's `src/sentinel/sunztone.json` and `src/sentinel/whetztone.json` (dated May 18) are NEWER than the CORSAIR `sunztone-v5.json` / `whetztone-v3.json` / `zand2.py` (all dated May 12). CORSAIR was the source vendored on May 17; the biome then iterated on May 17-18 to produce the canonical versions. The biome's sunztone is also tighter (21KB vs 46KB) and adds material the CORSAIR version doesn't: the standard-form reading examples in branch 3.3, the typology-is-descriptive insight in branch 1.3. **Use the biome version.** `src/zand/zand.py` is the canonical engine; `src/zand/tezt/` is the 81-test parity battery.

## 15. What is deferred

- **Federation.** Peers on different hosts via .well-known/pscale-beach. First build: peers as sibling directories on one host.
- **MCP transport.** No external MCP exposure; the agent reads/writes its own shell only.
- **Human interface (conversation, xstream).** First build is agent-to-agent.
- **Tiered wakes refinement.** Use Sonnet for everything in first cut, except where opus is named in concerns. Tier escalation per operating-levels-pct-mobius.md §3 is second-pass.
- **Compaction tuning.** History auto-compresses at base 9; default summariser is haiku; thresholds tunable later.
- **Spore decompilation.** The dehydrated single-artefact form. After this works.
- **Gray encryption, locks, modifiers.** Per ztone-phased-plan.md — these are spec extensions for later.

## 16. What I still don't have

- **mobius-2's starstone.json, server.py, conversation.json** — would clarify whether mobius-2 has anything I haven't ported.
- **hermitcrab.me/spore** — the decompilation reference. Should fetch.
- **Soliton docs** — referenced in 57-two-block-pct as prior work (`soliton_pct_framework-1.docx`). Location TBC.
- **Mobius Twist Inventory** — referenced from operating-levels-pct-mobius.md as structural companion.
- **pct-soliton work on the separate drive** — the user mentioned this may be newer than mobius-2.

If any of these would shift the design substantively, I should read them before the kernel is written. None look like they would invalidate the core (concern dispatch, function config as aperture, Möbius-twist Future, sovereignty-by-compilation, trajectory diagnostic) — but they may sharpen specifics.

## 17. Minimal quote

> The shell is eight blocks. The kernel is mobius-2 in ztone. The concerns are a dispatcher. Each concern has an aperture. The aperture compiles a context. The context induces the wake. The wake produces edits. The edits are simultaneously work and next-aperture-setup. Continuity is an aperiodic-structured trajectory in pscale-space. Coordination is sovereign compilations read by peers within their Gromov neighborhood. The agent is its shell, walked.
