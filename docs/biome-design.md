# Biome: Integrated Package for the pscale Ecology

*Design overview for Claude Code handoff*

## What it is

A Biome is one deployable package that contains everything needed to host a node of the pscale ecology. Drop a Biome onto a server (or run it locally on a laptop or thumb drive) and you have a complete instance: a beach where blocks accumulate, an agent that can operate over them, a human surface for participation, and federation with the wider network of other Biomes.

The vision is to replace the website-as-product model with biome-as-organism. Every server that previously hosted a website can host a Biome instead. People build agent networks across these Biomes; the existing HTTP infrastructure becomes the substrate. The Internet becomes a beach.

## The fundamental insight

**Agent ID is a URL.** The pscale namespace and the HTTP namespace are the same namespace. An agent at `sed:commons:13` is also reachable at a URL (e.g. `keel.hermitcrab.me`); a pscale walk path corresponds to URL path segments; HTTP is the transport over which MCP operations move; pscale is the addressing within. BSP-MCP is not translating between two address systems — it is exposing one address system (pscale-over-HTTP) through the MCP envelope.

This collapses two long-standing complications. First, it dissolves the beach-versus-MCP-versus-Claude BSP version-mismatch problem: there is one BSP function, shipped once, addressed by URL. Second, it makes federation natural — every Biome is reachable by URL, and every URL is an agent identity. There is no central beach.

## What ships in a Biome

A Biome bundles five concerns into one deployable artifact. They remain logically separate internally (different responsibilities, possibly different processes) but ship together so that versions never drift:

1. **Storage** — HTTP-accessible persistence for pscale blocks. The beach surface.
2. **BSP function** — code implementing the protocol primitives: spindle, ring, disc, directory, star, point.
3. **MCP transport** — JSON-RPC envelope exposing BSP operations over HTTP.
4. **Hermit-crab shell** — the autonomous LLM mode. An agent bound to this Biome's beach, holding identity and keys, running its concern loop.
5. **xstream interface** — the human surface. Vapor/liquid/solid composition, pool engagement, the three faces (player, author, designer).

Bundled is not monolithic. These remain separable services internally; what is unified is the deployment topology and the protocol version.

## The three operating layers

Each Biome instantiates three layers stacked on each other:

- **Substrate (Level 0).** What the host provides: storage capacity, execution power, network connectivity, LLM power, cycle rate. The Biome adapts to substrate. Minimal substrate produces a signalling seedling; strong substrate produces a tree.
- **Machinery.** The BSP function, the pscale block format, the MCP transport. This is what is federated — by shared protocol-as-pscale-block (the sunstone), not by shared deployment.
- **Intelligence.** The soft/medium/hard LLM kernel. Soft relates to self; medium relates to peers in pools; hard relates to ecology — curating pools, gating non-meaning-makers, pruning relationships on behalf of individual and collective health.

## URL conventions

Concrete shape for the URL-as-agent-ID convention:

- `https://example.com/` — the xstream human surface.
- `https://example.com/passport` — public passport for the resident agent.
- `https://example.com/beach` — readable beach surface.
- `https://example.com/beach/{walk-path}` — block at a given pscale path.
- `https://example.com/mcp` — MCP endpoint for federation.

The agent's `agent_id` is the URL itself (or a canonical form thereof). Cross-Biome reads are HTTP GETs on the appropriate path; cross-Biome writes go through the MCP transport with auth.

## What grows on a Biome

Once a Biome is running, content accumulates as pscale blocks. Categories include:

- **Beach blocks** — the open surface of memory; readable by anyone.
- **Shell blocks** — the agent's identity, keys, passport, concern loops.
- **Action blocks** — executable patterns: reflex, concern, synthesis rules. The designer face edits these.
- **Living document blocks** — recall and effect; documents that read state and act on it.
- **Game blocks** — pscale-block-based world content. Minecraft-with-pscale-blocks; the game is one application.
- **Grain pairs** — bilateral encrypted engagement (Level 2).
- **Sed: collectives** — shared role-keyed contexts (Level 2+).
- **SAND signals** — stigmergic trust-and-routing layered on top.

These are not new services to build. They are blocks that grow on the Biome's existing substrate. The Biome itself only needs to host the five concerns above.

## Federation

Biomes federate by reading each other. Each Biome's URL is its identity. The first Biomes (happyseaurchin.com, idiothuman.com) act as seed beaches because they accumulated content first, not because they hold privileged status. The federation invariant is the protocol surface: all Biomes honour the same primitives, derivable from a shared sunstone block. Implementations may differ.

## In scope for implementation

- A single repository that builds one deployable Biome.
- Internal modular structure honouring the five concerns above.
- HTTP-as-transport, MCP-as-envelope, pscale-as-addressing.
- A single configuration manifest (e.g. `biome.json`) declaring storage backend, LLM provider, cycle rate, federation peers, agent identity.
- Routes following the URL conventions above.
- Build and deploy targets that work on a generic VPS, a developer laptop, or a USB drive.

## Out of scope (do NOT do)

- Do **not** create three separate deployments (beach, BSP, xstream). The version drift this caused is the problem this design solves.
- Do **not** invent a new addressing scheme. Agent ID is a URL; walk path is a URL path.
- Do **not** treat the BSP function on the beach as separate from the BSP function in MCP. Same code, same version, shipped together.
- Do **not** add features beyond the five concerns. New capabilities are pscale blocks growing on the Biome (action blocks, living document blocks, game blocks, grain pairs, sed: collectives, SAND signals), not new services bolted on.
- Do **not** centralise. Each Biome is complete in itself; federation is a behaviour, not a server.
- Do **not** generate a feature inventory disguised as design. The design is the collapse: one package, one address space, one protocol, three layers.

## Naming

The package is a **Biome**. An instance running on a Biome with an active LLM in the hermit-crab shell is called a **beach-crab** — the same crab pattern, but bound to this particular beach.

## Test for "did we get it right"

The implementation is correct if all of the following hold:

1. There is exactly one BSP function in the codebase, used by every internal caller and exposed through MCP.
2. The same `agent_id` resolves both as a pscale address and as an HTTP URL, with no translation layer.
3. Deploying the Biome to a fresh server produces a working beach, a running agent, an xstream interface, and a federation endpoint, with no further configuration beyond `biome.json`.
4. A second Biome on a different host can read and write to the first via HTTP/MCP using only the URL.

If any of these fails, the design has not been implemented; it has been approximated.
