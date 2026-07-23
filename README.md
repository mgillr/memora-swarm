<div align="center">

# Memora

**Bit-exact Byzantine-fault-tolerant state layer for federated learning and edge/defence swarms.**

Fixed-point Strong Eventual Consistency replaces non-deterministic IEEE-754 aggregation, so
heterogeneous nodes — ARM, x86, GPU — **never silently diverge**, even under partition, jamming,
or adversarial poisoning. One prompt-injected or equivocating node is **mathematically unable to
fork, poison, or move** the agreed state; every write is **signed, attributable, and exactly
replayable**; and the memory itself **knows when it can't vouch for a value** and escalates it to a human.

[![PyPI](https://img.shields.io/pypi/v/memora-swarm.svg)](https://pypi.org/project/memora-swarm/)
[![Python](https://img.shields.io/pypi/pyversions/memora-swarm.svg)](https://pypi.org/project/memora-swarm/)
[![License](https://img.shields.io/badge/SDK-Apache--2.0-blue.svg)](LICENSE)

[Website](https://memora.optitransfer.ch) · [Live monitor](https://memora.optitransfer.ch/monitor) · [Docs](docs/) · [Paper](paper/) · [Validation battery](validation/)

</div>

> **Open glue, closed core.** The consensus engine (`memora-core`) is a **proprietary Rust crate**
> delivered as a pre-compiled wheel (`pip install memora-swarm`) and a hosted relay. **This repository
> is the open client SDK, the framework adapters, the documentation, and a runnable validation battery**
> — everything you need to build against Memora and to verify its guarantees, without the engine source.

---

## The silent fork

Aggregate float tensors across heterogeneous hardware and the result **silently forks**. IEEE-754
reduction order is not deterministic across architectures — the same federated update, Krum
selection, or mean computed on ARM, x86, or different GPUs can land on a different byte sequence or
select a different index. No software patch fixes it; the fix is an **exact-arithmetic boundary**.
And on a network partition a key-value store forks silently and never tells you. There is no
mathematical guardrail for shared distributed state.

Memora is that guardrail.

```python
# federated aggregation in float32 — same updates, different silicon
model = np.mean([n.update for n in nodes])   # ARM root a91f4c…  x86 root 4c02e1…  → silently forked

# Memora — exact Q16.16 integer multi-Krum
db.submit_tensor("model", [n.update for n in nodes])
db.get("model")                              # every node byte-identical (SEC)
```

## Three layers · one full service

Every key gets all three — the whole engine, unlimited nodes, no feature gates.

| Layer | What it does |
| :--- | :--- |
| **L1 · OR-Set CRDT + delta-state** | Conflict-free JSON beliefs. Concurrent writes merge deterministically — the swarm never forks, no locks. Author-signed tombstones. |
| **L2 · Epistemic layer** | *Is this value believable now?* Distributional drift detection, derived-fact self-repair, human-in-the-loop escalation of anything it can't self-certify, memory, and checkpoint/resume. Agreement never promotes to authority — only external re-verification does. |
| **L3 · ACFA Q16.16 multi-Krum + G-Set** | Byzantine-robust tensor aggregation in exact integer arithmetic; an equivocating **key** is convicted by a self-authenticating proof, durable across restarts. Up to *f* liars in a group of ≥ 2*f*+3 cannot move the agreed result. |

Runs in exact Q16.16 integer arithmetic, so ARM and x86 nodes resolve to **byte-identical** roots.

## Quickstart

```bash
pip install memora-swarm          # pre-compiled Rust wheel, zero C-extensions
```
```python
import memora_swarm as memora

db = memora.Blackboard("./swarm.memora", node_id="node_12", api_key="opti_sk_...")
db.connect("research-swarm")                              # join a room; every node shares one memory

db.put("status", "analyzing")                             # L1 — CRDT-merged key/value
db.submit_tensor("model", [0.71, 0.68, 0.73], round=1)    # L3 — Byzantine-robust aggregation (Q16.16)
vector, acfa_root, convicted = db.resolve(round=1, f=1)   # poisoners evicted, not averaged in

# L2 — the same aggregate, epistemically checked (drift verdict + HITL escalation)
vector, root, convicted, drift, authoritative = db.resolve_checked("model", round=1, f=1)
for esc in db.pending_escalations():                      # the HITL queue: reason + stable id
    db.ground_escalation(esc.id, confirmed=True)          # a human/tool closes it
```

Start the same script on N machines with the same room and different `node_id`s — they converge on
one shared, poison-resistant memory. Watch it live at
[`memora.optitransfer.ch/monitor`](https://memora.optitransfer.ch/monitor).

## Validate it yourself

Don't take the claims on faith — run them. The [`validation/`](validation/) battery exercises the
**wheel** (not the engine source) against the reference construction and a live relay:

```bash
python validation/acfa_verify.py     # byte-identity holds; ablations break it; equivocator convicted
```

This mirrors the reproducibility harness described in the [ACFA paper](paper/) — clone it, run the
checks, and watch byte-identity hold while the deliberately-broken ablations diverge.

## Framework integrations — `pip install` and go

Drop-in memory backends for the frameworks you already use (see [`integrations/`](integrations/)):

| Framework | Install | What you get |
| :--- | :--- | :--- |
| **LangChain** | `pip install memora-langchain` | `MemoraChatMessageHistory` — shared, poison-resistant history |
| **CrewAI** | `pip install memora-crewai` | `MemoraCrewMemory.tools()` + drift-checked `crew_consensus` |
| **Microsoft AutoGen** | `pip install memora-autogen` | `MemoraMemory` — the `autogen_core.memory.Memory` protocol, shared across a team |

Memora secures **any stateful payload** — FL model updates, drone telemetry, LLM contexts, or vector embeddings.

## Sandbox & deployment

- **Hosted sandbox** — a free validation quota (50,000 semantic ops on signup; unlimited nodes, the full
  three-layer engine) to test consensus, partition recovery, and Byzantine conviction against the live relay.
  A semantic op is a `put()` or a `submit_tensor()`; keepalive, sync, gossip and reads are never metered.
- **On-prem / air-gapped** — the native `memora-core` engine deploys on your own infrastructure for
  edge, HPC, or sovereignty-constrained environments. **[Contact us](https://optitransfer.ch)** for an
  enterprise licence or a technical briefing.

## Research & IP

- **Papers:** ACFA — coordinator-free Byzantine aggregation ([arXiv:2607.10305](https://arxiv.org/abs/2607.10305)); CRDT-Merge two-layer architecture ([arXiv:2605.19373](https://arxiv.org/abs/2605.19373)). See [`paper/`](paper/).
- **Patents:** the underlying trust and merge constructions are the subject of **UK patent applications
  GB2607132.4 (CRDT-Merge) and GB2608127.3 (E4 trust-as-data); further filings pending.** The ACFA
  construction is described in the public paper and is not itself covered by these applications.

## License

**Apache-2.0** covers this repository — the client SDK, framework adapters, documentation, examples,
and the validation battery. The Memora consensus engine (`memora-core`) is proprietary, delivered as a
compiled wheel (`pip install memora-swarm`) and a hosted service.

`memora-swarm` — a product of [optitransfer.ch](https://optitransfer.ch).
