# High Level Architecture
## Technical Summary
DocuGen runs as a self-hosted Docker Compose stack on each developer’s machine, using a modular TypeScript monorepo that shares domain packages across CLI, admin UI, and orchestration services. The Fastify-based orchestration API and queue processors execute inside Node.js containers, coordinating deterministic bundle generation jobs dispatched through BullMQ on Redis. A Next.js admin container surfaces manifest telemetry and approvals, while the CLI (executed on the host) communicates with the API via an internal network to trigger runs and stream progress. Postgres persists run metadata, manifests, and reconciliation checkpoints; MinIO supplies S3-compatible object storage for generated PDFs and signed archives; and a lightweight Vault dev server manages local KMS-style signing keys. Shared packages enforce identical validation and rendering logic across surfaces, keeping NAB fidelity, auditability, and determinism intact without requiring cloud infrastructure.

## Platform and Infrastructure Choice
**Viable options**
- **Local Docker Compose Stack (Recommendation)** — Pros: deterministic environment parity for every developer, zero cloud dependency, easy teardown/reset between test runs, straightforward to version with the repo. Cons: limited horizontal scaling; developers must provision sufficient resources locally; coordination for shared data requires manual sync.
- **Local Kubernetes (Kind/Minikube)** — Pros: closer approximation to production orchestration, native secrets management, easier to test Helm/production manifests. Cons: higher setup complexity, steeper learning curve, slower inner loop than Docker Compose.
- **Hybrid Cloud (AWS Serverless)** — Pros: turnkey managed services (Step Functions, KMS, S3) and production-grade security primitives. Cons: contradicts requirement to self-host locally; higher operational overhead for developers when working offline.

```
**Platform:** Local Docker Compose Stack
**Key Services:** Fastify API container, Next.js admin container, Redis Queue (`redis-queue`), Redis Cache (`redis-cache`), Postgres, MinIO (object storage), Vault dev server (signing keys), Puppeteer render workers, Sentry
**Deployment Host and Regions:** Developer workstation (Docker Desktop / Podman) — single-host loopback network
```

## Repository Structure
```
**Structure:** Monorepo with apps + shared packages
**Monorepo Tool:** Turborepo (pnpm workspaces)
**Package Organization:** 
- apps/cli (Node entrypoint)
- apps/admin (Next.js admin UI)
- apps/api (Fastify REST API + orchestrator)
- apps/worker (Puppeteer render/validation workers)
- packages/core-domain (domain logic & reconciliation rules)
- packages/renderers (document templates & helpers)
- packages/integrations (Google Places client, manifest signing utilities)
- packages/shared-types (zod schemas & TS types)
- infra/compose (Docker Compose definitions, env templates, setup scripts)
```

## High Level Architecture Diagram
```mermaid
graph TB
    Host[Developer Host OS] -->|docker exec| Compose[Docker Compose Network]

    subgraph "Docker Network"
        Admin[Next.js Admin Container]
        API[Fastify API & Orchestrator]
        Worker[Puppeteer Worker Pool]
        RedisQueue[Redis Queue]
        RedisCache[Redis Cache]
        Postgres[(Postgres)]
        MinIO[(MinIO Object Storage)]
        Vault[Vault Dev Server]
        Temporal[(Optional Temporal Dev)]:::optional
    end

    OpsCLI[Lending Ops CLI (Host)] -->|REST/WebSocket| API
    AdminUser[Admin Browser] -->|http://localhost| Admin

    Admin --> API
    API --> RedisQueue
    RedisQueue --> Worker
    Worker --> MinIO
    Worker --> Vault
    Worker --> Postgres
    API --> Postgres
    API --> Vault
    MinIO -->|Signed URLs| Admin
    API -->|Event streams via Socket.IO| Admin

    Integrator[Partner Emulator / Tests] -->|Webhook Stubs| API

    classDef optional stroke-dasharray: 5 5;
```

## Architectural Patterns
- **Service-Oriented Modular Monolith:** API and workers share a single codebase with clear module boundaries, simplifying local orchestration while keeping future extraction options open.
- **Local Event-Driven Queue (BullMQ):** Redis-backed queues decouple API triggers from heavy PDF rendering, preserving deterministic runs on constrained hardware.
- **Dual-Redis Separation:** Queue traffic uses `redis-queue` while caches live in `redis-cache`, preventing authentication/token lookups from competing with long-running jobs.
- **Shared Schema & Config Package:** Zod schemas exported from `packages/shared-types` enforce identical validation across CLI, admin, and backend.
- **Object Storage Abstraction via MinIO:** S3-compatible storage keeps manifest packaging logic identical to production plans while remaining fully local.
- **Vault-Managed Signing Keys:** Vault dev server issues in-memory KMS-style keys that workers use for manifest signing to uphold cryptographic requirements.
- **Fallback Manifest Signing:** A guarded fallback signer activates when Vault is unavailable, logs the mode change, and keeps bundles unblocked while operators restore Vault.
- **Infrastructure-as-Code for Local Stack:** `infra/compose` contains Docker Compose definitions, seed scripts, and `.env` templates ensuring deterministic onboarding.
