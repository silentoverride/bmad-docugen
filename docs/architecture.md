# DocuGen Fullstack Architecture Document

## Introduction
This document outlines the complete fullstack architecture for DocuGen, covering backend services, frontend experiences, and their integration across the CLI and admin surfaces that power the DocuGen platform. It serves as the single source of truth for Codex automation agents to execute deterministic, compliance-ready builds that uphold NAB fidelity requirements.

By replacing separate backend and frontend architecture docs, we keep operations, compliance, and integration stakeholders aligned on one blueprint, ensuring regulatory guardrails, audit traceability, and automation guardrails remain front-and-center. This unified approach also streamlines coordination for engineers extending DocuGen’s APIs and UI surfaces.

The next section evaluates whether DocuGen should leverage an existing starter template or repository baseline so any inherited decisions inform the architecture choices documented here.

### Starter Template or Existing Project
N/A – Greenfield project. The PRD and UX spec make no reference to existing starter repos or vendor templates, and the current repository only contains documentation assets. We’ll design DocuGen’s architecture with full flexibility while keeping room to introduce an Nx/Turborepo-style monorepo starter later if we decide to accelerate developer tooling.

### Change Log
| Date       | Version | Description             | Author             |
|------------|---------|-------------------------|--------------------|
| 2025-09-26 | 0.1     | Initial fullstack draft | Winston (Architect) |

## High Level Architecture
### Technical Summary
DocuGen runs as a self-hosted Docker Compose stack on each developer’s machine, using a modular TypeScript monorepo that shares domain packages across CLI, admin UI, and orchestration services. The Fastify-based orchestration API and queue processors execute inside Node.js containers, coordinating deterministic bundle generation jobs dispatched through BullMQ on Redis. A Next.js admin container surfaces manifest telemetry and approvals, while the CLI (executed on the host) communicates with the API via an internal network to trigger runs and stream progress. Postgres persists run metadata, manifests, and reconciliation checkpoints; MinIO supplies S3-compatible object storage for generated PDFs and signed archives; and a lightweight Vault dev server manages local KMS-style signing keys. Shared packages enforce identical validation and rendering logic across surfaces, keeping NAB fidelity, auditability, and determinism intact without requiring cloud infrastructure.

### Platform and Infrastructure Choice
**Viable options**
- **Local Docker Compose Stack (Recommendation)** — Pros: deterministic environment parity for every developer, zero cloud dependency, easy teardown/reset between test runs, straightforward to version with the repo. Cons: limited horizontal scaling; developers must provision sufficient resources locally; coordination for shared data requires manual sync.
- **Local Kubernetes (Kind/Minikube)** — Pros: closer approximation to production orchestration, native secrets management, easier to test Helm/production manifests. Cons: higher setup complexity, steeper learning curve, slower inner loop than Docker Compose.
- **Hybrid Cloud (AWS Serverless)** — Pros: turnkey managed services (Step Functions, KMS, S3) and production-grade security primitives. Cons: contradicts requirement to self-host locally; higher operational overhead for developers when working offline.

```
**Platform:** Local Docker Compose Stack
**Key Services:** Fastify API container, Next.js admin container, Redis Queue (`redis-queue`), Redis Cache (`redis-cache`), Postgres, MinIO (object storage), Vault dev server (signing keys), Puppeteer render workers, Sentry
**Deployment Host and Regions:** Developer workstation (Docker Desktop / Podman) — single-host loopback network
```

### Repository Structure
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

### High Level Architecture Diagram
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

### Architectural Patterns
- **Service-Oriented Modular Monolith:** API and workers share a single codebase with clear module boundaries, simplifying local orchestration while keeping future extraction options open.
- **Local Event-Driven Queue (BullMQ):** Redis-backed queues decouple API triggers from heavy PDF rendering, preserving deterministic runs on constrained hardware.
- **Dual-Redis Separation:** Queue traffic uses `redis-queue` while caches live in `redis-cache`, preventing authentication/token lookups from competing with long-running jobs.
- **Shared Schema & Config Package:** Zod schemas exported from `packages/shared-types` enforce identical validation across CLI, admin, and backend.
- **Object Storage Abstraction via MinIO:** S3-compatible storage keeps manifest packaging logic identical to production plans while remaining fully local.
- **Vault-Managed Signing Keys:** Vault dev server issues in-memory KMS-style keys that workers use for manifest signing to uphold cryptographic requirements.
- **Fallback Manifest Signing:** A guarded fallback signer activates when Vault is unavailable, logs the mode change, and keeps bundles unblocked while operators restore Vault.
- **Infrastructure-as-Code for Local Stack:** `infra/compose` contains Docker Compose definitions, seed scripts, and `.env` templates ensuring deterministic onboarding.

## Tech Stack
| Category              | Technology             | Version   | Purpose                                                         | Rationale                                                                                                   |
|-----------------------|------------------------|-----------|-----------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| Frontend Language     | TypeScript             | 5.5       | Typed language for admin UI and shared packages                 | Aligns with deterministic goals; single language across stack reduces schema drift.                         |
| Frontend Framework    | Next.js                | 14.2      | Admin interface with SSR/ISR and edge-ready routing             | Pairs with Dockerized self-hosting; supports React Server Components for manifest views.                   |
| UI Component Library  | Radix UI + shadcn/ui   | 1.8       | Accessible primitives and composable admin components           | Matches accessibility goals while staying unopinionated; readily themable for NAB fidelity.                |
| State Management      | TanStack Query         | 5.51      | Data fetching/cache for manifest telemetry in admin UI          | Handles real-time status and stale-data guarantees without custom caches, improving deterministic UX.      |
| Backend Language      | TypeScript             | 5.5       | Fastify API, workers, CLI shared logic                          | Single language for API/worker/CLI ensures shared types and simplifies maintenance.                        |
| Backend Framework     | Fastify                | 4.28      | REST API server running inside Docker                           | High-performance, schema-driven validation; great fit for JSON-heavy orchestration.                        |
| API Style             | REST (OpenAPI 3.1)     | 3.1 spec  | Primary interface for CLI/admin and integrator webhooks         | Simple for automation clients; OpenAPI enables codegen and contract testing required for compliance.       |
| Database              | PostgreSQL             | 16        | Run metadata, manifests, audit records                          | Strong relational guarantees and JSONB support for manifest storage; easy to run via Docker locally.       |
| Cache                 | Redis                  | 7.2       | BullMQ queues, rate limiting, transient state                   | Lightweight, deterministic queue backbone for rendering jobs and CLI throttling.                           |
| File Storage          | MinIO                  | 2025-01-20 | S3-compatible storage for PDFs & signed bundles           | Emulates S3 locally, enabling identical packaging and hash verification flows without cloud access.        |
| Authentication        | Keycloak               | 24        | OAuth2/OpenID provider for admin UI, CLI device flow            | Self-hosted container with RBAC, audit trails, and token introspection aligned with compliance needs.      |
| Frontend Testing      | Vitest + Testing Library| 1.6 / 14 | Unit/component tests for admin UI                               | Fast TypeScript-native runner plus familiar RTL APIs keeps UI deterministic and debuggable.                |
| Backend Testing       | Vitest + Supertest     | 1.6 / 6.4 | API/service unit & integration tests                            | Shares tooling with frontend, enabling cross-stack mocks; Supertest simplifies Fastify route coverage.     |
| E2E Testing           | Playwright             | 1.48      | CLI/Admin end-to-end and PDF regression harness                 | Handles multi-browser testing plus PDF snapshot validation required for NAB fidelity checks.               |
| Build Tool            | Turborepo              | 2.0       | Orchestrate builds/tests across monorepo                        | Matches repo structure and maximizes caching inside containers or CI.                                      |
| Bundler               | tsup + Next.js SWC     | 8.1 / built-in | Bundle CLI/API/worker packages and admin app               | tsup provides fast ESM/CJS builds for Node targets; Next.js SWC handles admin with zero extra config.      |
| IaC Tool              | Docker Compose         | 2.27      | Define local self-hosted stack (services, volumes, env)         | Deterministic, version-controlled infrastructure definition shipping with repo for every developer.        |
| CI/CD                 | GitHub Actions         | Hosted 2025 | Run tests, build images, publish Compose artifacts            | Cloud CI matches repo location, supports matrix jobs, exports Docker images for teammates.               |
| Monitoring            | Prometheus + Grafana   | 2.53 / 11 | Observe worker/API metrics inside local stack                   | Lightweight dockerized observability mirroring production telemetry goals.                                |
| Logging               | Loki + Promtail        | 3.0 / 3.0 | Centralize structured logs from API/worker containers           | Ensures manifest/audit logs stay queryable and exportable for compliance reviews.                          |
| CSS Framework         | Tailwind CSS           | 3.4       | Utility-first styling for admin UI                              | Speeds iteration, aligns with shadcn defaults, and supports design tokens for NAB brand fidelity.          |

