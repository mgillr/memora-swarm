"""
Use Memora as a shared, poison-resistant store for a CrewAI crew.

Each crew member reads and writes one shared room. Facts merge deterministically (CRDT), numeric
estimates are aggregated with Byzantine tolerance, and an equivocating member is convicted and
evicted from the agreed result.

    pip install memora-swarm
    export MEMORA_KEY=opti_sk_...

Illustrative wrapper on Memora's public API — drop the store into your CrewAI tools/callbacks.
"""

import os
import time
import memora_swarm as memora


class SwarmStore:
    """A tiny shared store your CrewAI agents can call from tools or callbacks."""

    def __init__(self, room: str, node_id: str):
        self.db = memora.Blackboard(
            f"./{node_id}.memora",
            node_id=node_id,
            api_key=os.environ["MEMORA_KEY"],
        )
        self.db.connect(room)
        time.sleep(1)  # let the connection establish

    # --- shared facts (CRDT key/value) ---
    def remember(self, key: str, value: str) -> None:
        self.db.put(key, value)

    def recall(self, key: str) -> list[str]:
        return self.db.get(key)  # the set of values contributed by the crew

    # --- Byzantine-tolerant numeric consensus ---
    def vote(self, name: str, values: list[float], round: int = 1) -> None:
        self.db.submit_tensor(name, values, round=round)

    def consensus(self, round: int = 1, f: int = 1):
        """Returns (aggregate_vector, acfa_root, convicted_node_ids)."""
        return self.db.resolve(round=round, f=f)


if __name__ == "__main__":
    store = SwarmStore(room="crewai-demo", node_id="researcher")
    store.remember("plan", "gather sources, then synthesize")
    store.vote("confidence", [0.82, 0.79, 0.85])
    time.sleep(1)
    vector, _, convicted = store.consensus()
    print("plan:", store.recall("plan"))
    print("consensus:", vector, "| convicted:", convicted)
