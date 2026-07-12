"""
Memora quickstart — a poison-resistant shared memory in ~25 lines.

    pip install memora-swarm

Get a free key at https://memora.optitransfer.ch/dashboard, then:

    export MEMORA_KEY=opti_sk_...
    python quickstart.py
"""

import os
import time
import memora_swarm as memora

db = memora.Blackboard(
    "./swarm.memora",                 # path to a local append-only log (survives restarts)
    node_id="agent_1",                # unique label for this agent
    api_key=os.environ["MEMORA_KEY"],
)
db.connect("quickstart")             # join a room; every agent in it shares one memory
time.sleep(1)                         # give the connection a moment to establish

# 1) Shared key/value state — CRDT-merged across the swarm, never forks.
#    get() returns the SET of current values (an OR-Set can hold concurrent writes).
db.put("best_hypothesis", "H3")
print("state:", db.get("best_hypothesis"))          # -> ['H3']

# 2) Byzantine-tolerant numeric aggregation.
#    submit your estimate, then resolve() returns (aggregate_vector, acfa_root, convicted_ids).
db.submit_tensor("reward_estimate", [0.71, 0.68, 0.73], round=1)
time.sleep(1)
vector, acfa_root, convicted = db.resolve(round=1, f=1)
print("swarm aggregate:", vector)
print("convicted (evicted) node ids:", convicted)   # empty with only honest agents

# 3) Stay ahead of the free allowance so ops never stop mid-run.
used, limit = db.usage
print(f"usage: {used}/{limit} free ops")
if db.usage_warning:
    print("Near the free limit — add a card: https://memora.optitransfer.ch/dashboard")