## Data Models
### DocumentBundleRun
**Purpose:** Represents a deterministic execution that produces the NAB-aligned artefact bundle, tying together inputs, validations, outputs, and audit trails.

**Key Attributes:**
- `id`: `UUID`
- `seedHash`: `string`
- `status`: `BundleStatus`
- `triggeredBy`: `ActorRef`
- `startedAt`: `Date`
- `completedAt`: `Date | null`
- `manifestId`: `UUID`
- `runParameters`: `RunParameters`

```typescript
export interface DocumentBundleRun {
  id: string;
  seedHash: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'blocked';
  triggeredBy: ActorRef;
  startedAt: Date;
  completedAt: Date | null;
  manifestId: string;
  runParameters: RunParameters;
}
```

**Relationships:** Belongs to a `ConfigurationSet`, owns `Manifest`, `DocumentArtefact`, `ValidationResult`, and `AuditLogEntry` collections.

### ConfigurationSet
**Purpose:** Captures normalized seed inputs, selected accounts, date ranges, and rendering options defining how a bundle run should execute.

```typescript
export interface ConfigurationSet {
  id: string;
  seedSource: 'uploaded' | 'fixture' | 'api';
  accounts: AccountConfig[];
  renderOptions: RenderOptions;
  createdBy: ActorRef;
}
```

### ApplicantProfile
```typescript
export interface ApplicantProfile {
  id: string;
  fullName: string;
  dateOfBirth: Date;
  primaryEmployerId: string | null;
  addresses: Address[];
}
```

### FinancialAccount
```typescript
export interface FinancialAccount {
  id: string;
  applicantId: string;
  institution: BankInstitution;
  accountNumberMasked: string;
  currency: string;
}
```

### AccountSnapshot
```typescript
export interface AccountSnapshot {
  id: string;
  bundleRunId: string;
  accountId: string;
  period: DateRange;
  openingBalance: number;
  closingBalance: number;
}
```

### TransactionRecord
```typescript
export interface TransactionRecord {
  id: string;
  snapshotId: string;
  merchantId: string | null;
  amount: number;
  occurredAt: Date;
  description: string;
}
```

### MerchantProfile
```typescript
export interface MerchantProfile {
  id: string;
  name: string;
  placesId: string | null;
  category: string;
  address: Address;
}
```

### PayslipRecord
```typescript
export interface PayslipRecord {
  id: string;
  bundleRunId: string;
  employerId: string;
  period: DateRange;
  grossPay: number;
  netPay: number;
  taxWithheld: number;
  superContribution: number;
}
```

### EmployerProfile
```typescript
export interface EmployerProfile {
  id: string;
  legalName: string;
  abn: string;
  address: Address;
  placesId: string | null;
}
```

### DocumentArtefact
```typescript
export interface DocumentArtefact {
  id: string;
  bundleRunId: string;
  type: 'bank_statement' | 'payslip' | 'proof_of_balance';
  storageKey: string;
  checksum: string;
  renderVersion: string;
}
```

### Manifest
```typescript
export interface Manifest {
  id: string;
  bundleRunId: string;
  hash: string;
  signature: string;
  signingKeyId: string;
  createdAt: Date;
  metadata: ManifestMetadata;
}
```

### ValidationResult
```typescript
export interface ValidationResult {
  id: string;
  bundleRunId: string;
  ruleCode: string;
  severity: 'info' | 'warning' | 'error';
  status: 'pass' | 'fail' | 'blocked';
  details: ValidationDetails;
}
```

### AuditLogEntry
```typescript
export interface AuditLogEntry {
  id: string;
  bundleRunId: string;
  actor: ActorRef;
  action: string;
  timestamp: Date;
  payload: Record<string, unknown>;
}
```

