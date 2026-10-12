# KCN Super Cognitive \u2194 Integration Layer Bridge

This package connects the **KCN Integration Layer** (Phase 11) to the  
**KCN-SUPER-COGNITIVE-HUMAN-GOVERNED-INTELLIGENCE-ECOSYSTEM-** repository.

## Quick usage

```python
from integration_layer_bridge.bridge import KCNBridge

bridge = KCNBridge()
bridge.bootstrap()

bridge.record_action(
    subject_id="hypothesis-42",
    subject_type="knowledge",
    action="validated",
    actor_id="human:alice",
    content={"claim": "X \u2192 Y", "confidence": 0.87},
)

package = bridge.export_evidence("hypothesis-42")
```

See `docs/INTEGRATION_GUIDE.md` for the full mapping of Super Cognitive cores.
