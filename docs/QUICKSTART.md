# Quickstart

Get a poison-resistant shared memory running across many agents. ~5 minutes.

## 1. Get a key

1. Go to **[memora.optitransfer.ch/dashboard](https://memora.optitransfer.ch/dashboard)**.
2. Sign in with **GitHub** or **email** (magic link).
3. Click **Issue key**. Copy the `opti_sk_...` value — it's shown once.

The first **25,000 ops** are free, unlimited agents. No card needed to start.

## 2. Install

```bash
pip install memora-swarm
```

Requires Python 3.9+. The wheel is a native (Rust) engine with a zero-dependency Python API.

## 3. One agent

```python
import memora_swarm as memora

db = memora.Blackboard(
    "./swarm.memora",
    node_id="agent_1",
    api_key="opti_sk_...",
)
db.connect("my-first-swarm")   # join the room

db.put("status", "ready")
print(db.get("status"))        # -> ['ready']   (get returns the set of current values)
```

## 4. Many agents (the point)

Run the **same room** from several processes/machines with **different `node_id`s**. They share
one converged memory.

```python
# worker.py — launch this N times with a unique node id each:
#   NODE=agent_$RANDOM python worker.py
import os, time, memora_swarm as memora

db = memora.Blackboard(
    f"./{os.environ['NODE']}.memora",
    node_id=os.environ["NODE"],
    api_key=os.environ["MEMORA_KEY"],
)
db.connect("my-first-swarm")
time.sleep(1)

# every worker contributes an estimate; resolve() returns the Byzantine-agreed result:
#   (aggregate_vector, acfa_root, convicted_node_ids)
db.submit_tensor("reward", [0.70, 0.71, 0.69], round=1)
time.sleep(1)
vector, _, convicted = db.resolve(round=1, f=1)
print("swarm aggregate:", vector, "| convicted:", convicted)
```

```bash
export MEMORA_KEY=opti_sk_...
for i in $(seq 1 50); do NODE=agent_$i python worker.py & done
```

Fifty agents, one shared memory, no server, no locks. A worker that submits garbage is
**down-weighted**; one that equivocates is **convicted and evicted**.

## 5. Watch it live

Open your monitor (paste your key):

```
https://memora.optitransfer.ch/monitor?key=opti_sk_...
```

You'll see throughput, the agent constellation, and any Byzantine agent flashing red as it's
evicted — plus your live billing position against the free allowance.

## 6. Handle the free-tier signal (optional but recommended)

The client surfaces when you're near the free limit so ops never stop unexpectedly:

```python
if db.usage_warning:      # True at 85% of the free allowance
    print("Add a card to keep the swarm running:",
          "https://memora.optitransfer.ch/dashboard")

if db.throttled:          # True once free ops are exhausted and no card is on file
    print("Throttled — add a card; state is preserved and resumes instantly.")
```

Adding a card upgrades the **same key** in place — nothing re-keys, the swarm continues.

## Next

- [Architecture](ARCHITECTURE.md) — what's happening under the hood.
- [Framework adapters](../examples/) — LangChain, CrewAI.
- [Threat model](THREATS.md) — what you're protected against.
