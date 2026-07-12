# memora-crewai

**Poison-resistant, Byzantine-fault-tolerant shared memory + robust voting for CrewAI crews.**

CrewAI agents coordinate through tools. `memora-crewai` hands your crew a set of tools backed by
[Memora](https://memora.optitransfer.ch): agents `remember_shared` / `recall_shared` facts in **one**
Byzantine-tolerant store, and `crew_vote` / `crew_consensus` on numeric estimates with a robust
aggregate. Concurrent writers merge (CRDT, nothing lost), and a rogue or prompt-injected agent can't
silently corrupt what the crew reads — or skew the vote.

```bash
pip install memora-crewai
```

One command — pulls in the `memora-swarm` engine and `crewai`. Free key (25,000 ops) at
**[memora.optitransfer.ch/dashboard](https://memora.optitransfer.ch/dashboard)**.

## Quickstart

```python
from crewai import Agent
from memora_crewai import MemoraCrewMemory

mem = MemoraCrewMemory("research-crew", api_key="opti_sk_...", node_id="planner")

researcher = Agent(
    role="Researcher",
    goal="Find and share verified facts with the crew",
    tools=mem.tools(),        # remember_shared, recall_shared, crew_vote, crew_consensus
    # ...
)
```

Every agent built with `mem.tools()` on the **same room** shares one poison-resistant memory.

## The tools

| Tool | What it does |
|---|---|
| `remember_shared(key, value)` | Store a fact in the crew's shared, Byzantine-safe memory |
| `recall_shared(key)` | Recall a fact every agent can see |
| `crew_vote(name, value)` | Submit a numeric estimate — outliers/poisoned votes are down-weighted |
| `crew_consensus(name)` | Resolve the Byzantine-robust consensus; equivocators are evicted |

## Why it's safe under a crew

- **No lost facts.** Writes merge deterministically (CRDT) — concurrent agents can't clobber each other.
- **No silent rewrite / no skewed vote.** Every contribution is signed and attributable in the Memora
  engine; a rogue agent's write or an outlier vote is convicted/down-weighted, not trusted on faith.
- **Durable + replayable** via a local append-only log.

## Pricing

First **25,000 ops** free (unlimited agents), then metered per semantic op — see
[memora.optitransfer.ch](https://memora.optitransfer.ch). Reads and keepalive are never billed.

## Links

- Engine & docs — https://memora.optitransfer.ch
- Source & other integrations — https://github.com/mgillr/memora-swarm
- Core package — [`memora-swarm`](https://pypi.org/project/memora-swarm/)

Apache-2.0 · a product of [optitransfer.ch](https://optitransfer.ch)
