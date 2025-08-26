# Fly.io Deployment Environment Variables Checklist

## Required Secrets (set via `fly secrets set`)

### Database Configuration
- `DATABASE_URL=postgresql+asyncpg://username:password@hostname/database?sslmode=require`

### JWT Authentication
- `JWT_SECRET_KEY=<secure-random-string>`
- `JWT_REFRESH_SECRET_KEY=<different-secure-random-string>`

### CORS Configuration
- `CORS_ORIGIN_REGEX=^https://([a-z0-9-]+)\.vercel\.app$`
- `CORS_ORIGINS=` (optional, can be empty when using regex)

### Admin User Configuration
- `ADMIN_USERNAME=admin`
- `ADMIN_PASSWORD=<secure-password>`
- `ADMIN_EMAIL=admin@ipam-tool.local`

### Optional Configuration
- `ACCESS_TOKEN_EXPIRE_MINUTES=15`
- `REFRESH_TOKEN_EXPIRE_DAYS=7`
- `LOG_LEVEL=info`
- `ENV=production`

## Deployment Commands

```bash
# Set all required secrets
fly secrets set DATABASE_URL="postgresql+asyncpg://..." -a ipam-tool
fly secrets set JWT_SECRET_KEY="your-secret-key" -a ipam-tool
fly secrets set JWT_REFRESH_SECRET_KEY="your-refresh-secret-key" -a ipam-tool
fly secrets set CORS_ORIGIN_REGEX="^https://([a-z0-9-]+)\.vercel\.app$" -a ipam-tool
fly secrets set ADMIN_USERNAME="admin" -a ipam-tool
fly secrets set ADMIN_PASSWORD="secure-password" -a ipam-tool
fly secrets set ADMIN_EMAIL="admin@ipam-tool.local" -a ipam-tool

# Deploy the application
fly deploy -a ipam-tool

# Check deployment status
fly status -a ipam-tool
fly logs -a ipam-tool
```

## Verification Steps

1. **Test health endpoint:**
   ```bash
   curl https://ipam-tool.fly.dev/healthz
   ```
   Expected: `{"status": "ok", "database": "connected"}`

2. **Test CORS preflight:**
   ```bash
   curl -X OPTIONS https://ipam-tool.fly.dev/api/auth/login \
     -H "Origin: https://ee-ipam.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -i
   ```
   Expected: HTTP 200 with `Access-Control-Allow-Origin` header

3. **Check application logs:**
   ```bash
   fly logs -a ipam-tool
   ```
   Look for startup validation messages and CORS configuration logs.
