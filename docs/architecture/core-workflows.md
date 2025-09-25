# Core Workflows
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
