"""Global event bus for the entire KCN ecosystem."""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid

class Event(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    source: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    headers: Dict[str, str] = Field(default_factory=dict)

EventHandler = Callable[[Event], None]

class GlobalEventBus:
    def __init__(self) -> None:
        self._handlers: Dict[str, List[EventHandler]] = defaultdict(list)
        self._history: List[Event] = []
    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)
    def publish(self, event: Event) -> None:
        self._history.append(event)
        for handler in self._handlers.get(event.event_type, []):
            handler(event)
        for key, handlers in self._handlers.items():
            if key.startswith("prefix:"):
                prefix = key[7:]
                if event.event_type.startswith(prefix):
                    for handler in handlers:
                        handler(event)
    def recent(self, event_type: Optional[str] = None, limit: int = 100) -> List[Event]:
        if event_type is None:
            return self._history[-limit:]
        return [e for e in self._history if e.event_type == event_type][-limit:]
