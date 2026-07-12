# memora-langchain

**Poison-resistant, Byzantine-fault-tolerant shared chat memory for LangChain agent swarms.**

When several LangChain agents share one conversation memory, that memory is the weakest link — one
prompt-injected or malfunctioning agent can overwrite what every other agent then reads. `memora-langchain`
backs LangChain's message history with [Memora](https://memora.optitransfer.ch), a CRDT + Byzantine-
tolerant shared store: **concurrent writers merge without losing turns, and no single agent can silently
rewrite the shared history.**

```bash
pip install memora-langchain
```

That's it — this pulls in the `memora-swarm` engine and `langchain-core` for you. Get a free API key
(25,000 ops free) at **[memora.optitransfer.ch/dashboard](https://memora.optitransfer.ch/dashboard)**.

## Quickstart

```python
from memora_langchain import MemoraChatMessageHistory

history = MemoraChatMessageHistory(
    "support-crew",              # room: every agent using this room shares one history
    api_key="opti_sk_...",
    node_id="triage-agent",      # unique per agent
)

history.add_user_message("customer can't log in")
history.add_ai_message("checking their account status…")

for m in history.messages:       # merged view across the whole swarm
    print(type(m).__name__, m.content)
```

## Use it with `RunnableWithMessageHistory`

```python
from langchain_core.runnables.history import RunnableWithMessageHistory

chain_with_memory = RunnableWithMessageHistory(
    your_chain,
    lambda session_id: MemoraChatMessageHistory(session_id, api_key="opti_sk_...", node_id="agent"),
    input_messages_key="input",
    history_messages_key="history",
)
```

`MemoraChatMessageHistory` is a standard `langchain_core.chat_history.BaseChatMessageHistory`, so it works
anywhere LangChain accepts a chat history — including as the shared store behind a LangGraph node.

## Why it's safe under a swarm

- **No lost turns.** The history is stored as uniquely-tagged message elements and every replica's view is
  **unioned on read**, so two agents writing at once can't clobber each other — both sets of turns survive.
- **No silent rewrite.** Every write is signed and attributable to a node in the underlying Memora engine;
  a rogue agent's contribution is convicted/evicted rather than trusted on faith.
- **Durable + replayable.** State survives restarts via a local append-only log.

## Pricing

The first **25,000 ops** are free (unlimited agents). After that it's metered per semantic op — see
[memora.optitransfer.ch](https://memora.optitransfer.ch). Reads and keepalive are never billed.

## Links

- Engine & docs — https://memora.optitransfer.ch
- Source & other integrations — https://github.com/mgillr/memora-swarm
- Core package — [`memora-swarm`](https://pypi.org/project/memora-swarm/)

Apache-2.0 · a product of [optitransfer.ch](https://optitransfer.ch)
