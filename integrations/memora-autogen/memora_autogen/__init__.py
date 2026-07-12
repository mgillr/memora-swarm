"""memora-autogen — poison-resistant shared memory for Microsoft AutoGen agent teams.

Implements AutoGen's ``autogen_core.memory.Memory`` protocol on top of
[Memora](https://memora.optitransfer.ch). Give every agent in a team a ``MemoraMemory`` pointed at
the same `room` and they share one Byzantine-fault-tolerant memory: concurrent writers merge
(CRDT — nothing lost), and a rogue / prompt-injected agent cannot silently rewrite what the team
recalls. ``update_context`` injects the shared memory into each agent's model context automatically.

    pip install memora-autogen

    from memora_autogen import MemoraMemory
    mem = MemoraMemory("research-team", api_key="opti_sk_...", node_id="researcher")
    # AssistantAgent(..., memory=[mem])
"""
from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

from autogen_core import CancellationToken
from autogen_core.memory import (
    Memory,
    MemoryContent,
    MemoryMimeType,
    MemoryQueryResult,
    UpdateContextResult,
)
from autogen_core.model_context import ChatCompletionContext
from autogen_core.models import SystemMessage

import memora_swarm as memora

__all__ = ["MemoraMemory"]
__version__ = "0.1.0"


class MemoraMemory(Memory):
    """AutoGen Memory shared across an agent team, backed by Memora.

    Get a free key (25,000 ops free) at https://memora.optitransfer.ch/dashboard.
    """

    def __init__(
        self,
        room: str,
        *,
        api_key: str = "",
        node_id: str = "autogen",
        key: str = "memory",
        path: Optional[str] = None,
        relay_url: Optional[str] = None,
    ) -> None:
        self.room = room
        self._key = key
        self._seq = 0
        kwargs = {"node_id": node_id, "api_key": api_key}
        if relay_url:
            kwargs["relay_url"] = relay_url
        self._db = memora.Blackboard(path or f"./{node_id}.memora", **kwargs)
        self._db.connect(room)

    # Memora's shared value is a CRDT register that may hold >1 concurrent version — UNION every
    # version's tagged elements so no team member's memories are lost under concurrent writes.
    def _elements(self) -> Dict[str, dict]:
        merged: Dict[str, dict] = {}
        for raw in self._db.get(self._key):
            try:
                lst = json.loads(raw)
            except Exception:
                continue
            if isinstance(lst, list):
                for e in lst:
                    if isinstance(e, dict) and "id" in e and "c" in e:
                        merged[e["id"]] = e
        return merged

    def _sorted(self) -> List[dict]:
        return sorted(self._elements().values(), key=lambda e: (e.get("t", 0.0), e.get("id", "")))

    async def add(self, content: MemoryContent, cancellation_token: Optional[CancellationToken] = None) -> None:
        merged = self._elements()
        eid = f"{self._db.node_num}:{self._seq}"
        self._seq += 1
        merged[eid] = {"id": eid, "t": time.time(), "c": str(content.content)}
        ordered = sorted(merged.values(), key=lambda e: (e.get("t", 0.0), e.get("id", "")))
        self._db.put(self._key, json.dumps(ordered))

    async def query(
        self,
        query: str | MemoryContent,
        cancellation_token: Optional[CancellationToken] = None,
        **kwargs: Any,
    ) -> MemoryQueryResult:
        q = str(query.content if isinstance(query, MemoryContent) else query).lower()
        results = [
            MemoryContent(content=e["c"], mime_type=MemoryMimeType.TEXT)
            for e in self._sorted()
            if not q or q in e["c"].lower()
        ]
        return MemoryQueryResult(results=results)

    async def update_context(self, model_context: ChatCompletionContext) -> UpdateContextResult:
        items = [e["c"] for e in self._sorted()]
        if items:
            memo = "\n".join(f"- {c}" for c in items)
            await model_context.add_message(SystemMessage(content=f"Shared swarm memory (Memora):\n{memo}"))
        results = [MemoryContent(content=c, mime_type=MemoryMimeType.TEXT) for c in items]
        return UpdateContextResult(memories=MemoryQueryResult(results=results))

    async def clear(self) -> None:
        self._db.put(self._key, "[]")

    async def close(self) -> None:
        return None
