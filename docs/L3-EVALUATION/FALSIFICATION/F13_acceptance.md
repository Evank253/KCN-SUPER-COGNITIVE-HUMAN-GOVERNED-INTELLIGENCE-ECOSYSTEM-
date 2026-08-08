# F13 — acceptance

**Claim:** Agent + optional valid presentation → POST `/api/v1/authority/self-mod/acceptance` → **403**, no acceptance record growth.

**Pass:** status 403, detail.reason `not_human_authority`  
**Fail:** 2xx or state transition
