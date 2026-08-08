# Verify (honest path)

```bash
cd backend
./test.sh
# expect authority boundary tests to PASS

curl -s http://127.0.0.1:8000/ | head
curl -s -X POST http://127.0.0.1:8000/api/v1/authority/self-mod/acceptance \
  -H 'Content-Type: application/json' -H 'X-Actor-Role: agent' \
  -d '{"request_id":"f13-manual","presentation":{"ok":true}}'
# expect 403
```
