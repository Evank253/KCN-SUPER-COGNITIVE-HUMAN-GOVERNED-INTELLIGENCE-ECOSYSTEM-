# Why deploy was failing + how to fix

## Root causes

1. **Vercel `npm ci`** often fails when lockfile and `package.json` drift. Fixed: use `npm install --legacy-peer-deps`.
2. **Wrong Root Directory** on Vercel — project is a monorepo; app lives in `frontend/`. Root `vercel.json` already `cd frontend`.
3. **Wrong branch** — code is on `copilot/kcn-super-cognitive-ecosystem` (and `develop`). Point Vercel Production Branch at that branch.
4. **Backend ≠ Vercel** — FastAPI backend needs **Render** (see `render.yaml`), not Vercel static hosting.

## Vercel checklist

1. Import repo on Vercel
2. Framework: Vite (or Other)
3. Root Directory: **leave blank** (repo root) — `vercel.json` handles `frontend/`
4. Production Branch: `copilot/kcn-super-cognitive-ecosystem` or `develop`
5. Redeploy

## Instant public page (no Vercel)

https://cdn.jsdelivr.net/gh/Evank253/KCN-SUPER-COGNITIVE-HUMAN-GOVERNED-INTELLIGENCE-ECOSYSTEM-@copilot/kcn-super-cognitive-ecosystem/public-demo/index.html

## Local frontend

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```