## API Specification
```yaml
openapi: 3.1.0
info:
  title: DocuGen Bundle API
  version: v1
  description: |
    REST interface powering DocuGen CLI, admin UI, and partner integrations. All endpoints require OAuth2 access tokens issued by Keycloak.
servers:
  - url: http://localhost:8080
    description: Local Docker Compose environment
  - url: https://api.docugen.local
    description: Tunnelled host URL for remote testing
paths:
  /api/v1/configurations:
    post:
      summary: Create a configuration set
      description: Normalises bundle inputs, account selections, and rendering options for deterministic reuse.
      tags: [Configurations]
      security:
        - oauth:
            - bundle.write
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateConfigurationRequest'
            examples:
              default:
                value:
                  seedSource: uploaded
                  seedPayload:
                    applicant:
                      fullName: "Jane Citizen"
                      dateOfBirth: "1991-03-08"
                    accounts:
                      - institution: NAB
                        bsb: "082-001"
                        accountNumber: "12345678"
                        currency: AUD
                  accounts:
                    - accountId: "primary-cheque"
                      periods:
                        - from: "2025-05-01"
                          to: "2025-07-31"
                  renderOptions:
                    locale: en-AU
                    includeWatermark: false
      responses:
        '201':
          description: Configuration created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ConfigurationSet'
        '400':
          $ref: '#/components/responses/ValidationError'
    get:
      summary: List configuration sets
      tags: [Configurations]
      security:
        - oauth:
            - bundle.read
      parameters:
        - in: query
          name: seedSource
          schema:
            $ref: '#/components/schemas/SeedSource'
        - in: query
          name: limit
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
      responses:
        '200':
          description: Paginated configuration sets
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ConfigurationSetPage'

  /api/v1/configurations/{configurationId}:
    get:
      summary: Fetch configuration details
      tags: [Configurations]
      security:
        - oauth:
            - bundle.read
      parameters:
        - $ref: '#/components/parameters/ConfigurationId'
      responses:
        '200':
          description: Configuration definition
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ConfigurationSet'
        '404':
          $ref: '#/components/responses/NotFound'

  /api/v1/bundles:
    post:
      summary: Launch a document bundle run
      tags: [Bundles]
      security:
        - oauth:
            - bundle.write
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LaunchBundleRequest'
            examples:
              default:
                value:
                  configurationId: "cfg_9b7e9d5b"
                  seedHash: "28c21c..."
                  forcingOptions:
                    skipValidations: false
      responses:
        '202':
          description: Bundle accepted for processing
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DocumentBundleRun'
    get:
      summary: List bundle runs
      tags: [Bundles]
      security:
        - oauth:
            - bundle.read
      parameters:
        - in: query
          name: status
          schema:
            $ref: '#/components/schemas/BundleStatus'
        - in: query
          name: since
          schema:
            type: string
            format: date-time
        - in: query
          name: limit
          schema:
            type: integer
            default: 20
            maximum: 100
      responses:
        '200':
          description: Paginated bundles
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BundleRunPage'

  /api/v1/bundles/{bundleId}:
    get:
      summary: Get bundle status summary
      tags: [Bundles]
      security:
        - oauth:
            - bundle.read
      parameters:
        - $ref: '#/components/parameters/BundleId'
      responses:
        '200':
          description: Bundle run
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DocumentBundleRun'
        '404':
          $ref: '#/components/responses/NotFound'

  /api/v1/bundles/{bundleId}/artefacts:
    get:
      summary: List generated artefacts for a bundle
      tags: [Bundles]
      security:
        - oauth:
            - bundle.read
      parameters:
        - $ref: '#/components/parameters/BundleId'
      responses:
        '200':
          description: Artefact collection
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ArtefactList'

  /api/v1/bundles/{bundleId}/manifest:
    get:
      summary: Retrieve signed manifest metadata
      tags: [Bundles]
      security:
        - oauth:
            - bundle.read
      parameters:
        - $ref: '#/components/parameters/BundleId'
      responses:
        '200':
          description: Manifest information
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Manifest'

  /api/v1/bundles/{bundleId}/validations:
    get:
      summary: Fetch validation results for a bundle
      tags: [Bundles]
      security:
        - oauth:
            - bundle.read
      parameters:
        - $ref: '#/components/parameters/BundleId'
      responses:
        '200':
          description: Validation results
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ValidationList'

  /api/v1/merchants/search:
    get:
      summary: Search cached merchant/employer profiles
      tags: [Reference Data]
      security:
        - oauth:
            - reference.read
      parameters:
        - in: query
          name: q
          required: true
          schema:
            type: string
            minLength: 2
        - in: query
          name: includePlacesLookup
          schema:
            type: boolean
            default: false
      responses:
        '200':
          description: Matching merchants/employers
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MerchantSearchResponse'

  /api/v1/webhooks/run-events:
    post:
      summary: Receive bundle lifecycle events
      description: Partners register a signed webhook endpoint to mirror EventBridge notifications.
      tags: [Integrations]
      security:
        - webhookSignature: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RunEvent'
      responses:
        '204':
          description: Event accepted

components:
  securitySchemes:
    oauth:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: http://localhost:8080/auth/realms/docugen/protocol/openid-connect/auth
          tokenUrl: http://localhost:8080/auth/realms/docugen/protocol/openid-connect/token
          scopes:
            bundle.read: Read bundle information
            bundle.write: Trigger bundles and manage configurations
            reference.read: Access cached merchant data
        deviceCode:
          authorizationUrl: http://localhost:8080/auth/realms/docugen/device
          tokenUrl: http://localhost:8080/auth/realms/docugen/protocol/openid-connect/token
          scopes:
            bundle.read: Read bundle information
            bundle.write: Trigger bundles and manage configurations
    webhookSignature:
      type: http
      scheme: bearer
      bearerFormat: HMAC-SHA256 signature header

  parameters:
    BundleId:
      in: path
      name: bundleId
      required: true
      schema:
        type: string
        format: uuid
    ConfigurationId:
      in: path
      name: configurationId
      required: true
      schema:
        type: string
        format: uuid

  responses:
    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    ValidationError:
      description: Request failed validation
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ValidationErrorResponse'

  schemas:
    SeedSource:
      type: string
      enum: [uploaded, fixture, api]
    ActorRef:
      type: object
      required: [type, id]
      properties:
        type:
          type: string
          enum: [cli-user, admin-user, automation]
        id:
          type: string
    RunParameters:
      type: object
      properties:
        selectedAccounts:
          type: array
          items:
            type: string
        includeWatermark:
          type: boolean
        locale:
          type: string
          default: en-AU
    CreateConfigurationRequest:
      type: object
      required: [seedSource, seedPayload, accounts]
      properties:
        seedSource:
          $ref: '#/components/schemas/SeedSource'
        seedPayload:
          type: object
          description: Structured applicant/account payload as per CLI schema.
        accounts:
          type: array
          items:
            type: object
            required: [accountId, periods]
            properties:
              accountId:
                type: string
              periods:
                type: array
                items:
                  type: object
                  required: [from, to]
                  properties:
                    from:
                      type: string
                      format: date
                    to:
                      type: string
                      format: date
        renderOptions:
          type: object
          properties:
            locale:
              type: string
              default: en-AU
            includeWatermark:
              type: boolean
              default: false
            outputFormat:
              type: string
              enum: [pdf, pdf_and_json]
    ConfigurationSet:
      type: object
      required: [id, seedSource, accounts, renderOptions, createdBy]
      properties:
        id:
          type: string
          format: uuid
        seedSource:
          $ref: '#/components/schemas/SeedSource'
        accounts:
          type: array
          items:
            type: object
            properties:
              accountId:
                type: string
              periods:
                type: array
                items:
                  type: object
                  properties:
                    from:
                      type: string
                      format: date
                    to:
                      type: string
                      format: date
        renderOptions:
          type: object
          properties:
            locale:
              type: string
            includeWatermark:
              type: boolean
            outputFormat:
              type: string
        createdBy:
          $ref: '#/components/schemas/ActorRef'
        createdAt:
          type: string
          format: date-time
    ConfigurationSetPage:
      type: object
      properties:
        items:
          type: array
          items:
            $ref: '#/components/schemas/ConfigurationSet'
        nextCursor:
          type: string
          nullable: true
    LaunchBundleRequest:
      type: object
      required: [configurationId]
      properties:
        configurationId:
          type: string
          format: uuid
        seedHash:
          type: string
          description: Optional pre-computed hash for deterministic replay.
        forcingOptions:
          type: object
          properties:
            skipValidations:
              type: boolean
            replayRunId:
              type: string
              format: uuid
    BundleStatus:
      type: string
      enum: [pending, running, completed, failed, blocked]
    DocumentBundleRun:
      type: object
      required: [id, status, triggeredBy, startedAt, manifestId, runParameters]
      properties:
        id:
          type: string
          format: uuid
        status:
          $ref: '#/components/schemas/BundleStatus'
        triggeredBy:
          $ref: '#/components/schemas/ActorRef'
        startedAt:
          type: string
          format: date-time
        completedAt:
          type: string
          format: date-time
          nullable: true
        manifestId:
          type: string
          format: uuid
        configurationId:
          type: string
          format: uuid
        runParameters:
          $ref: '#/components/schemas/RunParameters'
    BundleRunPage:
      type: object
      properties:
        items:
          type: array
          items:
            $ref: '#/components/schemas/DocumentBundleRun'
        nextCursor:
          type: string
          nullable: true
    DocumentArtefact:
      type: object
      required: [id, type, storageKey, checksum, renderVersion]
      properties:
        id:
          type: string
          format: uuid
        type:
          type: string
          enum: [bank_statement, payslip, proof_of_balance]
        storageKey:
          type: string
        checksum:
          type: string
        renderVersion:
          type: string
    ArtefactList:
      type: object
      properties:
        items:
          type: array
          items:
            $ref: '#/components/schemas/DocumentArtefact'
        presignedUrls:
          type: object
          additionalProperties:
            type: string
    Manifest:
      type: object
      required: [id, bundleRunId, hash, signature, signingKeyId, createdAt]
      properties:
        id:
          type: string
          format: uuid
        bundleRunId:
          type: string
          format: uuid
        hash:
          type: string
        signature:
          type: string
        signingKeyId:
          type: string
        createdAt:
          type: string
          format: date-time
        metadata:
          type: object
    ValidationResult:
      type: object
      required: [id, ruleCode, severity, status, details]
      properties:
        id:
          type: string
          format: uuid
        ruleCode:
          type: string
        severity:
          type: string
          enum: [info, warning, error]
        status:
          type: string
          enum: [pass, fail, blocked]
        details:
          type: object
    ValidationList:
      type: object
      properties:
        items:
          type: array
          items:
            $ref: '#/components/schemas/ValidationResult'
    MerchantSearchResponse:
      type: object
      properties:
        items:
          type: array
          items:
            type: object
            required: [id, name]
            properties:
              id:
                type: string
                format: uuid
              name:
                type: string
              category:
                type: string
              placesId:
                type: string
                nullable: true
              address:
                type: object
    RunEvent:
      type: object
      required: [bundleId, event, emittedAt]
      properties:
        bundleId:
          type: string
          format: uuid
        event:
          type: string
          enum: [RUN_STARTED, VALIDATION_FAILED, RUN_COMPLETED, MANIFEST_SIGNED]
        emittedAt:
          type: string
          format: date-time
        payload:
          type: object
    ErrorResponse:
      type: object
      required: [error]
      properties:
        error:
          type: object
          required: [code, message, requestId]
          properties:
            code:
              type: string
            message:
              type: string
            requestId:
              type: string
    ValidationErrorResponse:
      type: object
      required: [error]
      properties:
        error:
          type: object
          required: [code, message, violations]
          properties:
            code:
              type: string
              example: VALIDATION_FAILED
            message:
              type: string
            violations:
              type: array
              items:
                type: object
                required: [field, issue]
                properties:
                  field:
                    type: string
                  issue:
                    type: string
```

