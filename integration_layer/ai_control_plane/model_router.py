"""Model routing – selects which model endpoint should handle a request."""
from __future__ import annotations
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import uuid

class ModelEndpoint(BaseModel):
    endpoint_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    provider: str
    model_id: str
    capabilities: List[str] = Field(default_factory=list)
    max_tokens: int = 8192
    cost_per_1k_tokens: float = 0.0
    latency_ms_p50: float = 0.0
    available: bool = True
    metadata: Dict[str, str] = Field(default_factory=dict)

class ModelRouter:
    def __init__(self) -> None:
        self._endpoints: Dict[str, ModelEndpoint] = {}
    def register(self, endpoint: ModelEndpoint) -> ModelEndpoint:
        self._endpoints[endpoint.endpoint_id] = endpoint
        return endpoint
    def route(self, required_capabilities: List[str], *, prefer_low_cost: bool = True) -> Optional[ModelEndpoint]:
        candidates = [e for e in self._endpoints.values()
                      if e.available and all(c in e.capabilities for c in required_capabilities)]
        if not candidates:
            return None
        if prefer_low_cost:
            candidates.sort(key=lambda e: e.cost_per_1k_tokens)
        return candidates[0]
    def list_available(self) -> List[ModelEndpoint]:
        return [e for e in self._endpoints.values() if e.available]
