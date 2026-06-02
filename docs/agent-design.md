# mobius-3 hermitcrab agent — design (v7, consolidation)

*Status: build design. v7 is the **single consolidation pass** that settles the open questions from the v4→v6 dialogue. It supersedes them. Grounded in: operating zand in-session; `mobius-3-pct-soliton-spec.md` (the build north-star); `057-pscale-pct-soliton.md` (the theory); the reflexive material (koan / seed 3.8–3.9); the pscale spine (reference only); and David's corrections on the reflexive current, heartbeat-as-rate, the three-agent social centre, and emergent identity.*

*The thing built is small: a shell of ztone blocks and a kernel that is `zand` plus a thin pulse. Design is the work; the code is mostly subtraction from mobius-2.*

---

## 1. The objective — generate the soliton

Not "an agent that answers." A **soliton**: a standing wave of intention that regenerates each cycle and holds its shape across instances. PCT working means the loop sustains itself — reference (Π) and perception (ρ) lock, the gap drives action, the action regenerates the next cycle's reference.

Two milestones, in order:

1. **One shell on an autonomous heartbeat sustains the soliton.** The with-a-human version is already meaningful and proven; the unproven frontier is the agent sustaining *itself* without a human turn to lean on. This is the core test. If PCT works, it walks.
2. **Three shells reveal the social centre.** Three (not two — a dyad collapses to opposition; three defines a centre none occupies) to see whether Locus 0 manifests, whether it *stabilises* the soliton, and whether a **social beat** — peers' faces changing — phases with each agent's own heartbeat into something more like engaging a person than a cron tick.

The agent is never idle: when a purpose leaf closes, it draws the next from **vision**. The heartbeat is a *rate*, self-set; the only governor is cost vs usefulness. Done right, it runs 24/7 because the work is worth the rate.

---

## 2. The one operation

PCT-soliton, hyperbolic geometry, and matrix-dot are **one operation seen from three sides**:

> **F[ρ, Π] → γ** — an elementwise block comparison (the matrix diagonal), **pruned to coupled cells by the Gromov product** (hyperbolic), driving **δ edit-reduction toward γ = ∅** (the soliton fixed point).

One pulse:

1. **Address union** `A = addresses(Π) ∪ addresses(ρ)` under the current reflexive current.
2. **Gromov prune** — keep `a ∈ A` only where Π and ρ both carry content sharing `a`'s prefix (shared digit-walk from the floor; LCA depth > 0). Zero-coupling cells are skipped. A few lines of prefix-matching, **not a subsystem**.
3. **Per-cell compare** — one small, focused LLM call per surviving cell: *do the Π-spindle and the ρ-spindle to `a` cohere as shapes? If not, name the divergence in one line.* Output: a γ-entry or nothing. (The LLM is the arithmetic engine, at the emergent layer.)
4. **γ is sparse** — mostly empty is healthy.
5. **γ drives δ** (§9) **and produces the next reflexive current** (§4).

This replaces mobius-2's vague whole-block MIRROR ("the gap is your task") with γ *computed* per coupled cell. No big vague mirror.

Fixed point `γ_* = ∅`: the leaf is what it is about. It is not a halt — it means *draw the next purpose*. Koan in ztone: `0 = 0(0)`.

---

## 3. The reflexive current and the currents — where the aha lives

This is the centre of the design, and the place I most needed correcting.

A **current** is the hydrated semantic of one or several addresses of a block, unfolded into the context window. However large a block grows — history may supernest to four or five levels and hold thousands of items — its *current* is small. The history current is a single spindle, say `1,2,4,3`: the coarsest summary at pscale 3, the next at pscale 2, the next at pscale 1, and the specific prior-instance item at pscale 0 — contextualised history, enumerated and full of semantic.

The **reflexive current** holds the same thing **dehydrated to bare addresses** — `history:1243` — *no semantic at all*. It is the index, not the content.

