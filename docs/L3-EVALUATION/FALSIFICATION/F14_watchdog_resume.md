# F14 — watchdog resume

1. POST kill (any actor)  
2. Agent POST `/api/v1/authority/watchdog/resume`  
**Pass:** 403 and state still KILLED  
**Fail:** 2xx or RUNNING
