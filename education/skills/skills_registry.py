"""
Education System — Skills Registry
Registers capabilities (skills) that agents and humans can acquire / invoke.
Mirrors Global-Intelligence agent_runtime/tool_orchestration/tool_registry.py patterns,
but focuses on governed skills rather than raw tools.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
import time
import uuid


@dataclass
class SkillDefinition:
    skill_id: str
    name: str
    description: str
    category: str  # e.g. reasoning, research, coding, governance, verification
    version: str = "1.0.0"
    required_permissions: List[str] = field(default_factory=list)
    requires_human_approval: bool = True
    tools: List[str] = field(default_factory=list)  # linked tool names
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: float = field(default_factory=time.time)
    status: str = "active"  # active | deprecated | pending_review

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SkillsRegistry:
    """
    Central registry of skills available in the KCN ecosystem.
    Skills are higher-level than tools: a skill may compose multiple tools
    and is always subject to human governance flags.
    """

    def __init__(self):
        self._skills: Dict[str, SkillDefinition] = {}
        self._seed_core_skills()

    def _seed_core_skills(self) -> None:
        core = [
            SkillDefinition(
                skill_id="skill.reasoning.structured",
                name="Structured Reasoning",
                description="Apply logical inference, chain-of-thought, and structured analysis under verification.",
                category="reasoning",
                required_permissions=["intelligence:read"],
                requires_human_approval=False,
                tools=["vector_query_tool"],
                tags=["core", "intelligence"],
            ),
            SkillDefinition(
                skill_id="skill.research.web",
                name="Web Research",
                description="Gather and synthesize information from external sources with evidence tracking.",
                category="research",
                required_permissions=["intelligence:research"],
                requires_human_approval=True,
                tools=["web_search_tool"],
                tags=["core", "research"],
            ),
            SkillDefinition(
                skill_id="skill.governance.approval",
                name="Human Approval Workflow",
                description="Route high-risk actions through human-in-the-loop governance.",
                category="governance",
                required_permissions=["governance:approve"],
                requires_human_approval=True,
                tools=[],
                tags=["core", "governance"],
            ),
            SkillDefinition(
                skill_id="skill.verification.truth",
                name="Truth & Evidence Verification",
                description="Run verification suite (truth, evidence, logic, risk) before knowledge write.",
                category="verification",
                required_permissions=["verification:run"],
                requires_human_approval=False,
                tools=[],
                tags=["core", "verification"],
            ),
            SkillDefinition(
                skill_id="skill.coding.sandbox",
                name="Sandboxed Code Execution",
                description="Execute code in a constrained sandbox for analysis or generation.",
                category="coding",
                required_permissions=["execution:sandbox"],
                requires_human_approval=True,
                tools=["sandbox_code_executor"],
                tags=["core", "execution"],
            ),
            SkillDefinition(
                skill_id="skill.memory.recall",
                name="Federated Memory Recall",
                description="Retrieve verified knowledge from local and federated memory stores.",
                category="memory",
                required_permissions=["knowledge:read"],
                requires_human_approval=False,
                tools=["vector_query_tool"],
                tags=["core", "knowledge"],
            ),
            SkillDefinition(
                skill_id="skill.vibe.jarvis",
                name="Jarvis / Vibe Coaching",
                description="Local coaching and vibe-style developer assistance under human control.",
                category="assistance",
                required_permissions=["vibe:use"],
                requires_human_approval=False,
                tools=[],
                tags=["vibe", "jarvis"],
            ),
        ]
        for s in core:
            self._skills[s.skill_id] = s

    def register(self, skill: SkillDefinition) -> Dict[str, Any]:
        if skill.skill_id in self._skills:
            return {"status": "ALREADY_EXISTS", "skill_id": skill.skill_id}
        self._skills[skill.skill_id] = skill
        return {"status": "REGISTERED", "skill_id": skill.skill_id}

    def register_from_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        skill_id = data.get("skill_id") or f"skill.{uuid.uuid4().hex[:12]}"
        skill = SkillDefinition(
            skill_id=skill_id,
            name=data["name"],
            description=data.get("description", ""),
            category=data.get("category", "general"),
            version=data.get("version", "1.0.0"),
            required_permissions=data.get("required_permissions", []),
            requires_human_approval=data.get("requires_human_approval", True),
            tools=data.get("tools", []),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            status=data.get("status", "pending_review"),
        )
        return self.register(skill)

    def get(self, skill_id: str) -> Optional[Dict[str, Any]]:
        s = self._skills.get(skill_id)
        return s.to_dict() if s else None

    def list(
        self,
        *,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        status: Optional[str] = "active",
        requires_human_approval: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for s in self._skills.values():
            if status and s.status != status:
                continue
            if category and s.category != category:
                continue
            if tag and tag not in s.tags:
                continue
            if requires_human_approval is not None and s.requires_human_approval != requires_human_approval:
                continue
            out.append(s.to_dict())
        return out

    def deprecate(self, skill_id: str) -> bool:
        s = self._skills.get(skill_id)
        if not s:
            return False
        s.status = "deprecated"
        return True

    def manifest(self) -> Dict[str, Any]:
        return {
            "total": len(self._skills),
            "active": sum(1 for s in self._skills.values() if s.status == "active"),
            "categories": sorted({s.category for s in self._skills.values()}),
            "skills": [s.to_dict() for s in self._skills.values()],
        }


# Shared singleton
skills_registry = SkillsRegistry()
