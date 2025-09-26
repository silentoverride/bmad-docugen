# Story 2.1 Implement Responsible Lending Alignment Engine

## Status
Approved

## Story
**As a** credit policy specialist,
**I want** generation rules that enforce income stability, deposit alignment, and NAB formatting constraints,
**so that** produced bundles satisfy internal responsible lending reviews.

## Acceptance Criteria
1. Rule engine cross-checks payslip earnings against statement deposits and proof-of-balance totals, raising blocking errors on mismatches.
2. Income smoothing, employment tenure, and minimum balance rules map to codified configuration toggles with defaults from the brief.
3. Compliance diagnostics attach to manifests with references to violated rule ids for audit traceability.
4. Regression suite covers representative edge cases (contractor income, supplemental allowances, irregular deposits).

## Tasks / Subtasks
- [ ] Implement rule engine comparing payslip, statement, and balance totals, surfacing blocking errors (AC: 1)
- [ ] Add configuration toggles for lending rules with sensible defaults and documentation (AC: 2)
- [ ] Emit diagnostics and rule references into manifest metadata (AC: 3)
- [ ] Extend regression suite with edge-case fixtures covering non-traditional income patterns (AC: 4)

## Dev Notes
- Rule engine module: implement core logic in `packages/core-domain/rules/responsible-lending.ts` exposing `evaluateResponsibleLending(bundleRunId, config)`.
- Invocation points:
  - CLI path (Story 1.2): add `runResponsibleLending` step inside `apps/cli/src/commands/run.ts` for `generate` mode before manifest signing.
  - Worker queue (Story 1.5): invoke the same helper from `apps/worker/src/processors/generation.processor.ts` so queued runs share behaviour.
- Configuration structure:
  - Define toggle schema in `packages/shared-types/config/lending.json` (exported via Story 1.1 generator) with keys `incomeSmoothing.active`, `incomeSmoothing.windowDays`, `minimumBalance.threshold`, `employmentTenure.minMonths`, etc.
  - Provide defaults via `packages/core-domain/config/defaults/responsible-lending.ts` and surface overrides through CLI flags (`--lending-config`) and API (Story 1.4) to ensure parity.
- Manifest diagnostics:
  - Append rule outcomes to `manifest.metadata.rules.responsibleLending` array with objects `{ ruleId, severity, status, message, remediationHint }`.
  - Severity codes: `error` (blocks), `warning` (non-blocking). Ensure blocked runs set `status: 'blocked'` and include `details` for audit traceability.
- Regression fixtures & testing:
  - Store fixtures under `tests/fixtures/lending/` (`base-salaried.json`, `contractor-irregular.json`, `supplemental-allowance.json`).
  - Vitest suite located at `packages/core-domain/rules/__tests__/responsible-lending.spec.ts` should load each fixture and assert expected rule outcomes.
  - Integration tests run via `pnpm --filter core-domain run test:lending` to execute rule engine against seeded bundle runs.
- Reference compliance guidance from `docs/prd/epic-2-compliance-grade-document-synthesis.md` for rule descriptions and ensure alignment with schema definitions from Story 1.1.

## Cross-epic dependencies
- Epic 1 – Story 1.1 supplies the shared schema and seed configuration that the alignment engine validates against.

### Testing
- Build unit tests per rule scenario using Vitest with fixtures representing policy edge cases.
- Include integration tests verifying blocking errors halt bundle generation and annotate manifests correctly.

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
