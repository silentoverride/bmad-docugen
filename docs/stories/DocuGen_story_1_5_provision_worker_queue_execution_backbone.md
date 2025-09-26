# Story 1.5 Provision Worker Queue Execution Backbone

## Status
Approved

## Story
**As a** platform reliability engineer,
**I want** a managed worker queue governing render jobs,
**so that** DocuGen meets concurrency SLAs without sacrificing determinism.

## Acceptance Criteria
1. Queue service (e.g., BullMQ) schedules CLI/API generation jobs with configurable concurrency limits.
2. Jobs inherit deterministic seeds and produce identical outputs regardless of queue ordering.
3. Operational dashboards expose queue depth, processing time, and failure metrics for SRE monitoring.
4. Fallback and retry policies are defined, tested, and documented for partial failures.

## Tasks / Subtasks
- [ ] Implement worker queue backing CLI/API generation requests with configurable concurrency (AC: 1)
- [ ] Ensure job execution reuses deterministic seed and manifest logic to guarantee identical outputs (AC: 2)
- [ ] Surface queue metrics and alerts through observability stack established in Epic 3.4 (AC: 3)
- [ ] Define retry/backoff policies with documentation and tests covering failure scenarios (AC: 4)

## Dev Notes
- Queue implementation:
  - Create BullMQ queue definition in `apps/api/src/queues/generation.queue.ts` with job name `bundle:generate` and configurable concurrency via env `DOCUGEN_QUEUE_CONCURRENCY`.
  - API Story 1.4 and CLI Story 1.2 should both enqueue jobs through `packages/core-domain/queue/submit-generation-job.ts` to avoid duplicated logic.
- Worker processing:
  - Worker entry point `apps/worker/src/processors/generation.processor.ts` must load seeds via `packages/core-domain/seeding/` (Story 1.1 utilities) and invoke orchestrator from Story 1.2 so deterministic seeds carry through queue execution.
  - Ensure manifests produced still land in `manifests/{bundleRunId}.json` and artefacts in `artefacts/{bundleRunId}/`.
- Retry/backoff:
  - Configure BullMQ `backoff: {type: 'exponential', delay: 5000}` with `attempts` pulled from env `DOCUGEN_QUEUE_MAX_ATTEMPTS`.
  - Record failures to dead-letter queue `bundle:generate:dlq` with metadata for ops review; integrate fallback docs with Story 3.4 runbooks.
- Monitoring:
  - Emit metrics via Prometheus exporter in `packages/observability/queue-metrics.ts` for queue depth, processing duration, and failure counts.
  - Expose alerts to Story 3.4 dashboards using metrics `queue_bundle_generate_depth` and `queue_bundle_generate_failures_total`.
- Documentation: update `docs/architecture/operational-runbooks.md` with retry policy and dead-letter handling; ensure Story 3.4 references the new metrics panels.

## Cross-epic dependencies
- Epic 3 – Story 3.4 supplies the observability dashboards that surface queue health metrics and alerts.

### Testing
- Create integration tests simulating concurrent job submissions to verify deterministic outputs.
- Add resilience tests that force worker failures and confirm retry logic plus alerting behaviour.

## Change Log
| Date       | Version | Description         | Author |
|------------|---------|---------------------|--------|
| 2025-09-28 | 0.2     | Approved for implementation | PO     |
| 2025-09-28 | 0.1     | Initial story draft | PO     |

## Dev Agent Record
### Agent Model Used
_Pending assignment._

### Debug Log References
_Pending assignment._

### Completion Notes List
_Pending assignment._

### File List
_Pending assignment._

## QA Results
_Pending review._