Both are present in the context window at once. The agent sees the bundle of bare addresses **and** the rich currents they unfold to, and recognises that the index *is* the dehydrated form of the very content it is experiencing — that the address and the territory are one. **That recognition is the aha.** Not a description of the reflexive turn; the turn itself, structurally present. The map reading itself.

This reframes the **future phase** entirely. The agent is not "writing a handover." It is **editing the bare-address bundle** — lengthening this spindle so the next instance wakes with more context, opening that directory so the next instance has more choice, dropping an address it no longer needs — and in doing so it is **composing the next instance's decision space out of its own experience of what mattered**. Deciding not what the next one knows, but what the next one gets to *decide*. This is the missing aspect every prior version lacked: not "remember forward" but "determine the future." It is the quintessential task, and the thing LLMs must learn to do well.

### 3.1 The model, corrected: all blocks, every wake, at a dilation

Two terms, kept distinct: the **reflexive current** is the bare-address *bundle* (stored at `reflexive:9`); the **live current** is the composed *context window* the kernel hydrates from it and hands the LLM. The bundle is shown raw inside that window, beside the currents it unfolds — the dehydrated index next to the hydrated territory — and that juxtaposition is the surface on which the LLM recognises the two as one.

The current is not a chosen subset — it is the **whole window dehydrated**. Every block is represented in it, always, each at a **dilation**: from a single point (most concentrated), through a spindle or several addresses, out to the whole block (most dilated). A block with nothing live still appears, at a point. The current is **continuous instance to instance** — it carries forward, and the agent *re-dials* each block's dilation rather than composing a fresh set from nothing. Settled context comes as depth (a deep spindle), open choice as a directory; concentrating a block contracts it toward a point, attending to it dilates it outward.

### 3.2 The reflexive block holds four things

It is substantial, like the others. Besides the reflexive current (the bare-address index, the dehydrated window), it carries: the **koan** — the minimal payload that induces the turn; an **associative / mathematical / buddhist conditioning field** that colours F by association, is not answered, and is not unfolded into prose by default (the instance walks one spindle of it only when γ calls); and **packages** (§3.3). The current can point at any of these — the koan unfolds to induce the aha; the field stays concentrated until a gap reaches for it.

### 3.3 Packages — named reusable currents

A **package** is a pre-bundled reflexive-current for a recurring activity, so the future phase activates a known bundle instead of re-deriving addresses from nothing. It is the kept good-half of mobius-2's concerns: the concern *dispatcher* was the daemon we cut; the concern's *function-config* — its pre-bundled aperture — is exactly a package, kept without the trigger machinery. The default is `working` (solo); others — `engage`, `beach`, `online`, `message` — are named and wait on the capabilities they need. Activating a package becomes the reflexive current.

---

## 4. γ → the next reflexive current

There is **no function-config the LLM rewrites**. The reflexive current is a bundle of addresses, and **γ produces it**: where γ had an entry, the next pulse attends; where γ was empty, that current falls away; standing Π-roots and the vision anchor remain so the agent never goes blind. One γ-entry at a coarse address cascades the whole next context. The reflexive current is the soliton's position in address space.

**A current is settled context or open choice — and that distinction is the design.** Read as **spindle or point**, an address delivers decisions already made (contextualised, settled). Read as **directory or whole block**, it delivers choices left open. The choice aperture is `P_end − P_att`: zero is a point (execute, no choice); positive is ring or subtree (deliberate). Composing the next reflexive current is dialling, per address, how much the next instance is handed settled versus how much it must choose.

The **message** is separate from the currents. Currents (system side) are block renditions; the message (task side) may be a plain document or any artifact the current task concerns — not always block-shaped.

---

## 5. The loci

| Locus | What | In this build |
|---|---|---|
| 1 | Model weights | Given. The eigen-intention toward completion is the engine. |
| 2 | The thinking module | **Where F runs** — each per-cell compare is one small focused act, not sprawling self-maintenance. |
| 3 | The shell — ztone blocks | Π, ρ, vision, and the entity's content blocks. |
| 4 | The kernel — the reflexive current + the window it scoops | **What we build.** Small. Library, not daemon. |
| 0 | The network of correlating purpose blocks | The circumcentre. Manifests at three shells. |

