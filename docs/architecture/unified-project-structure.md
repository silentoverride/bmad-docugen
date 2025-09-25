# Unified Project Structure
```text
DocuGen/
├─ .github/workflows/
│  ├─ ci.yml
│  └─ build-images.yml
├─ apps/
│  ├─ admin/
│  ├─ api/
│  ├─ worker/
│  └─ cli/
├─ packages/
│  ├─ shared-types/
│  ├─ core-domain/
│  ├─ renderers/
│  ├─ integrations/
│  └─ eslint-config/
├─ infra/
│  ├─ compose/
│  │  ├─ docker-compose.yml
│  │  ├─ env/
│  │  ├─ scripts/
│  │  └─ README.md
│  ├─ migrations/
│  └─ grafana-dashboards/
├─ tools/
│  ├─ orval.config.ts
│  ├─ playwright.config.ts
│  ├─ vitest.config.ts
│  └─ tsconfig.base.json
├─ docs/
│  ├─ prd.md
│  ├─ front-end-spec.md
│  └─ architecture.md
├─ tests/
│  ├─ integration/
│  └─ fixtures/
├─ .env.example
├─ turbo.json
├─ pnpm-workspace.yaml
├─ package.json
└─ README.md
```
