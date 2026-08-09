"""
Skills API routes — Skills Registry exposure.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

_repo_root = Path(__file__).resolve().parents[3]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from education.skills.skills_registry import skills_registry

router = APIRouter(prefix="/skills", tags=["Skills"])


class RegisterSkillRequest(BaseModel):
    name: str
    description: str = ""
    category: str = "general"
    version: str = "1.0.0"
    required_permissions: list[str] = Field(default_factory=list)
    requires_human_approval: bool = True
    tools: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    skill_id: str | None = None
    status: str = "pending_review"


@router.get("/")
def list_skills(
    category: str | None = Query(None),
    tag: str | None = Query(None),
    status: str | None = Query("active"),
    requires_human_approval: bool | None = Query(None),
):
    return {
        "skills": skills_registry.list(
            category=category,
            tag=tag,
            status=status,
            requires_human_approval=requires_human_approval,
        )
    }


@router.get("/manifest")
def manifest():
    return skills_registry.manifest()


@router.get("/{skill_id}")
def get_skill(skill_id: str):
    skill = skills_registry.get(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.post("/")
def register_skill(body: RegisterSkillRequest):
    data = body.model_dump()
    result = skills_registry.register_from_dict(data)
    if result.get("status") == "ALREADY_EXISTS":
        raise HTTPException(status_code=409, detail=result)
    return result


@router.post("/{skill_id}/deprecate")
def deprecate_skill(skill_id: str):
    ok = skills_registry.deprecate(skill_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Skill not found")
    return {"status": "deprecated", "skill_id": skill_id}
