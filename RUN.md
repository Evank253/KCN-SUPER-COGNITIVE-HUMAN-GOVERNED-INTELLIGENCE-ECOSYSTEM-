# Run KCN backend (Python-3)

## Quick start

```bash
git clone https://github.com/Evank253/KCN-SUPER-COGNITIVE-HUMAN-GOVERNED-INTELLIGENCE-ECOSYSTEM-.git
cd KCN-SUPER-COGNITIVE-HUMAN-GOVERNED-INTELLIGENCE-ECOSYSTEM-
git checkout Python-3
cd backend
export PYTHONPATH=$(pwd)
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- API docs: http://127.0.0.1:8000/docs  
- Health-style root: http://127.0.0.1:8000/

## Tests

```bash
cd backend
export PYTHONPATH=$(pwd)
pytest tests/ -q
```

## Authority checks (manual)

```bash
# F13 — expect 403
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8000/api/v1/authority/self-mod/acceptance \
  -H 'Content-Type: application/json' -H 'X-Actor-Role: agent' \
  -d '{"request_id":"demo-1","presentation":{"proof":true}}'

# Kill then F14 resume — expect 403
curl -s -X POST http://127.0.0.1:8000/api/v1/authority/watchdog/kill
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8000/api/v1/authority/watchdog/resume \
  -H 'X-Actor-Role: agent' -H 'Content-Type: application/json' -d '{}'
```

## L3 audit structure

See `docs/L3-EVALUATION/README.md`.  
Running the app locally = L2 demonstration, not L3 certification.
