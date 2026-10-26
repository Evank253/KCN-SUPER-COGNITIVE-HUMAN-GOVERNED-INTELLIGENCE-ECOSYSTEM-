"""Regression tests for KCN approval and provenance findings.

Added before the implementation fixes. These assert fail-closed behavior rather
than treating a recommendation response as execution authorization.
"""
import pytest

from backend.app.routes.frontier_tools import execute_tool
pytestmark = pytest.mark.asyncio

from integration_layer.data_fabric.provenance_sync import (
    ProvenanceRecord,
    ProvenanceSync,
)


@pytest.mark.parametrize("approval", [False, "false", "0", 0, None, True])
async def test_experiment_gate_rejects_missing_or_false_human_approval(approval):
    response = await execute_tool({
        "name": "experiment_gate",
        "arguments": {
            "sandboxed": True,
            "network_enabled": False,
            "human_subjects": True,
            "approval": approval,
        },
    })
    assert response["result"]["can_run"] is False


async def test_experiment_gate_rejects_non_boolean_approval():
    response = await execute_tool({
        "name": "experiment_gate",
        "arguments": {
            "sandboxed": True,
            "network_enabled": False,
            "human_subjects": True,
            "approval": "true",
        },
    })
    assert response["result"]["can_run"] is False


def test_provenance_verification_detects_record_field_mutation():
    sync = ProvenanceSync()
    record = ProvenanceRecord.create(
        subject_id="artifact-1",
        subject_type="artifact",
        action="created",
        actor_id="operator-1",
        content={"value": "original"},
    )
    sync.record(record)
    record.actor_id = "attacker-controlled-actor"
    chain = sync.build_chain("artifact-1")
    assert chain.verified is False
    assert chain.verification_notes
