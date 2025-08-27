# ee-ipam

Production-grade IPAM monorepo (FastAPI backend + Vite React frontend)

- Backend: FastAPI, async SQLAlchemy + asyncpg, Alembic, JWT auth, CORS from env, /healthz
- Frontend: Vite + React + TS + Tailwind + shadcn/ui; React Query + Axios with HTTPS-only API

Backend environment (.env or Fly secrets):
- DATABASE_URL=postgresql+asyncpg://.../fly-db?sslmode=require
- JWT_SECRET_KEY=...
- JWT_REFRESH_SECRET_KEY=...
- ACCESS_TOKEN_EXPIRE_MINUTES=15
- REFRESH_TOKEN_EXPIRE_DAYS=7
- CORS_ORIGINS=<frontend-origin> (comma-separated exact origins, e.g., https://ipam.yourdomain.com; required unless CORS_ORIGIN_REGEX is set)
- CORS_ORIGIN_REGEX=regex for previews (e.g., ^https://([a-z0-9-]+)\.vercel\.app$)
- LOG_LEVEL=info
- ENV=production
- ADMIN_USERNAME=admin
- ADMIN_PASSWORD=changeme123!

At least one of `CORS_ORIGINS` or `CORS_ORIGIN_REGEX` must be set.

Frontend environment (.env.production or Vercel env):
- VITE_API_BASE=https://ipam-tool.fly.dev/api

CORS policy:
- Do not hardcode origins. Load from env.
- Include production domain(s) via CORS_ORIGINS and preview domains via CORS_ORIGIN_REGEX.
- Example regex for Vercel previews: ^https://([a-z0-9-]+)\.vercel\.app$

HTTPS-only:
- Frontend must use HTTPS API base in production. No http:// defaults.
- In development, http://localhost is allowed.

Health check:
- GET /healthz returns {"status":"ok"} and validates DB connectivity.

Seeding admin:
- On container start, after migrations, the app ensures an admin user exists using ADMIN_USERNAME and ADMIN_PASSWORD (defaults shown above). If the User model uses email (no username field), the admin will be created with email admin@local by default (override with ADMIN_EMAIL). Rotate credentials post-deploy by updating secrets and redeploying.

Deploy
- Fly.io (backend):
- Set secrets: DATABASE_URL (with sslmode=require), JWT_SECRET_KEY, JWT_REFRESH_SECRET_KEY, CORS_ORIGINS (or CORS_ORIGIN_REGEX), ADMIN_USERNAME, ADMIN_PASSWORD.
  - fly deploy -a ipam-tool
- Vercel (frontend):
  - Set VITE_API_BASE=https://ipam-tool.fly.dev/api
  - vercel deploy --prod

CI/CD via GitHub
- Wire up GitHub
  - Create an empty private repo in your org (e.g., ee-ipam). Copy the HTTPS URL.
  - From repo root:
    - git init
    - git remote add origin https://github.com/&lt;org&gt;/ee-ipam.git
    - git checkout -b main
    - git add backend frontend .github README.md .gitignore
    - git commit -m "Initial import: IPAM monorepo with Fly/Vercel CI"
    - git push -u origin main

- Add Repo Secrets (GitHub → Settings → Secrets and variables → Actions)
  - FLY_API_TOKEN: your FlyV1 token (paste the entire string exactly as provided, including the comma)

- Frontend deployment (Vercel Git Integration)
  - In Vercel, import the GitHub repo to your team.
  - Root Directory: frontend
  - Build Command: npm run build
  - Output Directory: dist
  - Environment Variables (Production & Preview): VITE_API_BASE=https://ipam-tool.fly.dev/api
  - Ensure Production Protection is disabled or configured as desired.
  - Note: The GitHub Action at .github/workflows/vercel-deploy.yml is disabled and can be ignored (kept only for future/manual use).

- Backend deployment (GitHub Actions → Fly.io)
  - Workflow: .github/workflows/fly-deploy.yml
  - Deploys backend/ to Fly app ipam-tool on push to main.

- First Deploy from GitHub
  - Push to main; GitHub Actions:
    - Deploy Backend to Fly.io runs via flyctl and releases backend.
  - Vercel Git Integration builds/deploys the frontend automatically from GitHub.
  - Verify:
    - Backend: https://ipam-tool.fly.dev/healthz returns {"status":"ok"}
    - Frontend: visit /login and other deep links (SPA rewrites prevent 404). If redirected to Vercel login, disable Production Protection or share bypass.
