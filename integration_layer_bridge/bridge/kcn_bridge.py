"""
KCNBridge – single entry point that wires the Integration Layer into the
Super Cognitive Human-Governed Intelligence Ecosystem.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
if str(_ROOT / "integration_layer") not in sys.path:
    sys.path.insert(0, str(_ROOT / "integration_layer"))

from service_mesh import (
    SubsystemRegistry, SubsystemInfo, SubsystemStatus,
    ServiceDiscovery, HealthMonitor, MessageRouter,
)
from identity_federation import (
    UnifiedIdentity, IdentityRecord, IdentityType,
    CredentialExchange, PermissionBridge, AccessDecision,
)
from event_orchestration import (
    GlobalEventBus, Event, MissionPipeline, Mission, MissionStatus,
)
from data_fabric import (
    ArtifactSync, KnowledgeSync, ProvenanceSync, ProvenanceRecord,
)
from ai_control_plane import (
    AgentRegistry, AgentRecord, ModelRouter, MemoryCoordinator,
    SwarmManager, Swarm, SwarmMember,
)

SUPER_COGNITIVE_CORES = [
    {"subsystem_id": "sc-intelligence-core", "name": "Intelligence Core", "phase": "SC-INTEL", "capabilities": ["reasoning", "research", "analysis"]},
    {"subsystem_id": "sc-verification-core", "name": "Verification Core", "phase": "SC-VERIFY", "capabilities": ["validation", "evidence", "scoring"]},
    {"subsystem_id": "sc-knowledge-core", "name": "Knowledge Core", "phase": "SC-KNOW", "capabilities": ["storage", "retrieval", "graph"]},
    {"subsystem_id": "sc-security-core", "name": "Security Core", "phase": "SC-SEC", "capabilities": ["protection", "audit", "isolation"]},
    {"subsystem_id": "sc-governance", "name": "Human Governance", "phase": "SC-GOV", "capabilities": ["approval", "policy", "authority"]},
    {"subsystem_id": "sc-execution-engine", "name": "Execution Engine", "phase": "SC-EXEC", "capabilities": ["build", "deploy", "runtime"]},
    {"subsystem_id": "sc-education", "name": "Education System", "phase": "SC-EDU", "capabilities": ["learning", "curriculum", "assessment"]},
    {"subsystem_id": "sc-innovation", "name": "Innovation System", "phase": "SC-INNO", "capabilities": ["ideation", "prototyping", "opportunity"]},
]


class KCNBridge:
    """Owns the Integration Layer and exposes a Super-Cognitive-friendly API."""

    def __init__(self) -> None:
        self.registry = SubsystemRegistry()
        self.discovery = ServiceDiscovery(self.registry)
        self.health = HealthMonitor(self.registry)
        self.router = MessageRouter()
        self.identity = UnifiedIdentity()
        self.credentials = CredentialExchange()
        self.permissions = PermissionBridge()
        self.events = GlobalEventBus()
        self.missions = MissionPipeline()
        self.artifacts = ArtifactSync()
        self.knowledge = KnowledgeSync()
        self.provenance = ProvenanceSync()
        self.agents = AgentRegistry()
        self.models = ModelRouter()
        self.memory = MemoryCoordinator()
        self.swarms = SwarmManager()
        self._bootstrapped = False

    def bootstrap(self) -> None:
        if self._bootstrapped:
            return
        for core in SUPER_COGNITIVE_CORES:
            self.registry.register(SubsystemInfo(
                subsystem_id=core["subsystem_id"],
                name=core["name"],
                phase=core["phase"],
                version="0.1.0",
                endpoints={"default": f"internal://{core['subsystem_id']}"},
                capabilities=core["capabilities"],
                status=SubsystemStatus.HEALTHY,
            ))
        self.permissions.mark_human_gated("mission", "create")
        self.permissions.mark_human_gated("agent", "deploy")
        self.permissions.mark_human_gated("model", "promote")
        self.permissions.mark_human_gated("knowledge", "publish")
        self._bootstrapped = True
        self.events.publish(Event(
            event_type="bridge.bootstrapped",
            source="kcn_bridge",
            payload={"cores": len(SUPER_COGNITIVE_CORES)},
        ))

    def register_human(self, display_name: str, email: str) -> IdentityRecord:
        return self.identity.register(IdentityRecord(
            identity_type=IdentityType.HUMAN,
            display_name=display_name,
            external_ids={"email": email},
        ))

    def register_agent_identity(self, display_name: str, agent_key: str) -> IdentityRecord:
        return self.identity.register(IdentityRecord(
            identity_type=IdentityType.AGENT,
            display_name=display_name,
            external_ids={"agent_key": agent_key},
        ))

    def record_action(
        self, *,
        subject_id: str,
        subject_type: str,
        action: str,
        actor_id: str,
        content: Any,
        parent_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ProvenanceRecord:
        rec = ProvenanceRecord.create(
            subject_id=subject_id,
            subject_type=subject_type,
            action=action,
            actor_id=actor_id,
            content=content,
            parent_ids=parent_ids,
            metadata=metadata or {},
        )
        self.provenance.record(rec)
        self.events.publish(Event(
            event_type=f"provenance.{action}",
            source="kcn_bridge",
            payload={"record_id": rec.record_id, "subject_id": subject_id, "actor_id": actor_id},
        ))
        return rec

    def export_evidence(self, subject_id: str) -> Dict[str, Any]:
        return self.provenance.export_evidence_package(subject_id)

    def get_chain(self, subject_id: str):
        return self.provenance.build_chain(subject_id)

    def create_mission(
        self,
        title: str,
        owner_id: str,
        objectives: List[str],
        assigned_cores: Optional[List[str]] = None,
    ) -> Mission:
        mission = Mission(
            title=title,
            owner_id=owner_id,
            objectives=objectives,
            assigned_subsystems=assigned_cores or ["sc-intelligence-core"],
            status=MissionStatus.DRAFT,
        )
        self.missions.create(mission)
        self.events.publish(Event(
            event_type="mission.created",
            source="kcn_bridge",
            payload={"mission_id": mission.mission_id, "title": title},
        ))
        return mission

    def status(self) -> Dict[str, Any]:
        return {
            "bootstrapped": self._bootstrapped,
            "subsystems": len(self.registry.list_all()),
            "identities": len(self.identity._identities),
            "provenance_records": len(self.provenance._records),
            "agents": len(self.agents._agents),
            "swarms": len(self.swarms._swarms),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
