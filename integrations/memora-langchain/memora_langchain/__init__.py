"""memora-langchain — poison-resistant shared chat memory for LangChain agent swarms.

Every agent that opens the same Memora `room` shares one Byzantine-fault-tolerant message history.
Memora's shared value is a CRDT register, so we store the history as a list of uniquely-tagged
message elements and UNION every replica's view on read: concurrent writers merge without losing
turns, and a rogue / prompt-injected agent cannot silently rewrite what the others read. Drop-in
for LangChain's RunnableWithMessageHistory.

    pip install memora-langchain

    from memora_langchain import MemoraChatMessageHistory
    hist = MemoraChatMessageHistory("crew-42", api_key="opti_sk_...", node_id="planner")
"""
from __future__ import annotations

import json
import time
from typing import Dict, List, Optional, Sequence

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, messages_from_dict, messages_to_dict

import memora_swarm as memora

__all__ = ["MemoraChatMessageHistory"]
__version__ = "0.1.0"


class MemoraChatMessageHistory(BaseChatMessageHistory):
    """LangChain chat history shared across an agent swarm, backed by Memora.

    Get a free key at https://memora.optitransfer.ch/dashboard. Use with
    ``RunnableWithMessageHistory`` by passing a factory that returns one of these per session/room.
    """

    def __init__(
        self,
        room: str,
        *,
        api_key: str = "",
        node_id: str = "langchain",
        key: str = "chat",
        path: Optional[str] = None,
        relay_url: Optional[str] = None,
    ) -> None:
        self.room = room
        self._key = key
        self._seq = 0
        kwargs = {"node_id": node_id, "api_key": api_key}
        if relay_url:
            kwargs["relay_url"] = relay_url
        # first positional arg is the local append-only log path (state survives restarts)
        self._db = memora.Blackboard(path or f"./{node_id}.memora", **kwargs)
        self._db.connect(room)

    def _elements(self) -> Dict[str, dict]:
        # Memora's value is a CRDT register that can hold >1 concurrent version — UNION every
        # version's tagged elements (keyed by a unique id) so no writer's messages are lost.
        merged: Dict[str, dict] = {}
        for raw in self._db.get(self._key):
            try:
                lst = json.loads(raw)
            except Exception:
                continue
            if isinstance(lst, list):
                for e in lst:
                    if isinstance(e, dict) and "id" in e and "m" in e:
                        merged[e["id"]] = e
        return merged

    @property
    def messages(self) -> List[BaseMessage]:
        elements = sorted(self._elements().values(), key=lambda e: (e.get("t", 0.0), e.get("id", "")))
        return messages_from_dict([e["m"] for e in elements])

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        merged = self._elements()  # read-merge current view (self-heals concurrent writes)
        node = self._db.node_num
        for m in messages:
            eid = f"{node}:{self._seq}"
            self._seq += 1
            merged[eid] = {"id": eid, "t": time.time(), "m": messages_to_dict([m])[0]}
        ordered = sorted(merged.values(), key=lambda e: (e.get("t", 0.0), e.get("id", "")))
        self._db.put(self._key, json.dumps(ordered))

    def add_message(self, message: BaseMessage) -> None:
        self.add_messages([message])

    def clear(self) -> None:
        # LWW register: writing an empty list resets the shared history.
        self._db.put(self._key, "[]")