## Components
### CLI Orchestrator
**Responsibility:** Collects operator inputs, validates seeds against shared schemas, and triggers bundle runs while streaming telemetry updates in terminal sessions.

**Key Interfaces:** `POST /api/v1/configurations`, `POST /api/v1/bundles`

**Dependencies:** Bundle API, Keycloak device flow, shared config package.

**Technology Stack:** Node.js TypeScript CLI, pnpm workspace in `apps/cli`, uses WebSockets for live updates.

### Admin Web App
**Responsibility:** Surfaces run dashboards, validation results, manifest previews, and compliance approval workflows for reviewers, including dual-approval override requests.

**Key Interfaces:** `GET /api/v1/bundles`, WebSocket run events.

**Dependencies:** Bundle API, Keycloak auth, shared UI library, Prometheus metrics endpoint.

**Technology Stack:** Next.js 14, Radix UI + shadcn, Tailwind CSS; containerized for Compose.

### Bundle API (Fastify)
**Responsibility:** Core REST layer exposing configurations, bundle management, artefact access, validations, and webhook dispatch.

**Key Interfaces:** REST endpoints defined in OpenAPI; Socket.IO event stream to admin UI.

**Dependencies:** Postgres, Redis, MinIO, Vault, domain packages.

### Queue Orchestrator
**Responsibility:** Coordinates long-running bundle jobs, enqueues rendering/validation tasks, and manages retries.

**Key Interfaces:** BullMQ queues, Redis pub/sub.

**Dependencies:** Redis, Worker pool, Postgres snapshots.

### Render Worker Pool
**Responsibility:** Processes rendering tasks, generates PDFs via Puppeteer, reconciles data, and uploads artefacts to MinIO.

**Dependencies:** Redis, Postgres, MinIO, Vault, Google Places cache.

### Validation Engine
**Responsibility:** Executes deterministic reconciliation and compliance rules, recording outcomes for gating and telemetry.

### Manifest Service
**Responsibility:** Produces signed manifests, calculates hashes, and stores signature metadata for each bundle.

### Merchant & Employer Cache
**Responsibility:** Centralizes Google Places lookups, caching enriched profiles for deterministic metadata reuse.

### Audit & Telemetry Service
**Responsibility:** Aggregates audit logs, metrics, and log streams ensuring compliance traceability and operational insight.

### Auth & Access Control (Keycloak)
**Responsibility:** Issues OAuth tokens, manages roles, handles CLI device flows.

### Component Diagram
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

## External APIs
- **Purpose:** Enrich merchant and employer entities with canonical metadata so statements, payslips, and proofs of balance stay synchronized.
- **API:** Google Places Web Service (`https://places.googleapis.com/v1/`)
- **Authentication:** API key pulled from Vault dev server (production: service-account credentials). Backend proxy keeps keys off clients.
- **Rate Limits:** Default 90k QPD; locally throttle to 5 QPS with exponential backoff and cache-first strategy.

**Endpoints Used:**
- `POST /places:searchText`
- `GET /places/{placeId}`
- `POST /places:searchNearby`

**Integration Notes:** Backend services cache responses in Postgres + Redis for deterministic reruns. Offline/CI runs stub responses from fixtures.

## Core Workflows
```mermaid
sequenceDiagram
    autonumber
    participant CLI as CLI Operator
    participant API as Bundle API
    participant KC as Keycloak
    participant Vault as Vault
    participant Queue as BullMQ
    participant Worker as Render Worker
    participant Places as Google Places API
    participant MinIO as MinIO
    participant Postgres as Postgres
    participant Admin as Admin UI

    CLI->>KC: Device flow authorization
    KC-->>CLI: Access token
    CLI->>API: POST /api/v1/configurations
    API->>Postgres: Store configuration
    API-->>CLI: 201 Created

    CLI->>API: POST /api/v1/bundles
    API->>Queue: Enqueue render job
    API-->>CLI: 202 Accepted

    Queue-->>Worker: bundle:render
    Worker->>Postgres: Load configuration
    Worker->>Vault: Request signing key
    Worker->>Places: Merchant enrichment
    Worker->>MinIO: Upload PDFs
    Worker->>Postgres: Persist artefacts
    Worker->>Queue: Enqueue validate job

    Queue-->>Worker: bundle:validate
    Worker->>Postgres: Apply rules
    alt Success
        Worker->>Vault: Sign manifest
        Worker->>Postgres: Store manifest & pass results
        Worker->>Queue: Publish RUN_COMPLETED
    else Failure
        Worker->>Postgres: Store fail result
        Worker->>Queue: Publish VALIDATION_FAILED
    end

    Queue->>API: Emit run event
    API->>Admin: WebSocket notification
    API->>Postgres: Update run status
    Admin->>API: GET bundle detail
    Admin->>MinIO: Download artefact (signed URL)
```

