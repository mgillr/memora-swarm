"""memora-crewai — poison-resistant shared memory tools for CrewAI crews.

CrewAI agents coordinate through tools. `memora-crewai` gives a crew a set of tools backed by
[Memora](https://memora.optitransfer.ch): agents `remember_shared` / `recall_shared` facts in one
Byzantine-fault-tolerant store, and `crew_vote` / `crew_consensus` on numeric estimates with a
robust aggregate. Concurrent writers merge (CRDT), and a rogue / prompt-injected agent can't
silently corrupt what the crew reads.

    pip install memora-crewai

    from memora_crewai import MemoraCrewMemory
    mem = MemoraCrewMemory("research-crew", api_key="opti_sk_...", node_id="planner")
    # Agent(role="researcher", tools=mem.tools(), ...)
"""
from __future__ import annotations

from typing import Any, List, Optional, Type

from pydantic import BaseModel, Field
from crewai.tools import BaseTool

import memora_swarm as memora

__all__ = [
    "MemoraCrewMemory",
    "MemoraRememberTool",
    "MemoraRecallTool",
    "MemoraVoteTool",
    "MemoraConsensusTool",
]
__version__ = "0.1.0"


# ── tool argument schemas ─────────────────────────────────────────────────────────────────────
class _RememberArgs(BaseModel):
    key: str = Field(description="a short label for the fact, e.g. 'best_hypothesis'")
    value: str = Field(description="the fact or value to share with the whole crew")


class _RecallArgs(BaseModel):
    key: str = Field(description="the label to look up in the crew's shared memory")


class _VoteArgs(BaseModel):
    name: str = Field(description="what is being estimated, e.g. 'confidence'")
    value: float = Field(description="this agent's numeric estimate")


class _ConsensusArgs(BaseModel):
    name: str = Field(description="the estimate to resolve, e.g. 'confidence'")


# ── tools (backed by a shared Memora Blackboard) ──────────────────────────────────────────────
class MemoraRememberTool(BaseTool):
    name: str = "remember_shared"
    description: str = (
        "Store a fact in the crew's shared, Byzantine-fault-tolerant memory (Memora). Every agent "
        "in the crew can recall it; concurrent writes merge and a rogue agent cannot silently "
        "overwrite it."
    )
    args_schema: Type[BaseModel] = _RememberArgs
    db: Any = None

    def _run(self, key: str, value: str) -> str:
        self.db.put(key, value)
        return f"remembered '{key}'"


class MemoraRecallTool(BaseTool):
    name: str = "recall_shared"
    description: str = "Recall a fact from the crew's shared Memora memory by its label."
    args_schema: Type[BaseModel] = _RecallArgs
    db: Any = None

    def _run(self, key: str) -> str:
        values = self.db.get(key)
        return "; ".join(values) if values else f"(nothing stored under '{key}')"


class MemoraVoteTool(BaseTool):
    name: str = "crew_vote"
    description: str = (
        "Submit this agent's numeric estimate to the crew. Estimates are aggregated with a "
        "Byzantine-robust mean, so an outlier or poisoned vote is down-weighted, not averaged in."
    )
    args_schema: Type[BaseModel] = _VoteArgs
    db: Any = None

    def _run(self, name: str, value: float) -> str:
        self.db.submit_tensor(name, [float(value)], round=1)
        return f"voted {value} on '{name}'"


class MemoraConsensusTool(BaseTool):
    name: str = "crew_consensus"
    description: str = "Resolve the crew's Byzantine-robust consensus on a numeric estimate, with any equivocators evicted."
    args_schema: Type[BaseModel] = _ConsensusArgs
    db: Any = None

    def _run(self, name: str) -> str:
        vector, _root, convicted = self.db.resolve(round=1, f=1)
        val = vector[0] if vector else None
        return f"consensus on '{name}' = {val} (evicted node ids: {convicted})"


class MemoraCrewMemory:
    """Shared, poison-resistant memory for a CrewAI crew.

    Create one per crew — every agent that uses `.tools()` on the same `room` shares one memory.
    Get a free key (25,000 ops) at https://memora.optitransfer.ch/dashboard.
    """

    def __init__(
        self,
        room: str,
        *,
        api_key: str = "",
        node_id: str = "crewai",
        path: Optional[str] = None,
        relay_url: Optional[str] = None,
    ) -> None:
        self.room = room
        kwargs = {"node_id": node_id, "api_key": api_key}
        if relay_url:
            kwargs["relay_url"] = relay_url
        self.db = memora.Blackboard(path or f"./{node_id}.memora", **kwargs)
        self.db.connect(room)

    def tools(self) -> List[BaseTool]:
        """The CrewAI tools to hand to your agents (share the same Memora room)."""
        return [
            MemoraRememberTool(db=self.db),
            MemoraRecallTool(db=self.db),
            MemoraVoteTool(db=self.db),
            MemoraConsensusTool(db=self.db),
        ]
