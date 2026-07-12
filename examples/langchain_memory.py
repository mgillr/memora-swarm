"""
Use Memora as a shared, Byzantine-safe scratchpad memory for a LangChain crew.

Every agent writes facts into one room; because the store is a CRDT, concurrent writers merge
without forking, and a poisoned/malfunctioning agent can't corrupt what the others read.

    pip install memora-swarm langchain-core
    export MEMORA_KEY=opti_sk_...

This is an illustrative adapter built entirely on Memora's public API (connect / put / get).
Adapt it to whatever LangChain memory contract your version expects.
"""

import os
from typing import Any, Dict, List

import memora_swarm as memora
from langchain_core.memory import BaseMemory

_SCRATCHPAD = "scratchpad"


class MemoraSwarmMemory(BaseMemory):
    """Shared scratchpad memory backed by a Memora room.

    load_memory_variables -> the merged set of facts every agent has contributed.
    save_context          -> appends this agent's output as a fact into the shared room.
    """

    room: str
    node_id: str = "langchain"
    api_key: str = ""
    memory_key: str = "swarm_facts"

    _db: Any = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._db = memora.Blackboard(
            f"./{self.node_id}.memora",
            node_id=self.node_id,
            api_key=self.api_key or os.environ.get("MEMORA_KEY", ""),
        )
        self._db.connect(self.room)

    @property
    def memory_variables(self) -> List[str]:
        return [self.memory_key]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # get() returns the SET of current values contributed by the whole swarm
        facts = self._db.get(_SCRATCHPAD)
        return {self.memory_key: "\n".join(facts)}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        fact = str(next(iter(outputs.values()), "")).strip()
        if fact:
            self._db.put(_SCRATCHPAD, f"[{self.node_id}] {fact}")

    def clear(self) -> None:
        self._db.put(_SCRATCHPAD, "")


if __name__ == "__main__":
    mem = MemoraSwarmMemory(room="langchain-demo", node_id="planner")
    mem.save_context({"task": "research"}, {"output": "candidate H3 looks strongest"})
    print(mem.load_memory_variables({}))