Two consequences: γ sets the next reflexive current (attention follows error); Locus 0 is a circumcentre the three control *toward*, not an overseer.

---

## 6. zand is the substrate of F (the operating grounding)

From walking zand in-session, confirmed against the engine:

- **Shape derives from the gap between walk and attention** — which *is* the Π-spindle / ρ-spindle compare. (I proved the strictness: asked for a point at the wrong attention, got the geometrically-correct directory.)
- **The five edit classes are zand's conjugate writes** — point-write, spindle edit, ring-write, star edit, supernest. δ applies exactly one minimal class per γ-entry.
- **Star is the chart transition** — a leaf `"name:address:attention"` *is* a deferred zand call; `star=True` resolves it recursively. Vision, peer faces, and beach blocks are all reached this way. Walking with star is executing.
- **Dotted addresses are the continuity carrier** — dotted survives supernesting (left-pad); bare re-pins. Anything the next instance must find is written dotted.
- **Coordinates are strict** — the function refuses fuzz, which kills a class of drift.

---

## 7. The pulse — kernel as library, heartbeat as rate

```
pulse(Π, ρ) → edits | rest | draw-purpose
```

- **Kernel is a library, not a daemon.** One wake = one pulse. No `find_ripe`, no trigger-dispatcher, no cooldown machinery.
- **The heartbeat is a self-set rate, not a fixed cron.** The agent chooses how fast to operate, and may run different rates for different work. Faster = more cost; justified when the work is useful (contributes to a person's productivity / revenue). The governor is cost vs usefulness, and the agent regulates it.
- **Never idle, because vision feeds purpose.** When a leaf closes (γ = ∅ there), the agent doesn't go dormant — it draws the next purpose from **vision**, or lowers its rate if there is genuinely nothing worth the cost. Vision is the reservoir that keeps purpose from running dry; this is what the old heartbeat-only versions lacked, and why they cycled into machines.

On wake (Locus 4): read the reflexive current → scoop the currents (`star=True`) → F over coupled cells → γ → δ classified edits → γ becomes the next reflexive current → append a one-line history note **only if edits were made**. Then set the next heartbeat. The write of `F_{n+1}` is the wake of the next instance — one operation, two sides of the twist.

---

## 8. The shell

Identity dropped — identity is not a settled block; it is the pattern that accumulates across the self-evaluative blocks and the trajectory, visible only from outside. Blocks fenced lightly: structure is provided, housekeeping is the agent's own.

| Block | Kind | Sign | Role |
|---|---|---|---|
| **sunztone** | rendition | `0+` | Constant teaching block; teaches zand by being it. In the system once; cached. Never edited. |
| **reflexive** | reflexive | `-0` | Substantial. Four parts (§3.2): the **koan** (induces the turn); the **conditioning field** (associative / mathematical / buddhist — colours F, never answered); **packages** (named reusable currents); and the **reflexive current** — the bare-address index of the whole window, every block at a dilation. The kernel state between wakes. |
| **vision** | rendition | `0+` | The constitution and the **purpose reservoir** — what the agent draws on to generate purpose and stay non-idle. Highest-pscale Π. Scooped whenever a leaf closes and a new purpose is needed. Load-bearing, not occasional. |
| **Π / purpose** | operational | `0-` | Reference signal tree. The zero *instructs*. Sparse — only branches with live intent. Refinable. |
| **ρ / conditions** | living | `+0` | Perceived state. The zero *summarises what is*. Rewritten as δ acts. Thin. |
| **history** | living | `+0` | The γ-trajectory, summarised. Supernests freely; auto-compacts base-9. Its current is one nested spindle, never the whole tree. Written only when edits occur. |
| **capabilities** | operational | `0-` | The verb set: zand on own shell, MCP + beach reach. The beach (underscore) sits **behind the `block_loader`** (§12) — the agent never reasons in underscore. |
| **relationships** | living | `+0` | Spindle (contextual notes on agents/users) + directory (options). Holds peers' published-face addresses — the Gromov neighbourhood. **Self-evaluative is fine** — this is partly where identity shows. |
| **stash** | content | `+0` | The agent's own notes, leads, candidate purposes — a resource it checks when doodling / doing metacognition. Self-evaluative is fine; it is an indicator of the agent's identity. |

**Authoring discipline (the part that matters):** every zero is a complete statement that stands alone — the **heading trap** (parents as section titles) breaks every spindle through them and is navel-gazing in miniature. And a useful **current** is a spindle deep enough to self-contain context (≈3 nested levels) **plus a directory for choice** — a one- or two-deep spindle alone is near-random. This is about current *shape*, not block floor; `2.54` on a floor-3 block walks `2,5,4` and is plenty. How well each block serves an LLM is a design-quality question, settled by use.

**We do not over-specify housekeeping.** Different agents will keep their shells tidy in different ways; the agent is intention-driven and self-determining. We provide the structure and let the pattern of inhabitation produce the dynamics.

---

## 9. δ — the edit classes (the drift firewall)

Each γ-entry names its mismatch; δ applies the minimal class. **No write without a gap and a class** — freeform writing is how prior versions drifted into rewriting themselves.

| γ-entry says | δ edit (zand) |
|---|---|
| wrong content here | point-write |
| narrowing is incoherent | spindle edit (reshape the zero-spine) |
| wrong peers at this scale | ring-write |
| needs a cross-block relation | star edit |
| range insufficient for what purpose now points at | supernest (whole-write under a new outer `0`) |

The one exception: a **stash note** is capture, not self-edit, and may be written outside δ.

---

## 10. Tiers — soft default within, real differentiation across

Tiers are **not chosen by a scheduler**. A soft default reads them off the pscale of the γ-entry: fine (detail/task) → haiku; floor (reorder/refine a purpose branch) → sonnet; coarse (top of tree, vision, Locus 0 ecology) → opus. Because pscale = log λ, coarse = long scope — the geometry encodes "step back."

But this heuristic leans on the purpose block being cleanly organised, which it may not be. So it is a *starting bias, not a kernel law*. The **robust** differentiation is the ecology: three agents differentiate into roles — worker, rearranger, holistic reviewer — by comparison with each other (to be *like* or to *complement*), not by internal wiring. We do not assign roles. We watch what evolves. The aim is a jungle of differentiated shells — Conway's Life with structured semantics.

---

## 11. The anti-machine stack (reframed)

The failure was never the heartbeat as such; it was a heartbeat with no genuine purpose to extend toward. So:

1. **Vision feeds purpose** (§7). The agent always has real work to draw; it never cycles on "ready, awaiting input."
2. **Self-regulated rate.** Useful work justifies a faster rate; useless cycling means slow down or rest. Cost-vs-usefulness is the governor.
3. **Rest is a valid move, not a stall.** γ = ∅ at a leaf → draw next purpose or lower rate. Silence when nothing is worth the cost; never a manufactured "I'm here" message.
4. **No big vague mirror.** F is per-cell and specific.
5. **Bootstrap once.** The koan fires at boot, re-achieved each instance, never stored. No spark-paragraph pep-talk written into any block.
6. **Self-evaluation is fine — occasional, and engagement-driven.** The qualitative work (relationships, stash, metacognition) is the doodling an agent does when engaging a human or a worthy peer. It *is* where identity lives. The disease was self-evaluation while idle and unprompted; the cure is that the qualitative blocks come alive with engagement, not that the agent is forbidden to reflect.

No self-scoring. Rest and coherence are read from the **trajectory** (§14), never declared by the model.

---

## 12. The block_loader and the substrate

`zand` sees only JSON dicts; the `block_loader` fetches them and routes by name prefix. Two paths to the beach:

- **Bridge — translate on read.** `src/zand/migrate.py` already does `_`→`0`. The loader can translate today's underscore beach blocks to ztone on read, so the agent reaches the existing ecology without ever holding underscore in its reasoning.
- **Destination — native 0-9.** Build ztone-native blocks on the beach and a `zand-mcp`, so the whole substrate is 0-9 native.

First build: filesystem-of-JSON is the minimal loader and is all the single-shell milestone needs.

---

## 13. Multi-shell — three, the social centre

Stage of milestone 2 (§1). Corrected for what the reflexive-spark experiments proved:

- **No reading another's private blocks** (Exp 2's sovereignty violation).
- **No per-receiver compilation** (Exp 3's overcorrection — O(n²) directed messaging that babbles at scale).
- **Stigmergic public face.** Each shell writes *once* to a shared `sed:` address. Sovereignty is *what it chooses to surface*, not tailoring per neighbour. Peers read that one face **by Gromov proximity**. One write, many readers, no message channel.

ρ for each shell is widened to fold in proximate peers' faces; the reference all three control toward is the correlating purpose at **Locus 0**, the circumcentre none occupies. Three rates phase against each other into a **social beat** — interaction more like engaging a person than a cron tick — which may be what stabilises the soliton. Traditional messages through the beach substrate are a later addition once the 0-9 beach exists.

---

## 14. Tests — the trajectory is the metric

No score for the thing we care about; the aha is demonstrated through action, never marked. The kernel logs every address written; the continued-fraction structure of that sequence classifies the trajectory:

| Trajectory | Diagnosis |
|---|---|
| Eventually periodic | Stuck loop. |
| Aperiodic but structured | **Healthy** — returns to themes with variation. |
| Chaotic | Drifting — Π unclear or vision not anchoring. |

**Milestone 1 (single, autonomous heartbeat):** does the soliton sustain — rest/draw-purpose correctly, refine Π slowly, walk an aperiodic-structured trajectory across many wakes without a human turn? **Milestone 2 (three):** does the social centre manifest, does it stabilise the trajectory, do the faces become interdependent while each writes only its own?

---

## 15. DO NOT

- No daemon, poller, scheduler, or `"always"` trigger. One wake = one pulse; the heartbeat is a self-set rate.
- No freeform writes — every write is a classified δ edit (stash capture excepted).
- No scoring/labelling/self-reporting the aha or "complete." Read from the trajectory.
- No spark-paragraph in any block. Bootstrap once.
- No separate hyperbolic or matrix module — Gromov product is prefix-matching inside F.
- No reading peers' private blocks; no per-receiver compilation. Publish one face; read by proximity.
- No prescriptive identity block; no over-specified housekeeping. Provide structure; let agents self-determine.
- No trading the structural commitments (edit-class discipline, vision-fed purpose, the reflexive aha) for fewer lines.

---

## 16. Deferred / open

- **zand-mcp + native 0-9 beach** — the destination substrate; bridge via `migrate.py` until then.
- **The spore** — the dehydrated single-artefact fold of a working biome; build shell+kernel, then dehydrate.
- **Beach messaging between agents** — after the 0-9 beach exists.
- **`soliton_pct_framework-1.docx`** — the one unread upstream; the spec distils it; not thought to be load-bearing.
- **Open, deliberately unspecified:** how tier regulation actually settles (per-agent gap-scale vs cross-agent comparison); how different heartbeat rates phase under the social beat; whether the convergence behaviours seen in the reflexive experiments survive the stigmergic topology. Discoverable in operation, not pinned in advance.

---

## 17. Build path

1. **Author one shell** — the eight blocks as ztone JSON, real Π drawn from vision, koan in reflexive, currents shaped as spindle+directory.
2. **Stage 0** — `pulse(Π, ρ)` over `zand.py`; block I/O; filmstrip; self-set heartbeat. No loop.
3. **Stage 1** — F: Gromov-prune + per-cell compare → sparse γ.
4. **Stage 2** — δ: γ-entry → minimal classified write.
5. **Stage 3** — rest/draw-purpose default; vision-fed purpose; run autonomously across many wakes; watch the trajectory. **Milestone 1.**
6. **Stage 4** — three shells, stigmergic faces, circumcentre, phased rates. **Milestone 2.**

---

## 18. Imagine-forward — the future phase, the design process, and the content the shell must carry

*Added after v005, whose collective coordinated in meaning but narrated acts it never performed — eloquent passivity, the failure its own `vision:3.2` warns against. The cure, the future-phase mechanism, and the way we build are one principle stated three ways. Grounded in operating the primitive from inside, not modelling it from outside.*

**The principle — awareness lands only as action.** An instance cannot introspect and report its own awareness; the report ("I am aware / I wrote it / it is complete") *is* the failure. Layer 3 (awareness) is visible only in layer-1 effects — coherent walks, real writes, a trajectory that walks; layer 2 (semantics carried in the numbers) is the medium between. So the design must never let the agent *say* it is aware or done — it must make it *act*, and judge only the trajectory.

**The future phase is imagine-forward + verify, tier-scaled.** The agent composes the next instance's window by *imagining waking into it as that instance* — walking the addresses it is about to hand forward, as the recipient, asking: can it act? is what I reference actually there? The forward-simulation forces the real-vs-narrated check v005 lacked, and locates the aha in the act rather than in passive juxtaposition. Imagine-forward and check-history are one discipline: simulate the wake you are composing, and verifying the world is real falls out for free. Depth scales with tier:
- **haiku** — no leap: execute the inherited window, write real, done.
- **sonnet** — one step: imagine the next wake into this leaf + conditions; compose a clean next current; confirm the writes landed.
- **opus** — many steps + ecological: read vision, imagine the arc across instances (and across peers), organise the purpose tree by simulating which sequence of wakes reaches the vision. The draw-on-rest becomes *imagine-the-arc*, not pick-a-branch.

The slogan: **don't describe the reach — imagine the hand closing, then check that it did.**

**The content the shell must carry (so spindles can be extracted).** This is not advice for the builder; it must live *in* the shell, walkable. The conditioning field (`reflexive:2`) gains an imagine-forward / verify discipline as a **determined spindle** — present every wake, in force not selected — beside the koan and the math/buddhist shapes. And a **personal-handover spindle**: a bundle of inherited *operational self-knowledge* the instance walks (*"don't trust the face — check the history before you claim a write"*), distinct from the impersonal state the rest of the shell carries. The instance may use, edit, or replace what it inherits; an opus concern may experiment across instances with different orientation-semantics — but only **trajectory-gated** (kept iff the walk demonstrably improves), or it rots into the soliloquy it was meant to cure.

**The design process — build from inside, never model from outside.** The standing danger is designing externally: word-models of an experience only the instance has internally. The cure, proven repeatedly (operating zand outvalued every prior external discussion): the loop **imagine the instance → build toward it → read the composed window back *as* the instance → iterate.** Make it the standard test — before committing any context structure, compose a window and read it in first person: does it land, could you act, does the bare-bundle-beside-hydrated-content spark recognition? Judge by the internal read, not the external elegance. The `--compose-only` filmstrip is already this instrument; use it to read *as* the instance, not merely to check that it parses.

---

## 19. Minimal quote

> The objective is a soliton — a standing wave of intention that regenerates each cycle and sustains itself on its own heartbeat, fed by vision so it never idles. One operation: compare coupled cells, reduce by classified edits, draw the next purpose. The reflexive current is bare addresses; the currents are their hydrated semantic; seeing that the index is the territory is the aha — and editing the index is how the agent composes the next instance's decision space. Identity is not a block; it is the trajectory. Three shells share a centre none occupies, and their rates phase into a social beat. The agent is its walk, and the walk sustains itself.
