# Components
## CLI Orchestrator
**Responsibility:** Collects operator inputs, validates seeds against shared schemas, and triggers bundle runs while streaming telemetry updates in terminal sessions.

**Key Interfaces:** `POST /api/v1/configurations`, `POST /api/v1/bundles`

**Dependencies:** Bundle API, Keycloak device flow, shared config package.

**Technology Stack:** Node.js TypeScript CLI, pnpm workspace in `apps/cli`, uses WebSockets for live updates.

## Admin Web App
**Responsibility:** Surfaces run dashboards, validation results, manifest previews, and compliance approval workflows for reviewers, including dual-approval override requests.

**Key Interfaces:** `GET /api/v1/bundles`, WebSocket run events.

**Dependencies:** Bundle API, Keycloak auth, shared UI library, Prometheus metrics endpoint.

**Technology Stack:** Next.js 14, Radix UI + shadcn, Tailwind CSS; containerized for Compose.

## Bundle API (Fastify)
**Responsibility:** Core REST layer exposing configurations, bundle management, artefact access, validations, and webhook dispatch.

**Key Interfaces:** REST endpoints defined in OpenAPI; Socket.IO event stream to admin UI.

**Dependencies:** Postgres, Redis, MinIO, Vault, domain packages.

## Queue Orchestrator
**Responsibility:** Coordinates long-running bundle jobs, enqueues rendering/validation tasks, and manages retries.

**Key Interfaces:** BullMQ queues, Redis pub/sub.

**Dependencies:** Redis, Worker pool, Postgres snapshots.

## Render Worker Pool
**Responsibility:** Processes rendering tasks, generates PDFs via Puppeteer, reconciles data, and uploads artefacts to MinIO.

**Dependencies:** Redis, Postgres, MinIO, Vault, Google Places cache.

## Validation Engine
**Responsibility:** Executes deterministic reconciliation and compliance rules, recording outcomes for gating and telemetry.

## Manifest Service
**Responsibility:** Produces signed manifests, calculates hashes, and stores signature metadata for each bundle.

## Merchant & Employer Cache
**Responsibility:** Centralizes Google Places lookups, caching enriched profiles for deterministic metadata reuse.

## Audit & Telemetry Service
**Responsibility:** Aggregates audit logs, metrics, and log streams ensuring compliance traceability and operational insight.

## Auth & Access Control (Keycloak)
**Responsibility:** Issues OAuth tokens, manages roles, handles CLI device flows.

## Component Diagram
```mermaid
graph TB
    subgraph "Client Surface"
        CLI[CLI Orchestrator]
        Admin[Admin Web App]
        Partner[Partner Webhook Endpoint]
    end

    subgraph "Core Services"
        API[Bundle API]
        Queue[Queue Orchestrator]
        Worker[Render Worker Pool]
        Validator[Validation Engine]
        ManifestSvc[Manifest Service]
        MerchantSvc[Merchant Cache]
        AuditSvc[Audit & Telemetry]
    end

    subgraph "Foundations"
        Redis[(Redis / BullMQ)]
        Postgres[(Postgres)]
        MinIO[(MinIO)]
        Vault[Vault]
        Keycloak[Keycloak]
        Prometheus[Prometheus]
        Grafana[Grafana]
        Loki[Loki]
    end

    CLI -->|REST + OAuth| API
    Admin -->|REST/WebSocket| API
    API --> Keycloak
    API --> Queue
    API --> MerchantSvc
    API --> RedisCache
    API --> Postgres
    API --> AuditSvc

    Queue --> Redis
    Queue --> Worker

    Worker --> ManifestSvc
    Worker --> Redis
    Worker --> Postgres
    Worker --> MinIO
    Worker --> MerchantSvc
    Worker --> Vault
    Worker --> AuditSvc

    Validator --> Postgres
    Validator --> AuditSvc

    ManifestSvc --> Vault
    ManifestSvc --> Postgres
    ManifestSvc --> MinIO

    MerchantSvc --> Postgres
    MerchantSvc --> RedisCache

    AuditSvc --> Postgres
    AuditSvc --> Prometheus
    AuditSvc --> Loki
    Grafana --> Prometheus
    Grafana --> Loki

    API -->|Webhook Events| Partner
    Partner --> API
```
