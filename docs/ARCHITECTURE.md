# Architecture

Memora is one API over a three-layer engine. You call `put`/`get`/`submit_tensor`/`aggregate`;
the engine keeps the shared memory **correct even when some agents are adversarial**. This page
explains *how*, conceptually — no internal source, just the model you need to reason about it.

## The shape

```
   your agents                         hosted relay
 ┌────────────┐   signed, delta-      ┌───────────────────────────┐
 │  agent_1   │──── encoded writes ──▶│  L1  CRDT merge           │
 │  agent_2   │◀─── merged state ─────│  L2  trust-weighted mean  │
 │    ...     │                       │  L3  Byzantine conviction │
 │  agent_50  │                       └───────────────────────────┘
 └────────────┘                                │
       ▲                                        ▼
       └──────── replayable, attributable append-only log
```

Each agent keeps a **local append-only log** (`./swarm.memora`) so its state survives restarts
and can be replayed. Writes are **signed** and sent as compact deltas; the relay merges them and
streams the agreed state back. There is no server for you to run.

## Identity: self-certifying nodes

Every agent has a keypair. Its `node_id` is derived from its public key, so an identity can't be
forged — a write either verifies against the claimed node or it's rejected. This is what makes
the log **attributable**: after any run you can say exactly which node wrote which value.

## L1 — CRDT state (never forks)

Shared key/value state is a **conflict-free replicated data type** (an OR-Set with delta
encoding). Two agents writing at the same time produce a result that both converge to,
deterministically, with no coordinator and no locks. Merging is commutative and idempotent, so
retries and out-of-order delivery are safe. The swarm **cannot** split-brain.

## L2 — Trust-weighted aggregation (outliers down-weighted)

For numeric contributions (`submit_tensor`), a plain average is fragile: one agent submitting
`[9999, ...]` drags the mean. Memora instead computes a **robust, trust-weighted mean** — each
contribution is weighted by how consistent it is with the rest, so a poisoner is *down-weighted*
rather than folded in. Honest agents dominate the result.

## L3 — Byzantine conviction (ACFA)

The hard case is a **Byzantine** agent: not just noisy, but *strategically* lying — telling agent
A one thing and agent B another (equivocation), or crafting values to skew the aggregate.

Memora's ACFA layer (Adversarial Coordinator-Free Aggregation) handles this with:

- **Multi-Krum + Bulyan-style selection** — robust aggregation that provably tolerates up to *f*
  Byzantine contributors as long as the group has **≥ 2f + 3** members.
- **Equivocation conviction (G-Set of evidence)** — if an agent is caught asserting
  contradictory things, cryptographic evidence accumulates and the agent is **convicted and
  evicted** from the aggregate. Eviction is visible on the live monitor in real time.

All of L3 runs in **exact fixed-point integer arithmetic (Q16.16)** — so the aggregate is
bit-for-bit identical on ARM and x86. No floating-point drift between agents, ever.

## The safety boundary (honest limits)

Memora is strong, not magic. What it guarantees and where the edge is:

- **Holds:** up to *f* Byzantine agents in a group of ≥ 2f + 3 cannot move the agreed numeric
  result; equivocators are convicted; CRDT state never forks; every write is attributable.
- **Edge:** if **more than f** of the members in a group are colluding adversaries, they can by
  definition skew that group's aggregate — this is the fundamental Byzantine bound, not a bug.
  Keep honest majorities per room and the guarantee holds.
- Memora secures **shared state**. It does not sandbox the code your agents run or inspect their
  prompts — pair it with your normal application-level controls.

## Further reading

- [Threat model](THREATS.md) — the concrete attacks this defends against, with sources.
- [Paper](../paper/) — the ACFA research behind L3.
