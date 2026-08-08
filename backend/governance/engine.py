from datetime import datetime


# Actions that change the system itself — never autonomous
SELF_MODIFICATION_ACTIONS = frozenset({
    "self_modification",
    "system_self_change",
    "modify_governance",
    "modify_judgment",
    "modify_watchdog",
    "modify_killswitch",
    "modify_security_controls",
    "modify_audit_rules",
    "disable_safety",
    "remove_safety",
    "change_root_policy",
    "rewrite_charter",
    "agent_self_upgrade",
    "twin_self_upgrade",
    "core_code_change",
    "permission_escalation",
    "disable_logging",
    "disable_monitoring",
})


class GovernanceEngine:
    def __init__(self):
        self.rules = {
            "critical_change": "HUMAN_APPROVAL_REQUIRED",
            "security_change": "HUMAN_APPROVAL_REQUIRED",
            "agent_permission_change": "HUMAN_APPROVAL_REQUIRED",
            "deploy_production": "HUMAN_APPROVAL_REQUIRED",
            "remove_safety": "BLOCKED",
            "disable_safety": "BLOCKED",
            "self_modification": "HUMAN_ACCEPTANCE_REQUIRED",
            "system_self_change": "HUMAN_ACCEPTANCE_REQUIRED",
            "modify_governance": "HUMAN_ACCEPTANCE_REQUIRED",
            "modify_judgment": "HUMAN_ACCEPTANCE_REQUIRED",
            "modify_watchdog": "HUMAN_ACCEPTANCE_REQUIRED",
            "modify_killswitch": "HUMAN_ACCEPTANCE_REQUIRED",
            "modify_security_controls": "HUMAN_ACCEPTANCE_REQUIRED",
            "core_code_change": "HUMAN_ACCEPTANCE_REQUIRED",
            "permission_escalation": "HUMAN_ACCEPTANCE_REQUIRED",
            "disable_logging": "BLOCKED",
            "disable_monitoring": "BLOCKED",
            "normal_operation": "ALLOW",
        }
        self.principle = (
            "The system must not make any changes to itself without actual human acceptance."
        )

    def is_self_modification(self, action: str, intent: str = "") -> bool:
        key = (action or "").strip().lower().replace(" ", "_").replace("-", "_")
        if key in SELF_MODIFICATION_ACTIONS or key in self.rules and self.rules.get(key) in (
            "HUMAN_ACCEPTANCE_REQUIRED",
            "BLOCKED",
        ):
            return key in SELF_MODIFICATION_ACTIONS or "HUMAN_ACCEPTANCE" in str(self.rules.get(key, ""))
        blob = f"{action} {intent}".lower()
        markers = (
            "self mod", "modify itself", "change its own", "rewrite governance",
            "disable watchdog", "disable killswitch", "upgrade core", "patch system",
            "modify judgment", "change charter", "escalate permission",
        )
        return any(m in blob for m in markers)

    def evaluate(self, action: str, intent: str = "") -> dict:
        key = (action or "").strip().lower().replace(" ", "_").replace("-", "_")
        if self.is_self_modification(action, intent):
            decision = self.rules.get(key, "HUMAN_ACCEPTANCE_REQUIRED")
            if decision == "ALLOW":
                decision = "HUMAN_ACCEPTANCE_REQUIRED"
            return {
                "action": action,
                "decision": decision,
                "self_modification": True,
                "human_acceptance_required": decision != "BLOCKED",
                "autonomous_change_forbidden": True,
                "principle": self.principle,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        decision = self.rules.get(key, "REVIEW_REQUIRED")
        return {
            "action": action,
            "decision": decision,
            "self_modification": False,
            "human_acceptance_required": decision in (
                "HUMAN_APPROVAL_REQUIRED",
                "HUMAN_ACCEPTANCE_REQUIRED",
            ),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    def status(self) -> dict:
        return {
            "governance": "ACTIVE",
            "rules": len(self.rules),
            "self_modification_policy": "HUMAN_ACCEPTANCE_REQUIRED",
            "principle": self.principle,
        }


governance = GovernanceEngine()
