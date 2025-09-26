# Story 5.1 Versioned Compliance Rule Library

## Status
Draft (Multi-sprint)

## Story
**As a** compliance architect,
**I want** a version-controlled rules engine with documented change management,
**so that** regulatory updates propagate safely across DocuGen surfaces.

## Acceptance Criteria
1. Compliance rules live in a dedicated package with semantic versioning, changelog, and dependency graph annotations.
2. CLI command `docugen compliance diff` compares rule versions, highlighting breaking and additive changes with linked documentation.
3. Regression suite covers baseline scenarios (income variance, merchant blacklist, template guardrails) and runs in CI on rule updates.
4. Rule metadata records effective dates and approval signatures for audit review.

## Tasks / Subtasks
- [ ] Create `packages/compliance-rules` with semantic versioning and changelog automation (AC: 1)
- [ ] Implement `docugen compliance diff` command surfacing rule deltas with doc links (AC: 2)
  - [ ] Integrate command output with admin UI or logs for visibility (AC: 2)
- [ ] Expand regression suite covering baseline scenarios and ensure CI enforcement (AC: 3)
- [ ] Capture rule metadata (effective date, approver) and persist alongside manifests (AC: 4)
  - [ ] Update compliance governance docs (`docs/prd/epic-5-compliance-automation-continuous-assurance.md`) with metadata process (AC: 4)

## Delivery plan
- Sprint 1: establish the dedicated compliance rule package with semantic versioning, changelog automation, and metadata scaffolding.
- Sprint 2: deliver the `docugen compliance diff` command and surface deltas through CLI logs and optional admin UI touchpoints.
- Sprint 3: harden regression coverage and CI gates to block rule changes lacking baseline scenario validation.

## Dev Notes
- Rule evaluation currently lives in the validation engine described in `docs/prd/epic-2-compliance-grade-document-synthesis.md`; refactor carefully to avoid regressions.
- Package organisation guidance exists in `docs/architecture/unified-project-structure.md`; follow Turborepo workspace conventions.
- Audit and manifest requirements are covered in `docs/architecture/components.md#manifest-service` and `docs/prd/epic-3-operational-delivery-observability.md` (Story 3.2).
- Ensure changelog process aligns with governance expectations in `docs/brief.md` and `docs/prd/requirements.md` (compliance sections).

## Cross-epic dependencies
- Epic 2 – Story 2.1 supplies the responsible lending rules being extracted into the dedicated library.
- Epic 3 – Story 3.2 provides manifest persistence and audit logging that store rule metadata and changelog outputs.

### Testing
- Add unit coverage for rule evaluation scenarios using Vitest as outlined in `docs/architecture/testing-strategy.md`.
- Integrate diff command tests into CLI integration suite (`pnpm test:integration`).
- Ensure CI gating runs regression suite automatically when rule package changes.

## Change Log
| Date       | Version | Description            | Author |
|------------|---------|------------------------|--------|
| 2025-09-27 | 0.1     | Initial story draft    | PO     |
| 2025-09-27 | 0.2     | Promoted to Approved; documented metadata follow-through | PO |

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