```mermaid
sequenceDiagram
    autonumber
    participant Admin as Admin Reviewer
    participant API as Bundle API
    participant Postgres as Postgres
    participant Queue as BullMQ
    participant Worker as Validation Worker
    participant Audit as Audit Log

    Admin->>API: GET validations
    API-->>Admin: Validation list
    Admin->>API: POST override request
    API->>Postgres: Record override
    API->>Audit: Log intent
    API->>Queue: Enqueue re-validate

    Queue-->>Worker: bundle:validate
    Worker->>Postgres: Fetch override
    alt Passes secondary checks
        Worker->>Postgres: Mark pass + overridden
        Worker->>Audit: Log approval
        Worker->>Queue: Publish RUN_COMPLETED
    else Still failing
        Worker->>Postgres: Persist fail
        Worker->>Audit: Log rejection
        Worker->>Queue: Publish VALIDATION_FAILED
    end

    Queue->>API: Emit event
    API->>Admin: WebSocket update
```

Dual-approval is enforced: reviewers create `pending` requests, compliance leads approve with reauthentication, and audit logs capture both actions. See `docs/runbooks/override-approval.md` for the operational checklist.

## Database Schema
```sql
CREATE TYPE bundle_status AS ENUM ('pending', 'running', 'completed', 'failed', 'blocked');
CREATE TYPE seed_source AS ENUM ('uploaded', 'fixture', 'api');
CREATE TYPE validation_severity AS ENUM ('info', 'warning', 'error');
CREATE TYPE validation_status AS ENUM ('pass', 'fail', 'blocked');

CREATE TABLE configuration_sets (
    id UUID PRIMARY KEY,
    seed_source seed_source NOT NULL,
    seed_payload JSONB NOT NULL,
    render_options JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_by_type TEXT NOT NULL CHECK (created_by_type IN ('cli-user','admin-user','automation')),
    created_by_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX configuration_sets_seed_source_idx ON configuration_sets(seed_source);
CREATE INDEX configuration_sets_created_at_idx ON configuration_sets(created_at DESC);

CREATE TABLE document_bundle_runs (
    id UUID PRIMARY KEY,
    configuration_id UUID NOT NULL REFERENCES configuration_sets(id) ON DELETE RESTRICT,
    seed_hash TEXT NOT NULL,
    status bundle_status NOT NULL DEFAULT 'pending',
    triggered_by_type TEXT NOT NULL CHECK (triggered_by_type IN ('cli-user','admin-user','automation')),
    triggered_by_id TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    manifest_id UUID,
    run_parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (manifest_id)
);

CREATE INDEX bundle_runs_configuration_idx ON document_bundle_runs(configuration_id);
CREATE INDEX bundle_runs_status_idx ON document_bundle_runs(status);
CREATE INDEX bundle_runs_started_at_idx ON document_bundle_runs(started_at DESC);

CREATE TABLE employers (
    id UUID PRIMARY KEY,
    legal_name TEXT NOT NULL,
    abn TEXT UNIQUE,
    address JSONB NOT NULL,
    places_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE applicant_profiles (
    id UUID PRIMARY KEY,
    full_name TEXT NOT NULL,
    date_of_birth DATE NOT NULL,
    primary_employer_id UUID,
    addresses JSONB NOT NULL DEFAULT '[]'::jsonb,
    CONSTRAINT applicant_primary_employer_fk FOREIGN KEY (primary_employer_id) REFERENCES employers(id)
        DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE financial_accounts (
    id UUID PRIMARY KEY,
    applicant_id UUID NOT NULL REFERENCES applicant_profiles(id) ON DELETE CASCADE,
    institution JSONB NOT NULL,
    account_number_masked TEXT NOT NULL,
    currency TEXT NOT NULL CHECK (char_length(currency) = 3),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX financial_accounts_applicant_idx ON financial_accounts(applicant_id);

CREATE TABLE account_snapshots (
    id UUID PRIMARY KEY,
    bundle_run_id UUID NOT NULL REFERENCES document_bundle_runs(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES financial_accounts(id) ON DELETE CASCADE,
    period JSONB NOT NULL,
    opening_balance NUMERIC(16,2) NOT NULL,
    closing_balance NUMERIC(16,2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (bundle_run_id, account_id)
);

CREATE INDEX account_snapshots_bundle_idx ON account_snapshots(bundle_run_id);

CREATE TABLE merchants (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    places_id TEXT UNIQUE,
    address JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE transaction_records (
    id UUID PRIMARY KEY,
    snapshot_id UUID NOT NULL REFERENCES account_snapshots(id) ON DELETE CASCADE,
    merchant_id UUID REFERENCES merchants(id),
    amount NUMERIC(16,2) NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    description TEXT NOT NULL,
    extra_metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX transaction_records_snapshot_idx ON transaction_records(snapshot_id);
CREATE INDEX transaction_records_occurred_at_idx ON transaction_records(occurred_at);
CREATE INDEX transaction_records_merchant_idx ON transaction_records(merchant_id);

CREATE TABLE payslip_records (
    id UUID PRIMARY KEY,
    bundle_run_id UUID NOT NULL REFERENCES document_bundle_runs(id) ON DELETE CASCADE,
    employer_id UUID NOT NULL REFERENCES employers(id) ON DELETE RESTRICT,
    period JSONB NOT NULL,
    gross_pay NUMERIC(16,2) NOT NULL,
    net_pay NUMERIC(16,2) NOT NULL,
    tax_withheld NUMERIC(16,2) NOT NULL,
    super_contribution NUMERIC(16,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX payslip_bundle_idx ON payslip_records(bundle_run_id);

CREATE TABLE document_artefacts (
    id UUID PRIMARY KEY,
    bundle_run_id UUID NOT NULL REFERENCES document_bundle_runs(id) ON DELETE CASCADE,
    artefact_type TEXT NOT NULL CHECK (artefact_type IN ('bank_statement','payslip','proof_of_balance')),
    storage_key TEXT NOT NULL,
    checksum TEXT NOT NULL,
    render_version TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (bundle_run_id, artefact_type)
);

CREATE INDEX document_artefacts_bundle_idx ON document_artefacts(bundle_run_id);

CREATE TABLE manifests (
    id UUID PRIMARY KEY,
    bundle_run_id UUID NOT NULL UNIQUE REFERENCES document_bundle_runs(id) ON DELETE CASCADE,
    hash TEXT NOT NULL,
    signature TEXT NOT NULL,
    signing_key_id TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE validation_results (
    id UUID PRIMARY KEY,
    bundle_run_id UUID NOT NULL REFERENCES document_bundle_runs(id) ON DELETE CASCADE,
    rule_code TEXT NOT NULL,
    severity validation_severity NOT NULL,
    status validation_status NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (bundle_run_id, rule_code)
);

CREATE INDEX validation_results_bundle_idx ON validation_results(bundle_run_id);
CREATE INDEX validation_results_status_idx ON validation_results(status);

CREATE TABLE audit_log_entries (
    id UUID PRIMARY KEY,
    bundle_run_id UUID REFERENCES document_bundle_runs(id) ON DELETE CASCADE,
    actor_type TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    action TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    payload JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX audit_bundle_idx ON audit_log_entries(bundle_run_id);
CREATE INDEX audit_action_idx ON audit_log_entries(action);
CREATE INDEX audit_timestamp_idx ON audit_log_entries(timestamp DESC);
```

Automated retention is handled by `infra/compose/scripts/maintain-audit-retention.sh`, invoked nightly via cron or the scheduler service. It seeds future partitions, removes stale data following the retention policy, and exports a Prometheus timestamp gauge. Operational steps are documented in `docs/runbooks/audit-retention.md`.

