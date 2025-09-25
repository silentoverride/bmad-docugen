# Deployment Architecture
## Deployment Strategy
**Frontend:** Next.js server container behind Traefik within Docker Compose. Build via `pnpm --filter admin build`, output in `apps/admin/.next`, Traefik caches static assets and optional `pnpm compose:proxy` enables HTTPS via mkcert.

**Backend:** Fastify API and BullMQ workers as Docker services. Build with `pnpm --filter api build` and `pnpm --filter worker build`. Deploy with `docker-compose up --build` (wrapped by `pnpm compose:up`).

## CI/CD Pipeline
```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  lint-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: docugen
          POSTGRES_PASSWORD: docugen
          POSTGRES_DB: docugen
        ports: ['5432:5432']
      redis:
        image: redis:7
        ports: ['6379:6379']
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
      - run: pnpm install
      - run: pnpm generate:types
      - run: pnpm lint
      - run: pnpm test:unit
      - run: pnpm test:integration
      - run: pnpm test:e2e -- --headed=false --reporter=list
  build-images:
    if: github.ref == 'refs/heads/main'
    needs: lint-test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
        with:
          version: 9
      - run: pnpm install --frozen-lockfile
      - run: pnpm generate:types
      - run: pnpm docker:build
      - uses: actions/upload-artifact@v4
        with:
          name: compose-bundle
          path: infra/compose/dist
```

## Environments
| Environment | Frontend URL             | Backend URL              | Purpose                |
|-------------|--------------------------|--------------------------|------------------------|
| Development | http://localhost:3000    | http://localhost:8080    | Local development      |
| Staging     | http://staging.docugen   | http://staging.docugen   | Pre-production testing |
| Production  | http://prod.docugen      | http://prod.docugen      | Live environment       |
