# Fable 5 / Mythos 5 tools → KCN

Reference: Anthropic Claude Fable 5 & Mythos 5 (June 2026). Same underlying model; **Fable** = public + classifiers; **Mythos** = limited Project Glasswing, fewer safeguards.

## Official feature list (Fable/Mythos)

| Feature | KCN status |
|---------|------------|
| Effort | ✅ `reasoning_effort` on `/frontier/chat/completions` |
| Task budgets | ✅ `POST /api/v1/agent/task_budget` (+ tick) |
| Memory tool | ✅ `POST /api/v1/agent/memory` |
| Code execution | ✅ `POST /api/v1/agent/code_execution` (sandbox, no network) |
| Programmatic tool calling | ✅ `/frontier` + `/agent` catalogs |
| Context editing / tool-result clearing | ✅ `POST /api/v1/agent/context_edit` |
| Compaction | ✅ `POST /api/v1/agent/compact` |
| Vision | ✅ multimodal `image_url` parts |
| Sub-agent / long-horizon | ✅ `POST /api/v1/agent/sub_agent` |
| Self-verify | ✅ `POST /api/v1/agent/self_verify` |
| Refusal / fallback | ✅ `POST /api/v1/agent/refusal_fallback` |
| Streaming | ❌ later |
| Prompt caching | ❌ provider-side when using upstream LLM |
| Mythos unrestricted cyber/bio | ❌ **intentionally not built** |

## Design choice

KCN follows **Fable-safe** patterns: escalate high-risk domains to **human**, not unrestricted Mythos tooling.

## Catalog

```http
GET /api/v1/agent/tools
GET /api/v1/frontier/tools
```
