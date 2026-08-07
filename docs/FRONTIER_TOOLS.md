# KCN Frontier Tools

Tools aligned with open frontier model APIs (e.g. Kimi K3 style), **plus** human governance that pure weight releases do not include.

## Endpoints

| Method | Path | Purpose |
|--------|------|--------|
| GET | `/api/v1/frontier/tools` | Catalog of built-in tools |
| POST | `/api/v1/frontier/chat/completions` | OpenAI-compatible chat |
| POST | `/api/v1/frontier/tools/execute` | Run a governed tool |
| GET | `/api/v1/frontier/tracking` | Timestamped call log |

## Parity with frontier APIs

| Capability | Support |
|------------|--------|
| `reasoning_effort` (`low` / `high` / `max`) | Yes |
| `reasoning_content` preserved on assistant messages | Yes |
| Multimodal `content` parts (`text`, `image_url`) | Yes |
| `tools` / `tool_calls` function calling | Yes |
| Session continuity (`session_id`) | Yes |
| Upstream LLM passthrough | Yes (`KCN_LLM_*`) |
| Streaming | Not yet (501) |

## Tools only KCN has

- `vibe_build` — Vibe → Kronos pipeline  
- `verify_artifact` — SHA-256 + pass checks  
- `governance_check` — human policy gate  
- `experiment_gate` — sandbox / network / subjects  
- `tracking_append` — explicit audit phase log  

## Upstream (optional)

```bash
export KCN_LLM_BASE_URL=https://api.moonshot.ai/v1   # or Together / vLLM
export KCN_LLM_API_KEY=sk-...
export KCN_LLM_MODEL=kimi-k3
```

Without these, local governed replies + tool heuristics still work.

## Example

```bash
curl -s http://localhost:8000/api/v1/frontier/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "kcn-k3-governed",
    "reasoning_effort": "max",
    "messages": [{"role": "user", "content": "Build a small typescript helper"}]
  }'
```