## Frontend Architecture
### Component Architecture
```text
apps/admin/
├─ app/
│  ├─ (dashboard)/
│  │  ├─ layout.tsx
│  │  ├─ page.tsx
│  │  ├─ bundle/[bundleId]/
│  │  │  ├─ page.tsx
│  │  │  ├─ manifest/page.tsx
│  │  │  ├─ artefacts/page.tsx
│  │  │  ├─ _components/
│  │  │  └─ _hooks/
│  │  │  └─ loader.ts
│  │  ├─ configurations/
│  │  └─ telemetry/
│  ├─ api/
│  └─ (public)/login/page.tsx
├─ components/
├─ hooks/
├─ lib/
├─ providers/
├─ styles/
└─ tests/
```

```typescript
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { StatusBadge } from '@/components/runs/status-badge';
import { formatDistanceToNow } from 'date-fns';
import type { components } from '@/types/openapi';

type DocumentBundleRun = components['schemas']['DocumentBundleRun'];

interface BundleRunCardProps {
  run: DocumentBundleRun;
  onSelect: (id: string) => void;
}

export function BundleRunCard({ run, onSelect }: BundleRunCardProps) {
  const completedAgo = run.completedAt
    ? formatDistanceToNow(new Date(run.completedAt), { addSuffix: true })
    : 'in progress';

  return (
    <Card
      role="button"
      tabIndex={0}
      onClick={() => onSelect(run.id)}
      onKeyDown={(event) => event.key === 'Enter' && onSelect(run.id)}
      className="transition hover:border-primary focus-visible:ring"
      aria-label={`Bundle ${run.id} status ${run.status}`}
    >
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-base font-semibold">Run #{run.id.slice(0, 8)}</CardTitle>
        <StatusBadge status={run.status} />
      </CardHeader>
      <CardContent className="text-sm text-muted-foreground space-y-1">
        <p>Seed hash: {run.seedHash.slice(0, 12)}…</p>
        <p>Triggered by: {run.triggeredBy.id}</p>
        <p>Completed: {completedAgo}</p>
      </CardContent>
    </Card>
  );
}
```

### State Management Architecture
```typescript
import { QueryClient } from '@tanstack/react-query';
import { cookies } from 'next/headers';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: false,
    },
  },
});

export const runQueryKeys = {
  all: ['runs'] as const,
  list: (filters?: Record<string, unknown>) => ['runs', filters] as const,
  detail: (bundleId: string) => ['runs', bundleId] as const,
  validations: (bundleId: string) => ['runs', bundleId, 'validations'] as const,
};

export function getSessionToken() {
  return cookies().get('docugen_session')?.value ?? null;
}
```

- TanStack Query owns all server state; session tokens live in HttpOnly cookies issued by NextAuth/Keycloak.
- WebSocket handlers optimistically update queries via `setQueryData`, invalidating specific keys if payloads appear stale.
- Query stale times differentiate telemetry (5s) from reference data (60s).
- UI filters persist in URL params; user prefs stored in scoped local store that never holds secrets.
- Playwright preloads query cache using fixtures to keep UI regression tests deterministic.
- Local React state is updated immutably with `setState` spread patterns—never mutate objects or arrays in place.

### Routing Architecture
```text
app/
├─ layout.tsx
├─ middleware.ts
├─ (public)/login/page.tsx
├─ (dashboard)/
│  ├─ layout.tsx
│  ├─ page.tsx
│  ├─ bundle/[bundleId]/
│  │  ├─ page.tsx
│  │  ├─ manifest/page.tsx
│  │  ├─ artefacts/page.tsx
│  │  ├─ _components/
│  │  └─ _hooks/
│  ├─ configurations/page.tsx
│  ├─ telemetry/page.tsx
│  └─ settings/tokens/page.tsx
```

```typescript
import { decodeJwtAndRoles } from '@/lib/auth-token';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { DashboardShell } from '@/components/layout/dashboard-shell';

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const token = cookies().get('docugen_session')?.value;
  if (!token) {
    redirect('/login?reason=session-expired');
  }

  const session = await decodeJwtAndRoles(token);

  if (!session.roles.includes('bundle.read')) {
    redirect('/login?reason=insufficient-permissions');
  }

  return <DashboardShell session={session}>{children}</DashboardShell>;
}
```

### Frontend Services Layer
```typescript
import ky from 'ky';
import mitt from 'mitt';
import { getSessionToken } from '@/lib/session-token';
import { toastEmitter } from '@/lib/toast-emitter';

export const apiEvents = mitt<{ unauthorized: void }>();

export const apiClient = ky.create({
  prefixUrl: process.env.NEXT_PUBLIC_BUNDLE_API_BASE ?? 'http://localhost:8080',
  timeout: 10_000,
  hooks: {
    beforeRequest: [async (request) => {
      const token = await getSessionToken();
      if (!token) return;
      request.headers.set('Authorization', `Bearer ${token}`);
      request.headers.set('Accept', 'application/json');
    }],
    afterResponse: [
      async (_request, _options, response) => {
        if (response.status === 401) {
          apiEvents.emit('unauthorized');
          return;
        }

        if (response.status === 429) {
          toastEmitter.emit('toast', {
            title: 'Throttled',
            description: 'Too many requests. Please retry shortly.',
            variant: 'destructive',
          });
        }

        if (response.status >= 500) {
          toastEmitter.emit('toast', {
            title: 'Server error',
            description: 'DocuGen backend encountered an issue. Check telemetry dashboards.',
            variant: 'destructive',
          });
        }
      },
    ],
  },
});
```

```typescript
import { apiClient } from '@/lib/api-client';
import type { operations } from '@/types/openapi';

type FetchBundleRunsResponse = operations['getBundles']['responses']['200']['content']['application/json'];

export async function fetchBundleRuns(params?: { status?: string; since?: string }) {
  const search = new URLSearchParams();
  if (params?.status) search.set('status', params.status);
  if (params?.since) search.set('since', params.since);

  return apiClient
    .get(`api/v1/bundles${search.toString() ? `?${search}` : ''}`)
    .json<FetchBundleRunsResponse>();
}

export async function triggerBundle(configurationId: string) {
  const response = await apiClient.post('api/v1/bundles', {
    json: { configurationId },
  });

  return response.json<operations['launchBundle']['responses']['202']['content']['application/json']>();
}
```

## Backend Architecture
### Service Architecture
```text
apps/api/src/
├─ app.ts
├─ plugins/
│  ├─ auth.ts
│  ├─ redis.ts
│  ├─ postgres.ts
│  ├─ minio.ts
│  └─ vault.ts
├─ routes/
│  ├─ configurations/
│  ├─ bundles/
│  ├─ merchants/
│  └─ webhooks/
├─ services/
├─ repositories/
├─ queues/
└─ telemetry/
```

```typescript
import { FastifyInstance } from 'fastify';
import { z } from 'zod';
import { bundleService } from '@/services/bundle-service';
import { authorize } from '@/plugins/auth';

const launchBodySchema = z.object({
  configurationId: z.string().uuid(),
  seedHash: z.string().optional(),
  forcingOptions: z
    .object({
      skipValidations: z.boolean().optional(),
      replayRunId: z.string().uuid().optional(),
    })
    .optional(),
});

export async function registerBundleRoutes(app: FastifyInstance) {
  app.route({
    method: 'POST',
    url: '/api/v1/bundles',
    preHandler: authorize({ scope: 'bundle.write' }),
    schema: {
      tags: ['Bundles'],
      body: launchBodySchema,
      response: {
        202: { $ref: 'DocumentBundleRun#' },
      },
    },
    handler: async (request, reply) => {
      const body = launchBodySchema.parse(request.body);
      const result = await bundleService.launchRun({
        configurationId: body.configurationId,
        seedHash: body.seedHash,
        forcingOptions: body.forcingOptions,
        actor: request.user,
      });

      return reply.code(202).send(result);
    },
  });
}
```

