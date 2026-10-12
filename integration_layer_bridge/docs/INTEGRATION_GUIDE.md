# Integration Guide – Super Cognitive ↔ Integration Layer

## Mapping

| Super Cognitive Core | Integration Layer domains |
|----------------------|---------------------------|
| Human Governance | Identity Federation + Permission Bridge |
| Intelligence Core | AI Control Plane + Event Orchestration |
| Verification Core | Data Fabric (Provenance Sync) |
| Knowledge Core | Data Fabric (Knowledge + Artifact Sync) |
| Security Core | Identity + Permission + Health Monitor |
| Execution Engine | Service Mesh + Mission Pipeline |

## Usage

```python
from integration_layer_bridge.bridge import KCNBridge

bridge = KCNBridge()
bridge.bootstrap()

alice = bridge.register_human("Alice", "alice@kcn.example")
mission = bridge.create_mission("Validate claim", alice.identity_id, ["gather", "verify"])

bridge.record_action(
    subject_id="claim-001", subject_type="knowledge", action="created",
    actor_id=alice.identity_id, content={"text": "X causes Y"},
)
package = bridge.export_evidence("claim-001")
assert package["verified"]
```
