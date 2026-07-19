<div align="center">

# Memora

**Byzantine-fault-tolerant shared memory for AI agent swarms.**

### Your security stack watches the network. Nothing watches what your agents tell each other — or whether the memory they share is still believable.

Memora is the missing layer — shared memory where one compromised agent is **mathematically unable
to fork or poison** the state of the rest, every write is **signed, attributable, and exactly
replayable**, and the memory itself **knows when it can't vouch for a value** and escalates it to a human.

[![PyPI](https://img.shields.io/pypi/v/memora-swarm.svg)](https://pypi.org/project/memora-swarm/)
[![Python](https://img.shields.io/pypi/pyversions/memora-swarm.svg)](https://pypi.org/project/memora-swarm/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

[Website](https://memora.optitransfer.ch) · [Get a key](https://memora.optitransfer.ch/dashboard) · [Live monitor](https://memora.optitransfer.ch/monitor) · [Docs](docs/) · [Paper](paper/)

**First 25,000 ops free on signup · exact Q16.16 integer math · ARM and x86 resolve to the identical bytes**

</div>

---

## The silent fork

Frameworks run dozens of agents over shared state in a dumb key-value store. AutoGen, CrewAI,
LangGraph — they all point at Redis or Postgres. If one agent is prompt-injected and writes
poisoned JSON or tensors, every other agent reads the poison and the swarm hallucinates. On a
network partition, Redis forks silently and never tells you. And even when everyone agrees, nothing
tells you whether the agreed value has quietly **drifted** away from the truth. There is **no
mathematical guardrail for shared agent state.**

**Memora is that guardrail.**

## Three layers · one full service

Every key gets all three — the whole engine, unlimited agents, **no feature gates**. They compose:
L1 keeps shared state conflict-free, L2 decides whether a resolved value is *believable right now*,
and L3 makes numeric consensus Byzantine-robust. The same math ships to our cloud and on-prem,
unchanged.

| Layer | What it does |
|---|---|
| **L1 · OR-Set CRDT + delta-state** | Conflict-free JSON beliefs. Concurrent writes merge deterministically — the swarm **never forks**, no locks. Author-signed tombstones: only a fact's writer can retract it. |
| **L2 · Epistemic layer** | *Is this value believable now?* Distributional **drift detection**, derived-fact **self-repair** (DCER), **primitive grounding**, and **human-in-the-loop escalation** of anything it can't self-certify. Plus semantic/procedural memory and clean-state checkpoint/resume. **Agreement never promotes to authority — only external re-verification does.** See [`docs/EPISTEMIC.md`](docs/EPISTEMIC.md). |
| **L3 · ACFA Q16.16 multi-Krum + G-Set** | Byzantine-robust tensors; **equivocators are auto-banned** by a self-certifying proof. Up to *f* liars in a group of ≥ 2f+3 cannot move the agreed result. |

Every write is **signed** by a self-certifying node identity and appended to a **replayable**
log — so any state is attributable and auditable after the fact. Runs in **exact Q16.16 integer
arithmetic**, so ARM and x86 agents resolve to byte-identical roots (node ids are u64 — collision
probability ~6.8e-14 across 50k identities in one room).

> You aren't paying for message delivery. You're paying for mathematical certainty that a single
> compromised agent can't fork the swarm — and for a memory that knows when it can't vouch for itself.

---

## Get your swarm live in 60 seconds

**1. Get a free key** — sign up at **[memora.optitransfer.ch/dashboard](https://memora.optitransfer.ch/dashboard)**
(GitHub or email), then click **Issue key**. You get `opti_sk_...`.

**2. Install**

```bash
pip install memora-swarm
```

**3. Connect and use it**

```python
import memora_swarm as memora

db = memora.Blackboard(
    "./swarm.memora",          # local append-only log (state survives restarts)
    node_id="agent_12",        # any label unique to this agent
    api_key="opti_sk_...",     # your key from the dashboard
)
db.connect("research-swarm")   # join a room; every agent in it shares one memory

# L1 — shared key/value, CRDT-merged. get() returns the SET of current values.
db.put("best_hypothesis", "H3")
print(db.get("best_hypothesis"))            # -> ['H3']

# L3 — Byzantine-tolerant numeric aggregation. submit, then resolve the agreed result:
db.submit_tensor("reward_estimate", [0.71, 0.68, 0.73], round=1)
vector, acfa_root, convicted = db.resolve(round=1, f=1)
print(vector, "convicted:", convicted)      # poisoners are evicted, not averaged in

# L2 — the same aggregate, epistemically checked. Adds a drift verdict + HITL escalation:
vector, root, convicted, drift_json, authoritative = db.resolve_checked("reward_estimate", round=1, f=1)
if not authoritative:                       # swarm could not self-certify (drift / primitive / conflict)
    for esc in db.pending_escalations():    # reason + stable id, never the payload
        print("needs grounding:", esc)
    # db.ground_escalation(escalation_id, confirmed=True)   # a human/tool closes it
```

**4. Run more agents** — start the same script on N machines (or N processes) with the **same
`room`** and **different `node_id`s**. They converge on one shared, poison-resistant memory.
**Agents are unlimited** — you're billed by semantic ops, not connections.

**5. Watch it live** — open
**[memora.optitransfer.ch/monitor?key=YOUR_KEY](https://memora.optitransfer.ch/monitor)** to see your
swarm in real time: throughput, agent constellation, **per-room drift status**, the **human-in-the-loop
escalation queue** (one-click *Ground*), and any Byzantine agent getting convicted and evicted.

There is **no server to run**. Your key connects you to the hosted relay, which does the CRDT merge,
trust-weighting, epistemic checks, and Byzantine aggregation for you.

---

## Framework integrations — `pip install` and go

Drop-in, **live-tested** packages for the frameworks you already use. Each one pulls in
`memora-swarm` automatically — one command, everything installed:

| Framework | Install | What you get |
|---|---|---|
| **LangChain** | `pip install memora-langchain` | `MemoraChatMessageHistory` — shared, poison-resistant chat history (drop-in for `RunnableWithMessageHistory`) |
| **CrewAI** | `pip install memora-crewai` | `MemoraCrewMemory.tools()` — `remember_shared` / `recall_shared` + robust `crew_vote` / `crew_consensus` (drift-checked via `resolve_checked`) |
| **Microsoft AutoGen** | `pip install memora-autogen` | `MemoraMemory` — the `autogen_core.memory.Memory` protocol, shared across a team |

PyPI: [memora-langchain](https://pypi.org/project/memora-langchain/) ·
[memora-crewai](https://pypi.org/project/memora-crewai/) ·
[memora-autogen](https://pypi.org/project/memora-autogen/) ·
source and getting-started examples in [`integrations/`](integrations/).

On a custom or unsupported framework? The [`examples/`](examples/) show the raw pattern to adapt.

---

## Pricing

**25,000 semantic ops free** on signup — unlimited agents, the full three-layer engine, no feature gates.

- An **op** is a semantic state transition: a `put()` or a `submit_tensor()`. Keepalive, sync,
  gossip and reads are **never billed**. An idle swarm costs nothing.
- At **85%** of the free allowance you're prompted to add a card so nothing stops mid-run.
- After that: **$0.35 / 1,000 ops** ($0.20 / 1,000 above 2M/month). The **same key** upgrades in
  place — no re-keying, the swarm never stops.

Full breakdown → [docs/PRICING.md](docs/PRICING.md).

---

## Learn more

- **[Architecture](docs/ARCHITECTURE.md)** — how the three layers work, conceptually.
- **[Epistemic layer](docs/EPISTEMIC.md)** — drift channels, HITL escalation, DCER self-repair, memory, resume.
- **[Quickstart](docs/QUICKSTART.md)** — the step-by-step, including scaling to many agents.
- **[Threat model](docs/THREATS.md)** — the attacks Memora is built to survive (OWASP Agentic
  Security, Morris-II self-replicating prompt worms, and more), with sources.
- **[Paper](paper/)** — the ACFA coordinator-free Byzantine aggregation research.
- **[FAQ](docs/FAQ.md)**

---

## License

Apache-2.0 — see [LICENSE](LICENSE). Covers this documentation and the example glue code. The
Memora engine is delivered as a compiled wheel (`pip install memora-swarm`) and a hosted service; the
examples here are yours to use, fork, and adapt freely.

**memora-swarm** — a product of [optitransfer.ch](https://optitransfer.ch).