### Database Architecture (Repository Example)
```typescript
import { db } from '@/plugins/postgres';
import { sql } from 'drizzle-orm';
import { bundleRuns } from '@/plugins/postgres/schema';
import type { BundleStatus } from '@/types/domain';

export const bundleRepo = {
  async createRun(input: {
    id: string;
    configurationId: string;
    seedHash: string;
    triggeredByType: string;
    triggeredById: string;
    runParameters: Record<string, unknown>;
  }) {
    await db.insert(bundleRuns).values({
      id: input.id,
      configurationId: input.configurationId,
      seedHash: input.seedHash,
      status: 'pending',
      triggeredByType: input.triggeredByType,
      triggeredById: input.triggeredById,
      runParameters: input.runParameters,
    });

    return this.findById(input.id);
  },

  findById(id: string) {
    return db.query.bundleRuns.findFirst({
      where: (fields, { eq }) => eq(fields.id, id),
      with: {
        manifest: true,
        artefacts: true,
      },
    });
  },

  async updateStatus(id: string, status: BundleStatus) {
    await db
      .update(bundleRuns)
      .set({ status, completedAt: status === 'completed' ? sql`NOW()` : null })
      .where((fields, { eq }) => eq(fields.id, id));
  },
};
```

### Authentication & Authorization
```mermaid
sequenceDiagram
    participant Client as CLI/Admin
    participant KC as Keycloak
    participant API as Fastify API
    participant Vault as Vault
    participant Redis as Redis Cache

    Client->>KC: OAuth authorization
    KC-->>Client: Access + refresh tokens (JWT)
    Client->>API: HTTPS request with Bearer token
    API->>Redis: Check cached introspection
    alt Cache hit
        Redis-->>API: Cached permissions
    else Cache miss
        API->>KC: Introspect token
        KC-->>API: Token claims & roles
        API->>Redis: Cache result with TTL
    end

    API->>API: authorize(scope)
    alt Allowed
        API->>Vault: Resolve signing key if needed
        API-->>Client: 2xx response
    else Denied
        API-->>Client: 403 Forbidden
    end
```

```typescript
import createHttpError from 'http-errors';
import type { FastifyInstance } from 'fastify';

export function registerErrorHandler(app: FastifyInstance) {
  app.setErrorHandler((error, request, reply) => {
    const requestId = request.id;

    request.log.error({ err: error, requestId }, 'Request failed');

    if (createHttpError.isHttpError(error)) {
      const { statusCode, message } = error;
      reply.status(statusCode).send({
        error: {
          code: error.expose ? error.name : 'INTERNAL_ERROR',
          message: error.expose ? message : 'Something went wrong',
          details: error.expose ? error : undefined,
          timestamp: new Date().toISOString(),
          requestId,
        },
      });
      return;
    }

    reply.status(500).send({
      error: {
        code: 'INTERNAL_ERROR',
        message: 'Something went wrong',
        timestamp: new Date().toISOString(),
        requestId,
      },
    });
  });
}
```

## Unified Project Structure
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

## Development Workflow
### Local Development Setup
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

### Environment Configuration
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

## Deployment Architecture
### Deployment Strategy
**Frontend:** Next.js server container behind Traefik within Docker Compose. Build via `pnpm --filter admin build`, output in `apps/admin/.next`, Traefik caches static assets and optional `pnpm compose:proxy` enables HTTPS via mkcert.

**Backend:** Fastify API and BullMQ workers as Docker services. Build with `pnpm --filter api build` and `pnpm --filter worker build`. Deploy with `docker-compose up --build` (wrapped by `pnpm compose:up`).

### CI/CD Pipeline
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

### Environments
| Environment | Frontend URL             | Backend URL              | Purpose                |
|-------------|--------------------------|--------------------------|------------------------|
| Development | http://localhost:3000    | http://localhost:8080    | Local development      |
| Staging     | http://staging.docugen   | http://staging.docugen   | Pre-production testing |
| Production  | http://prod.docugen      | http://prod.docugen      | Live environment       |

## Security and Performance
### Security Requirements
- **Frontend:** Strict CSP (`default-src 'self'` etc.), React strict mode, DOMPurify for dynamic content, session tokens stored in HttpOnly `docugen_session` cookie only.
- **Backend:** zod validation on every route, OWASP sanitizers for free text, Fastify rate limiting (100 req/min/IP) backed by Redis, CORS locked to known hosts, queue concurrency caps.
- **Vault Fallback:** API/worker retries transit signing, and if `ALLOW_FALLBACK_SIGNING=true`, a temporary signer activates while raising audit warnings; see `docs/runbooks/vault-outage.md`.
- **Authentication:** Keycloak-managed tokens with 60-minute access / 45-minute refresh window, Redis cache invalidated on logout, forced logout on role change, Keycloak password policy requiring ≥12 chars with complexity.

### Performance Optimization
- **Frontend:** Target <250 KB JS on first load, use streaming + Suspense skeletons, lazy-load heavy charts, TanStack Query SWR caching, Traefik caches static assets (1 hour max-age).
- **Backend:** Keep config/bundle GET endpoints under 150 ms p95 (500 ms for launch), maintain indexes on status/started_at, monthly partition audit logs, dedicate `redis-queue` to BullMQ and `redis-cache` to introspection/lookup workloads, BullMQ exporter tracks queue depth.

## Testing Strategy
```
E2E Tests
/        \
Integration Tests
/            \
Frontend Unit  Backend Unit
```

### Test Organization
```text
apps/admin/__tests__/
├─ components/
├─ hooks/
├─ fixtures/
└─ setup-tests.ts
```
```text
apps/api/tests/
├─ routes/
├─ services/
├─ repositories/
├─ fixtures/
└─ setup.ts
```
```text
tests/e2e/
├─ specs/
├─ fixtures/
├─ commands/
└─ setup.ts
```

### Test Examples
```typescript
import { render, screen } from '@testing-library/react';
import { BundleRunCard } from '@/components/runs/bundle-run-card';
import runFixture from '../fixtures/bundle-run.json';

describe('BundleRunCard', () => {
  it('shows run metadata and status badge', () => {
    const onSelect = vi.fn();
    render(<BundleRunCard run={runFixture} onSelect={onSelect} />);
    expect(screen.getByText(/Run #/)).toBeInTheDocument();
    screen.getByRole('button').click();
    expect(onSelect).toHaveBeenCalledWith(runFixture.id);
  });
});
```

```typescript
import { buildTestServer } from '../setup';
import configurationFixture from '../fixtures/configuration.json';

describe('POST /api/v1/bundles', () => {
  const app = buildTestServer();

  beforeAll(async () => {
    await app.ready();
    await app.prisma.configuration.create({ data: configurationFixture });
  });

  afterAll(() => app.close());

  it('queues a bundle run and returns 202', async () => {
    const response = await app.inject({
      method: 'POST',
      url: '/api/v1/bundles',
      headers: { authorization: 'Bearer test-token-with-bundle.write' },
      payload: { configurationId: configurationFixture.id },
    });

    expect(response.statusCode).toBe(202);
  });
});
```

