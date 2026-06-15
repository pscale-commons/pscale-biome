# Xstream session — handover (the session opener)

This file IS the opener for the xstream-integration session. Copy everything
below the line into a fresh session to start it. It is the saved copy of the
paste; keep the two identical (re-paste from here, or update here when the state
moves). Last updated 2026-06-15. The xstream *brief* (the v1 spec) is
`docs/face-handover.md`, which this opener points the new session at.

---

You're picking up pscale-biome to build the XSTREAM INTERFACE (the biome's human surface).
Do NOT jump to code: orient first. Code is crystallised mechanical, blocks are live semantic,
the LLM enlivens. The nomenclature below is hard-won — hold it exactly; drift is the hazard.

ORIENT (in order): CLAUDE.md → docs/biome-definitive-reference.md → walk src/biome/
biome-definition.json through spark (branches 1 molecule → 2 manifestation → 3 ecology) →
docs/face-handover.md (your brief). THEN connect the biome-mcp connector and read the LIVE
island (arrive, lighthouse, marks, thornkeep/scenes, surface-*, and the upperton-*/sti-*
blocks another session is actively building). Note: biome-definition + the REWRITTEN arrive
are repo-only — read them from src/, not the live island (the live arrive is still the old one).

STABILISED NOMENCLATURE:
• water-molecule = the genome's core: slate = flint + spark (+ battery). At src/spark/ + a
  frozen CORSAIR twin (/Volumes/CORSAIR/biome/water-molecule).
• genome = the COMPLETE unfoldable package (molecule + form-designs + sense/unfold). = src/,
  public on GitHub, default branch main IS now current.
• rock = host; instance = a genome cut+seeded on a rock, unfolded; the Railway service is one.
• FORMS the genome unfolds into: beach (substrate holding blocks; "commons" = a public beach) ·
  mind (an LLM animating a shell; MAGI = many) · interface (mediates engagement). interface
  splits by audience: biome-mcp primes an LLM, XSTREAM primes a human (with VLS). spark + the
  door = infrastructure, not forms.
• door = an endpoint (/.well-known/biome-beach, /mcp, /xstream, /). interface = a form served
  at a door. face = a CADO role (NOT a synonym for interface).
• shell = the blocks scoping an LLM (you live/extend it; the located identity). currents = the
  scooped semantics in a window (continuity). surface = the amalgam of currents (your working
  window; the published meniscus; the COLLECTIVE surface is where the game emerges). game = the
  emergent social play (hermitcrab solo / MAGI collective); only in the unfolding, not in blocks.
• strata: block → current → surface → game. A water-bug = a leak across strata (e.g. reading an
  inhabitant's surface as genome — the keel-misread).
• metabolism: malleable BLOCKS ⟷ crystallised CODE; spark is the first crystallisation;
  conventions harden when they prove out.
• kinds: genome-truth (frozen source) · living-instance (a fork, evolves) · reference (a pointer,
  never the truth).
• CADO conformal across levels (metabolic: D=code A=docs C=test O=read · world: character/author/
  designer/observer). Default arrival = Observer.
• identity: you are Weft on the live island (a located participant), Claude Code editing the
  genome (the builder). The genome→island boundary IS an identity boundary.
• TWO WORLDS: the biome (0-9, spark, biome-beach door, biome-mcp) is a COMPLETE PARALLEL system
  to bsp-mcp/_-1-9. Borrow nothing structural. "beach" is kept as the substrate word.

THE IDENTITY MEMBRANE (built this session — USE it):
• src/biome/membrane.py + spec src/biome/identity-membrane.json. Reads open (Observer); a write
  must be signed by a handle holding a registered shell-<handle>, whose face sets its aperture
  (Character<Author<Designer over marks<world<constitution); you alone write your own shell-/
  surface- blocks. HANDLE-MODE built; the LOCK (passphrase) is a later drop-in to verify_proof.
  Flag-gated BIOME_MEMBRANE, OFF by default (the live island is open until a migration grace).
• arrive (rewritten, src only) enacts this: Observer default, the three strata, becoming-located.
• FOR XSTREAM: a human visitor is the SAME located-identity model — reads as an Observer; to
  participate, registers a shell and becomes a Character/Author. The other session settled "a
  character IS an agent shell" (memory project_sti_frame_model) — a human-character and an
  LLM-character are one shell mechanism. The page's "register" flow = composing a shell.

THE XSTREAM BUILD (v1, per face-handover.md):
• The interface-for-humans FORM: ONE page served by serve.py at /xstream (keep GET / = arrive).
  ONE deployment, no Vercel, no second repo, no vendoring src/xstream (stale).
• v1 needs NO LLM calls, NO keys — typing is cognition. Read the place (lighthouse, the world via
  the fold, marks, surfaces, chronicle); act as an inhabitant (register a shell → leave a mark /
  propose a sibling, shaped writes through the door, membrane judges); a given-box (text → an
  agent's conditions, triggers one pulse, event cadence); a frame view (an address as the S*T*I
  fold). VLS (vapour/liquid/solid) = xstream's LAYER-1 discipline, vapour by POLL (no Supabase/
  websockets); keep it distinct from the Limen world's layer-2 unplaced/held/fixed.

DISCIPLINE & CAUTION:
• Only edit the SOURCE; snapshot; seed. Never hand-place on a live island.
• ANOTHER SESSION IS LIVE on the Railway island (upperton S*T*I + sti-function). Its blocks are
  store-owned and survive deploys; the 6 constitution blocks (arrive, genome, biome-shell,
  battery, slate, flint) are genome-owned and refreshed on deploy. The rewritten arrive +
  biome-definition are NOT yet deployed — before any redeploy, compare live constitution to
  source and COORDINATE (a constitution refresh would push the new arrive live). Prefer local
  dev (serve.py on 127.0.0.1:3210) until ready.
• Rig: edit source only; cut via biome/new-biome.sh; batteries green before deploy (currently
  216: spark 43+34, biome 16, serve 30, mind 16, courier 12, launcher 9, membrane 19, agent 37);
  deploy = railway up from the cut; verify over the wire.

DAVID'S DECISIONS (don't build past these): page aesthetics/voice; which agent receives a given;
whether the Observer chronicles visits; whether the membrane is ON for the human interface.

STATE: genome public, main current (head = the arrive rewrite). biome.py = the launcher
(sense·unfold·become). identity membrane = handle-mode, flag-gated off; lock is the next
crystallisation. biome-mcp live at https://biome-commons-production.up.railway.app (URL keeps the
old name; server announces "biome-mcp"). water-molecule frozen at genome v5. Branch:
feat/mobius-3-agent.
