# Story 2.2 Integrate Merchant and Employer Enrichment

## Status
Approved

## Story
**As a** document reviewer,
**I want** merchant and employer details enriched via Google Places with deterministic caching,
**so that** artefacts display credible Australian entities without external flakiness.

## Acceptance Criteria
1. Google Places integration retrieves legal name, suburb, and ABN-like metadata, storing responses in encrypted cache with configurable TTL.
2. Offline fallback dataset covers top 100 Australian merchant categories relevant to lending use cases.
3. Cache miss, fallback use, and enrichment overrides are logged in manifests for audit replay.
4. Integration tests simulate quota exhaustion and offline modes to confirm deterministic outputs.

## Tasks / Subtasks
- [ ] Implement Google Places client with encrypted cache and configurable TTL (AC: 1)
- [ ] Curate offline fallback dataset for top merchant categories and hook into enrichment flow (AC: 2)
- [ ] Extend manifest logging to record cache hits, fallbacks, and manual overrides (AC: 3)
- [ ] Add integration tests covering quota exhaustion, offline execution, and deterministic outputs (AC: 4)

## Dev Notes
- Google Places integration:
  - Implement client in `packages/integrations/google-places/client.ts` with helpers `lookupMerchant(placeId)` and `lookupEmployer(placeId)` returning the normalised shape consumed by Story 1.1 schemas.
  - Configure API key via env `GOOGLE_PLACES_API_KEY`; wrap HTTP calls with deterministic retry policy (no random jitter) to preserve reproducibility.
- Encrypted caching layer:
  - Add cache adapter `packages/core-domain/cache/enrichment-cache.ts` using BullMQ/Redis namespace `enrichment:` with TTL from env `GOOGLE_PLACES_CACHE_TTL_MINUTES` (default 10080 = 7 days).
  - Encrypt cache payloads with Vault transit key `docugen-enrichment` (or local AES fallback) as described in `docs/architecture/security-and-performance.md`.
- Offline fallback dataset:
  - Store curated records in `tests/fixtures/enrichment/offline-merchants.json` and `offline-employers.json` with fields `legalName`, `category`, `abn`, `suburb`.
  - Document update cadence in `docs/runbooks/enrichment-dataset.md`; include sourcing instructions and review checklist with operations team.
- Manifest & logging:
  - Append enrichment telemetry to `manifest.metadata.enrichment` entries `{ source: 'cache' | 'places' | 'fallback' | 'override', entityId, placeId?, timestamp }`.
  - Emit structured logs via `packages/core-domain/audit` so Stories 3.2/3.4 can surface cache miss/override counts.
- Deterministic seeding alignment:
  - Ensure enrichment pipeline reads seed context from `packages/core-domain/seeding/` (Story 1.2) so repeated runs reuse the same merchant/employer IDs.
  - For offline mode tests, set env `GOOGLE_PLACES_MODE=offline` to bypass live calls and force fallback usage.

## Cross-epic dependencies
- Epic 1 – Story 1.2 provides deterministic seeding and manifest wiring that enrichment services must integrate with.

### Testing
- Mock Google Places API responses in unit tests to validate cache behaviour and encryption.
- Run end-to-end tests toggling offline mode to confirm deterministic outputs using fallback data.

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
