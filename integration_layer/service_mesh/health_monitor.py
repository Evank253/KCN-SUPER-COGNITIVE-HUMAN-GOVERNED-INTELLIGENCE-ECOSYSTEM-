"""Health monitoring for registered subsystems."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from .subsystem_registry import SubsystemRegistry, SubsystemStatus


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthReport(BaseModel):
    subsystem_id: str
    status: HealthStatus
    last_heartbeat: Optional[datetime] = None
    latency_ms: Optional[float] = None
    details: Dict[str, str] = Field(default_factory=dict)
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HealthMonitor:
    def __init__(self, registry: SubsystemRegistry, heartbeat_timeout: timedelta = timedelta(seconds=30)) -> None:
        self._registry = registry
        self._timeout = heartbeat_timeout
        self._reports: Dict[str, HealthReport] = {}

    def report(self, report: HealthReport) -> None:
        self._reports[report.subsystem_id] = report
        mapping = {
            HealthStatus.HEALTHY: SubsystemStatus.HEALTHY,
            HealthStatus.DEGRADED: SubsystemStatus.DEGRADED,
            HealthStatus.UNHEALTHY: SubsystemStatus.UNHEALTHY,
            HealthStatus.UNKNOWN: SubsystemStatus.REGISTERED,
        }
        try:
            self._registry.update_status(report.subsystem_id, mapping[report.status])
        except KeyError:
            pass

    def check(self, subsystem_id: str) -> HealthReport:
        info = self._registry.get(subsystem_id)
        if info is None:
            return HealthReport(subsystem_id=subsystem_id, status=HealthStatus.UNKNOWN)
        now = datetime.now(timezone.utc)
        if info.last_heartbeat is None:
            status = HealthStatus.UNKNOWN
        elif now - info.last_heartbeat > self._timeout:
            status = HealthStatus.UNHEALTHY
        else:
            explicit = self._reports.get(subsystem_id)
            if explicit and (now - explicit.checked_at) < self._timeout:
                status = explicit.status
            else:
                status = HealthStatus.HEALTHY
        return HealthReport(subsystem_id=subsystem_id, status=status, last_heartbeat=info.last_heartbeat)

    def check_all(self) -> List[HealthReport]:
        return [self.check(s.subsystem_id) for s in self._registry.list_all()]
