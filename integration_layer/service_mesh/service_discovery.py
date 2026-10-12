"""Service discovery built on top of the SubsystemRegistry."""

from __future__ import annotations

from typing import List, Optional
from .subsystem_registry import SubsystemRegistry, SubsystemInfo, SubsystemStatus


class ServiceDiscovery:
    def __init__(self, registry: SubsystemRegistry) -> None:
        self._registry = registry

    def resolve(self, subsystem_id: str) -> Optional[SubsystemInfo]:
        info = self._registry.get(subsystem_id)
        if info is None:
            return None
        if info.status in (SubsystemStatus.HEALTHY, SubsystemStatus.DEGRADED):
            return info
        return None

    def find_by_capability(self, capability: str, *, healthy_only: bool = True) -> List[SubsystemInfo]:
        candidates = self._registry.list_by_capability(capability)
        if healthy_only:
            return [c for c in candidates if c.status in (SubsystemStatus.HEALTHY, SubsystemStatus.DEGRADED)]
        return candidates

    def get_endpoint(self, subsystem_id: str, endpoint_name: str = "default") -> Optional[str]:
        info = self.resolve(subsystem_id)
        if info is None:
            return None
        return info.endpoints.get(endpoint_name)
