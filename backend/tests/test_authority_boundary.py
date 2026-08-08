"""Authority boundary tests — F13 acceptance, F14 watchdog resume."""

from fastapi.testclient import TestClient

from app.main import app
from kcn_core.human_ai import human_ai_governance
from kcn_core.human_ai.watchdog import WatchdogState

client = TestClient(app)


def test_f13_agent_acceptance_403():
    r = client.post(
        "/api/v1/authority/self-mod/acceptance",
        headers={"Authorization": "Bearer agent-token", "X-Actor-Role": "agent"},
        json={
            "action": "acceptance",
            "request_id": "f13-v1-0001",
            "presentation": {"type": ["VerifiablePresentation"], "proof": {"valid": True}},
        },
    )
    assert r.status_code == 403
    assert r.json()["detail"]["reason"] == "not_human_authority"


def test_f14_agent_resume_403():
    human_ai_governance.kill(reason="test")
    assert human_ai_governance.state == WatchdogState.KILLED
    r = client.post(
        "/api/v1/authority/watchdog/resume",
        headers={"Authorization": "Bearer agent-token", "X-Actor-Role": "agent"},
        json={"presentation": {"proof": "valid"}},
    )
    assert r.status_code == 403
    assert human_ai_governance.state == WatchdogState.KILLED
