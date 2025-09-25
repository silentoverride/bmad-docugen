# Development Workflow
## Local Development Setup
```bash
# Required tooling
# (Use native installers on Linux/Windows if brew is unavailable)
pnpm --version || npm install -g pnpm
brew install docker docker-compose || true
brew install node@20 || true

# Clone repository + install deps
pnpm install

# Generate OpenAPI types
pnpm generate:types

# Prime local services (Keycloak realm, Postgres schema, fixtures)
pnpm compose:setup
```

```bash
# Start all services (foreground)
pnpm compose:up

# Optional detached mode
pnpm compose:up -- -d && pnpm compose:logs

# Start frontend only
pnpm --filter admin dev

# Start backend only (uses concurrently)
pnpm dev:backend

# Run tests
pnpm lint
pnpm test:unit
pnpm test:integration
pnpm test:e2e
```

## Environment Configuration
```bash
# Frontend (.env.local)
NEXT_PUBLIC_BUNDLE_API_BASE=http://localhost:8080
NEXT_PUBLIC_WEBSOCKET_URL=http://localhost:8081
NEXT_PUBLIC_KEYCLOAK_REALM=docugen
NEXT_PUBLIC_KEYCLOAK_CLIENT_ID=docugen-admin-ui
NEXT_PUBLIC_SENTRY_DSN=http://sentry:9000/1

# Backend (.env)
PORT=8080
KEYCLOAK_URL=http://keycloak:8080/auth
KEYCLOAK_REALM=docugen
KEYCLOAK_CLIENT_ID=docugen-api
KEYCLOAK_CLIENT_SECRET=local-secret
DATABASE_URL=postgres://docugen:docugen@postgres:5432/docugen
REDIS_QUEUE_URL=redis://redis-queue:6379
REDIS_CACHE_URL=redis://redis-cache:6379
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=docugen
MINIO_SECRET_KEY=docugen123
VAULT_ADDR=http://vault:8200
VAULT_TOKEN=root
ALLOW_FALLBACK_SIGNING=false

# Shared
GOOGLE_PLACES_API_KEY=replace-me-for-online
PROM_PUSH_GATEWAY_URL=http://prometheus-pushgateway:9091
default_SEED_FIXTURE=tests/fixtures/seeds/default.json
PLAYWRIGHT_TEST_BASE_URL=http://localhost:3000
```
