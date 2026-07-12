# memora-autogen

**Poison-resistant, Byzantine-fault-tolerant shared memory for Microsoft AutoGen agent teams.**

`memora-autogen` implements AutoGen's `autogen_core.memory.Memory` protocol on top of
[Memora](https://memora.optitransfer.ch). Give every agent in a team a `MemoraMemory` pointed at the
same `room` and they share **one** memory that a rogue or prompt-injected agent can't silently
corrupt — concurrent writers merge (CRDT, nothing lost), and `update_context` injects the shared
memory into each agent's model context automatically.

```bash
pip install memora-autogen
```

One command — this pulls in the `memora-swarm` engine and `autogen-core`. Free key (25,000 ops) at
**[memora.optitransfer.ch/dashboard](https://memora.optitransfer.ch/dashboard)**.

## Quickstart

```python
from memora_autogen import MemoraMemory
from autogen_core.memory import MemoryContent, MemoryMimeType

mem = MemoraMemory("research-team", api_key="opti_sk_...", node_id="researcher")

await mem.add(MemoryContent(content="prod region is lax", mime_type=MemoryMimeType.TEXT))
print([r.content for r in (await mem.query("region")).results])   # -> ['prod region is lax']
```

## With an AssistantAgent

```python
from autogen_agentchat.agents import AssistantAgent
from memora_autogen import MemoraMemory

shared = MemoraMemory("research-team", api_key="opti_sk_...", node_id="agent-1")
agent = AssistantAgent("researcher", model_client=..., memory=[shared])
```

Every agent constructed with a `MemoraMemory` on the **same room** reads and writes one shared,
poison-resistant memory. `update_context` runs before each model call and prepends the shared memory
as a system message, so the whole team reasons over the same trusted context.

## Why it's safe under a team

- **No lost memories.** Items are stored as uniquely-tagged elements and every replica's view is
  **unioned on read**, so two agents writing at once can't clobber each other.
- **No silent rewrite.** Writes are signed and attributable in the underlying Memora engine; a rogue
  agent's contribution is convicted/evicted rather than trusted.
- **Durable + replayable** via a local append-only log.

## API

Implements the full `autogen_core.memory.Memory` protocol: `add`, `query`, `update_context`,
`clear`, `close` (all async). `query(text)` does a substring filter over the shared items;
`query("")` returns everything.

## Pricing

First **25,000 ops** free (unlimited agents), then metered per semantic op — see
[memora.optitransfer.ch](https://memora.optitransfer.ch). Reads and keepalive are never billed.

## Links

- Engine & docs — https://memora.optitransfer.ch
- Source & other integrations — https://github.com/mgillr/memora-swarm
- Core package — [`memora-swarm`](https://pypi.org/project/memora-swarm/)

Apache-2.0 · a product of [optitransfer.ch](https://optitransfer.ch)
