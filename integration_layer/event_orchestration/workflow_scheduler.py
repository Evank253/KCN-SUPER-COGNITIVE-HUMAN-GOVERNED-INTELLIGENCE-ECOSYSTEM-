"""Workflow scheduler – ordered step execution with dependency resolution."""
from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid

class StepStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"

class WorkflowStep(BaseModel):
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    subsystem: str
    depends_on: List[str] = Field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    payload: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

class Workflow(BaseModel):
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mission_id: Optional[str] = None
    name: str
    steps: List[WorkflowStep] = Field(default_factory=list)
    status: str = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WorkflowScheduler:
    def __init__(self) -> None:
        self._workflows: Dict[str, Workflow] = {}
        self._executors: Dict[str, Callable] = {}
    def register_executor(self, subsystem: str, executor: Callable) -> None:
        self._executors[subsystem] = executor
    def submit(self, workflow: Workflow) -> Workflow:
        for step in workflow.steps:
            if not step.depends_on:
                step.status = StepStatus.READY
        self._workflows[workflow.workflow_id] = workflow
        return workflow
    def get(self, workflow_id: str) -> Optional[Workflow]:
        return self._workflows.get(workflow_id)
    def tick(self, workflow_id: str) -> Workflow:
        wf = self._workflows[workflow_id]
        for step in wf.steps:
            if step.status != StepStatus.READY:
                continue
            executor = self._executors.get(step.subsystem)
            step.status = StepStatus.RUNNING
            step.started_at = datetime.now(timezone.utc)
            try:
                step.result = executor(step) if executor else {"warning": f"No executor for {step.subsystem}"}
                step.status = StepStatus.SUCCEEDED
            except Exception as exc:
                step.status = StepStatus.FAILED
                step.result = {"error": str(exc)}
            step.finished_at = datetime.now(timezone.utc)
        succeeded = {s.step_id for s in wf.steps if s.status == StepStatus.SUCCEEDED}
        for step in wf.steps:
            if step.status == StepStatus.PENDING and all(d in succeeded for d in step.depends_on):
                step.status = StepStatus.READY
        if all(s.status in (StepStatus.SUCCEEDED, StepStatus.SKIPPED) for s in wf.steps):
            wf.status = "completed"
        elif any(s.status == StepStatus.FAILED for s in wf.steps):
            wf.status = "failed"
        else:
            wf.status = "running"
        return wf
