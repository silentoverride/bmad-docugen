# Story 1.4 Expose Generation API Surface

## Status
Approved

## Story
**As a** platform integration engineer,
**I want** an authenticated API surface for triggering document generation,
**so that** partner systems can orchestrate DocuGen without relying solely on the CLI.

## Acceptance Criteria
1. REST API endpoint accepts the same configuration payload as the CLI, validating input via shared schema modules.
2. Requests require authenticated service tokens with role scopes that mirror operator RBAC rules.
3. API responses include run manifest identifiers and status links consistent with CLI outputs.
4. OpenAPI specification and usage guide document request/response formats, auth setup, and rate limits.

## Tasks / Subtasks
- [ ] Implement authenticated REST endpoint that triggers generation using shared schema and orchestrator (AC: 1)
- [ ] Integrate token-based auth and role scopes aligned with operator permissions (AC: 2)
- [ ] Return manifest identifiers, status polling URLs, and error payloads that match CLI semantics (AC: 3)
- [ ] Publish OpenAPI spec and partner usage guide covering auth, rate limits, and example flows (AC: 4)

## Dev Notes
- API handler module: add `POST /api/v1/bundles` to `apps/api/src/routes/bundles.route.ts`, delegating to `apps/api/src/controllers/bundles.controller.ts#createBundle`.
- Request schema: reuse Story 1.1 configuration schema by importing `packages/shared-types/schema/configuration.json` (validate via the same Zod parser used by CLI Story 1.2).
- Auth scopes: enforce Keycloak client `docugen-api` with role scopes `bundle:submit` for submission and `bundle:status` for polling. Map service accounts via Keycloak configuration documented in `docs/architecture/backend-architecture.md#authentication-authorization`.
- Response payload: include `runId`, `manifestId`, and `statusUrl` (e.g., `/api/v1/bundles/{runId}/status`). Align manifest metadata with Story 1.2 naming conventions.
- OpenAPI updates: update `docs/architecture/api-specification.md` and run `pnpm generate:types` to refresh SDKs. Document example requests/responses in `docs/prd/api-usage.md` (new section).
- Rate limiting: integrate with queue controls from Story 1.5 using `apps/api/src/middleware/rate-limit.ts`, default limits from env `DOCUGEN_API_RPM`.
- Logs/telemetry: emit audit entries via `packages/core-domain/audit` capturing token subject, runId, and config hash to satisfy Epic 3 observability expectations.

### Testing
- Add integration tests invoking the API endpoint with valid and invalid payloads to exercise validation and auth failures.
- Include contract tests to ensure response structures remain backwards compatible once published.

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
