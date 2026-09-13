"""KCN Security Fabric v1 foundation."""

from app.security_fabric.adapters import ADAPTERS, Adapter, AdapterError, AdapterResult
from app.security_fabric.cases import SecurityCase
from app.security_fabric.correlation import CorrelationEngine
from app.security_fabric.evidence import EvidenceRecord, build_evidence
from app.security_fabric.models import SecurityEvent
from app.security_fabric.normalize import Normalizer

__all__ = [
    "ADAPTERS",
    "Adapter",
    "AdapterError",
    "AdapterResult",
    "CorrelationEngine",
    "EvidenceRecord",
    "Normalizer",
    "SecurityCase",
    "SecurityEvent",
    "build_evidence",
]