```typescript
import { test, expect } from '@playwright/test';
import { runCli } from '../commands/cli';

test('operator launches bundle and reviewer approves', async ({ page }) => {
  await runCli(['bundle', 'launch', '--config', 'tests/fixtures/seeds/sample-applicant.json']);
  await page.goto('http://localhost:3000');
  await page.getByRole('button', { name: /Run #/ }).first().click();
  await expect(page.getByText('Validations')).toBeVisible();
  await page.getByRole('button', { name: 'Override validation' }).click();
  await page.getByLabel('Justification').fill('Manual review based on NAB docs');
  await page.getByRole('button', { name: 'Submit override' }).click();
  await expect(page.getByText('Run status: completed')).toBeVisible();
});
```

## Coding Standards
- **Type Source of Truth:** Import all TypeScript types from `packages/shared-types`; never redeclare interfaces inside apps.
- **IO Boundaries:** Use shared IO helpers (`apiClient`, `packages/core-domain` job builders) for HTTP and BullMQ payloads; no ad-hoc fetch calls or JSON bodies.
- **Secrets & Config:** Load secrets/signing keys through Vault or env config helpers; never hardcode credentials or reach for `process.env` inside business logic.
- **Standard Error Handling:** Fastify handlers respond via `reply.sendError`/`createHttpError`; workers use the job failure utility so telemetry stays consistent.
- **Structured Logging & Telemetry:** Use the shared pino logger (`packages/core-domain/logger`) with run/bundle IDs; avoid `console.log` in production code.
- **Deterministic Fixtures:** Tests import fixtures from `tests/fixtures` and update via scripts—no inline JSON or random data.
- **Immutable React State:** Local component state must be updated immutably using `setState`/spread patterns; never mutate objects or arrays in place even outside Query/Zustand.

| Element          | Frontend                    | Backend    | Example                    |
|------------------|-----------------------------|------------|----------------------------|
| Components       | PascalCase                  | –          | `BundleRunCard.tsx`        |
| Hooks            | camelCase with 'use'        | –          | `useAuthSession.ts`        |
| API Routes       | –                           | kebab-case | `/api/v1/bundle-runs`      |
| Database Tables  | –                           | snake_case | `document_bundle_runs`     |

## Error Handling Strategy
```mermaid
sequenceDiagram
    participant Client as CLI/Admin UI
    participant API as Fastify API
    participant Service as Domain Service
    participant Repo as Repository
    participant Logger as Logger/Telemetry

    Client->>API: Request
    API->>Service: execute()
    Service->>Repo: persist/read
    Repo-->>Service: error (DB constraint)
    Service->>Logger: capture error + context
    Service-->>API: throw createHttpError
    API->>Logger: log request error with requestId
    API-->>Client: JSON error response (code/message/requestId)
    Client->>Client: display toast linking telemetry
```

```typescript
interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
    timestamp: string;
    requestId: string;
  };
}
```

```typescript
import { toastEmitter } from '@/lib/toast-emitter';
import type { ApiError } from '@/types/openapi';

export function handleApiError(error: unknown) {
  if (typeof error === 'object' && error !== null && 'error' in error) {
    const apiError = error as ApiError;
    toastEmitter.emit('toast', {
      title: apiError.error.code,
      description: apiError.error.message,
      variant: 'destructive',
      action: {
        label: 'View Logs',
        onClick: () => window.open(`/telemetry?requestId=${apiError.error.requestId}`, '_blank'),
      },
    });
    return;
  }

  toastEmitter.emit('toast', {
    title: 'Unexpected error',
    description: 'An unexpected error occurred. Check the console for details.',
    variant: 'destructive',
  });
}
```

```typescript
import createHttpError from 'http-errors';
import type { FastifyInstance } from 'fastify';

export function registerErrorHandler(app: FastifyInstance) {
  app.setErrorHandler((error, request, reply) => {
    const requestId = request.id;

    request.log.error({ err: error, requestId }, 'Request failed');

    if (createHttpError.isHttpError(error)) {
      const { statusCode, message } = error;
      reply.status(statusCode).send({
        error: {
          code: error.expose ? error.name : 'INTERNAL_ERROR',
          message: error.expose ? message : 'Something went wrong',
          details: error.expose ? error : undefined,
          timestamp: new Date().toISOString(),
          requestId,
        },
      });
      return;
    }

    reply.status(500).send({
      error: {
        code: 'INTERNAL_ERROR',
        message: 'Something went wrong',
        timestamp: new Date().toISOString(),
        requestId,
      },
    });
  });
}
```

## Monitoring and Observability
- **Frontend Monitoring:** Next.js emits custom metrics through `apps/admin/lib/metrics-client` into Prometheus; Grafana dashboards track Core Web Vitals and WebSocket latency.
- **Backend Monitoring:** Fastify’s pino transport streams structured logs to Loki; `/metrics` exposes Prometheus counters for request/queue activity, Vault health (`vault_up`), and audit retention timestamps with Grafana dashboards for bundle throughput.
- **Error Tracking:** Self-hosted Sentry captures admin/API exceptions, tagging each with `requestId`; alerts flow to Slack.
- **Performance Monitoring:** Prometheus + Grafana visualize latency/CPU/memory; k6 scripts optional for load; BullMQ exporter surfaces queue depth and processing durations.

**Frontend Metrics:**
- Core Web Vitals
- JavaScript errors
- API response times
- User interactions

**Backend Metrics:**
- Request rate
- Error rate
- Response time
- Database query performance

## Operational Runbooks
- `docs/runbooks/vault-outage.md` – Vault health, fallback signer, and recovery steps
- `docs/runbooks/redis-operations.md` – Redis queue/cache management and troubleshooting
- `docs/runbooks/override-approval.md` – Dual-approval process for validation overrides
- `docs/runbooks/audit-retention.md` – Automated pruning script usage and verification

## Checklist Results Report
The Architect validation (2025-09-26) rated the solution **High readiness**. All checklist sections were reviewed with the following outcomes:

| Section | Status | Notes |
|---------|--------|-------|
| Requirements Alignment | ✅ | Functional/non-functional requirements mapped to components, workflows, and observability. |
| Architecture Fundamentals | ✅ | Monorepo layout, diagrams, and service boundaries clearly documented. |
| Data & Integration Design | ✅ | Entities, OpenAPI schema, Redis split, and Google Places integration covered. |
| Security & Compliance | ⚠️ | Vault fallback documented; ongoing operational vigilance required (see `docs/runbooks/vault-outage.md`). |
| Performance & Scalability | ⚠️ | Resource demands and Redis queue/cache isolation addressed; monitor developer hardware guidance. |
| Observability & Operations | ✅ | Prometheus/Loki/Grafana stack, runbooks, and push-gateway integration defined. |
| AI Implementation Suitability | ✅ | Coding standards, naming conventions, and examples tailored for automation agents. |
| Accessibility (Frontend) | ⚠️ | UX spec ensures WCAG alignment; future automation should enforce accessibility tests. |

Outstanding watch items:
- Continue refining override approval UX to enforce dual-approval ergonomics.
- Monitor audit-retention job metrics and adjust retention windows as real data dictates.
- Review hardware footprint after longer test runs and update onboarding guidance if necessary.
