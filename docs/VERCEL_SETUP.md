# Deploy KCN frontend on Vercel

Public demo (landing, Jarvis, dashboard) as a static Vite app.

## 1. Import the repo

1. Open [https://vercel.com/new](https://vercel.com/new)
2. **Import** `Evank253/KCN-SUPER-COGNITIVE-HUMAN-GOVERNED-INTELLIGENCE-ECOSYSTEM-`
3. Authorize GitHub if prompted

## 2. Project settings

| Setting | Value |
|---------|--------|
| Framework Preset | Vite |
| Root Directory | leave blank (repo root) **or** set to `frontend` |
| Build Command | `cd frontend && npm run build` (if Root = repo root) |
| Output Directory | `frontend/dist` (if Root = repo root) |
| Install Command | `cd frontend && npm ci` (if Root = repo root) |
| Production Branch | `copilot/kcn-super-cognitive-ecosystem` (or merge to `main`) |

If you set **Root Directory** to `frontend`, use:

- Build: `npm run build`
- Output: `dist`
- Install: `npm ci`

## 3. Environment variables (optional for frontend-only)

| Name | Value | Notes |
|------|--------|--------|
| `VITE_API_BASE_URL` | `https://your-api.example.com` | Leave empty for local Jarvis fallback |

Jarvis works offline without a backend (local Vibe→Kronos pipeline).

## 4. Deploy

Click **Deploy**. After success you get a URL like:

`https://kcn-….vercel.app`

Share that for the 2-week free public demo.

## 5. SPA routing

`vercel.json` rewrites all paths to `index.html` so `/jarvis`, `/dashboard`, etc. work on refresh.

## 6. Custom domain (optional)

Project → Settings → Domains → add your domain → follow DNS instructions.

## 7. Backend later

FastAPI is not on Vercel by default. Options:

- Railway / Render / Fly.io for `backend/`
- Or Docker on a VPS

Then set `VITE_API_BASE_URL` to that API origin and redeploy.

## CLI alternative

```bash
npm i -g vercel
cd frontend   # or repo root with vercel.json
vercel login
vercel --prod
```
