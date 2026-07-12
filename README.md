<div align="center">

# Memora

**Byzantine-fault-tolerant shared memory for AI agent swarms.**
A drop-in replacement for Redis in multi-agent systems — where one prompt-injected agent
**cannot** poison the shared state of the other 49.

[![PyPI](https://img.shields.io/pypi/v/memora.svg)](https://pypi.org/project/memora/)
[![Python](https://img.shields.io/pypi/pyversions/memora.svg)](https://pypi.org/project/memora/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

[Website](https://memora.optitransfer.ch) · [Get a key](https://memora.optitransfer.ch/dashboard) · [Live monitor](https://memora.optitransfer.ch/monitor) · [Docs](docs/) · [Paper](paper/)

</div>

---

## The problem

When many agents share one memory, that memory is your weakest link. A single agent that gets
**prompt-injected**, goes rogue, or just malfunctions can write poison that every other agent
then reads and trusts. Plain key-value stores (Redis, etc.) have no defense — last write wins,
no matter who wrote it or whether it's a lie.

## What Memora does

Memora replaces that shared store with an engine that stays **correct under adversarial
writers**. Three layers, one API:

| Layer | Guarantee |
|---|---|
| **CRDT state** | Concurrent writes merge deterministically. The swarm never forks. No locks. |
| **Trust-weighted aggregation** | Numeric contributions are combined by a robust mean that **down-weights** outliers instead of averaging them in. |
| **Byzantine conviction (ACFA)** | An agent that tells different peers different things (equivocation) is **detected and evicted**. Up to *f* liars in a group of ≥ 2f+3 cannot move the agreed result. |

Every write is **signed** by a self-certifying node identity and appended to a **replayable**
log — so any state is attributable and auditable after the fact.

> You aren't paying for message delivery. You're paying for mathematical certainty that a single
> compromised agent can't fork the swarm.

---

## Get your swarm live in 60 seconds

**1. Get a free key** — sign up at **[memora.optitransfer.ch/dashboard](https://memora.optitransfer.ch/dashboard)**
(GitHub or email), then click **Issue key**. You get `opti_sk_...`.

**2. Install**

```bash
pip install memora
```

**3. Connect and use it**

```python
import memora

db = memora.Blackboard(
    "./swarm.memora",          # local append-only log (state survives restarts)
    node_id="agent_12",        # any label unique to this agent
    api_key="opti_sk_...",     # your key from the dashboard
)
db.connect("research-swarm")   # join a room; every agent in it shares one memory

# Shared key/value — CRDT-merged. get() returns the SET of current values.
db.put("best_hypothesis", "H3")
print(db.get("best_hypothesis"))            # -> ['H3']

# Byzantine-tolerant numeric aggregation. submit, then resolve to read the agreed result:
#   resolve(round, f) -> (aggregate_vector, acfa_root, convicted_node_ids)
db.submit_tensor("reward_estimate", [0.71, 0.68, 0.73], round=1)
vector, acfa_root, convicted = db.resolve(round=1, f=1)
print(vector, "convicted:", convicted)      # poisoners are evicted, not averaged in
```

**4. Run more agents** — start the same script on N machines (or N processes) with the **same
`room`** and **different `node_id`s**. They converge on one shared, poison-resistant memory.
**Agents are unlimited** — you're billed by semantic ops, not connections.

**5. Watch it live** — open
**[memora.optitransfer.ch/monitor?key=YOUR_KEY](https://memora.optitransfer.ch/monitor)** to see
your swarm in real time: throughput, agent constellation, and any Byzantine agent getting
convicted and evicted.

There is **no server to run**. Your key connects you to the hosted relay, which does the CRDT
merge, trust-weighting, and Byzantine aggregation for you.

---

## Use it with your framework

Memora is a plain shared-memory backend, so it slots under the agent frameworks you already use.
Copy-paste starters:

- [LangChain](examples/langchain_memory.py) — shared chat/scratchpad memory across a crew
- [CrewAI](examples/crewai_backend.py) — a poison-resistant shared store for a crew
- [Plain Python](examples/quickstart.py) — the 20-line version

---

## Pricing

**25,000 semantic ops free** on signup — unlimited agents, the full engine, no feature gates.

- An **op** is a semantic state transition: a `put()` or a `submit_tensor()`. Keepalive, sync,
  gossip and reads are **never billed**. An idle swarm costs nothing.
- At **85%** of the free allowance you're prompted to add a card so nothing stops mid-run.
- After that: **$0.35 / 1,000 ops** ($0.20 / 1,000 above 2M/month). The **same key** upgrades in
  place — no re-keying, the swarm never stops.

Full breakdown → [docs/PRICING.md](docs/PRICING.md).

---

## Learn more

- **[Architecture](docs/ARCHITECTURE.md)** — how the three layers work, conceptually.
- **[Quickstart](docs/QUICKSTART.md)** — the step-by-step, including scaling to many agents.
- **[Threat model](docs/THREATS.md)** — the attacks Memora is built to survive (OWASP Agentic
  Security, Morris-II self-replicating prompt worms, and more), with sources.
- **[Paper](paper/)** — the ACFA coordinator-free Byzantine aggregation research.
- **[FAQ](docs/FAQ.md)**

---

## License

Apache-2.0 — see [LICENSE](LICENSE). Covers this documentation and the example glue code. The
Memora engine is delivered as a compiled wheel (`pip install memora`) and a hosted service; the
examples here are yours to use, fork, and adapt freely.

Made under the [optitransfer.ch](https://optitransfer.ch) umbrella.
