# FAQ

**Do I have to run a server?**
No. `pip install memora-swarm`, paste your key, and you're connected to the hosted relay. It does the
CRDT merge, trust-weighting and Byzantine aggregation. On-prem/self-hosted relay is available on
Enterprise.

**Is it really a drop-in Redis replacement?**
For the shared-memory patterns multi-agent systems use (shared key/value state and numeric
aggregation), yes — with the difference that a malicious writer can't poison the swarm. It is not
a general-purpose Redis (no pub/sub streams, Lua, etc.); it's purpose-built for agent state.

**How many agents can share one room?**
Unlimited. You're billed by semantic ops, not by connections. Idle agents cost nothing.

**What actually happens to a poisoned or lying agent?**
Numeric outliers are down-weighted by the robust mean. An agent that equivocates (tells different
peers different things) accumulates cryptographic evidence and is **convicted and evicted** from
the aggregate — visible live on the monitor.

**What's the guarantee, precisely?**
Up to *f* Byzantine agents in a group of **≥ 2f + 3** members cannot move the agreed numeric
result, and the CRDT state never forks. If **more than f** members collude, they can skew that
group's aggregate — that's the fundamental Byzantine bound, not a defect. Keep honest majorities
per room.

**Are results deterministic across machines?**
Yes. The Byzantine aggregation runs in exact fixed-point integer arithmetic (Q16.16), so ARM and
x86 agents compute byte-identical results. No floating-point drift.

**Which Python versions / platforms?**
Python 3.9+ via a native wheel. Install with `pip install memora-swarm`.

**Does it work with LangChain / CrewAI / AutoGen?**
Yes — Memora is a plain shared-memory backend that slots underneath them. See
[examples/](../examples/).

**Is my data auditable for compliance?**
Every write is signed, attributable to a node, and replayable from an append-only log with
byte-identical roots — designed to support EU AI Act Art. 12/13 traceability. See
[THREATS.md](THREATS.md).

**Is the engine open source?**
The engine ships as a compiled wheel and a hosted service. This repository holds the docs,
examples and paper. The example glue code here is Apache-2.0 — use it freely.

**How do I get help?**
Open an issue in this repo, or reach us via [memora.optitransfer.ch](https://memora.optitransfer.ch).
