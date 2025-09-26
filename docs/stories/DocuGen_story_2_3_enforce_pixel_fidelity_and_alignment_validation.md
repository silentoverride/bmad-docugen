# Story 2.3 Enforce Pixel Fidelity and Alignment Validation

## Status
Approved

## Story
**As a** QA engineer,
**I want** automated pixel diff and reconciliation checks during generation,
**so that** inaccuracies are caught before bundles reach compliance reviewers.

## Acceptance Criteria
1. Automated visual diff compares generated PDFs against golden fixtures with ≥95% similarity threshold and stored diff artefacts on failure.
2. Reconciliation step validates totals, dates, and identifiers across all artefacts prior to packaging, halting runs on inconsistencies.
3. CLI surfaces pass/fail summary with links to diff reports and reconciliation logs.
4. CI pipeline publishes fidelity metrics to monitoring dashboards for historical tracking.

## Tasks / Subtasks
- [ ] Implement pixel diff tooling that compares PDFs to golden fixtures and stores diff artefacts (AC: 1)
- [ ] Build reconciliation service validating totals, dates, and identifiers before packaging (AC: 2)
- [ ] Update CLI output to link to diff reports and reconciliation logs (AC: 3)
- [ ] Publish fidelity metrics from CI to observability dashboards (AC: 4)

## Dev Notes
- Pixel diff tooling:
  - Implement `packages/qa/pixel-diff/index.ts` exposing `comparePdf(renderedPath, goldenPath, threshold)` using `pixelmatch` + Puppeteer screenshots.
  - Golden fixtures reside in `tests/fixtures/golden-pdfs/*.pdf`; configure threshold and mask options via `packages/qa/pixel-diff/config.ts` (default similarity ≥95%).
- Reconciliation service:
  - Create `packages/core-domain/reconciliation/run-reconciliation.ts` that aggregates totals across transaction listings, payslips, and proofs of balance (reusing Story 1.1/1.3 schemas).
  - Hook into CLI (Story 1.2) and worker pipeline (Story 1.5) immediately after rendering completes, halting packaging if inconsistencies remain.
- CLI output & manifest annotations:
  - Update `apps/cli/src/commands/run.ts` to emit summary table with columns `Check`, `Status`, `ReportPath`.
  - Append entries to `manifest.metadata.validation` array: `{ type: 'pixel_diff' | 'reconciliation', status: 'pass' | 'fail', severity, reportKey }` where `reportKey` references artefacts stored in MinIO `diff-reports/{bundleRunId}/`.
- Artefact retention:
  - Store diff PNGs and HTML reports in MinIO at `diff-reports/{bundleRunId}/{documentType}` and ensure Story 3.2 retention policies include this prefix.
- Metrics & dashboards:
  - Publish Prometheus metrics via `packages/observability/validation-metrics.ts`: `docugen_pixel_diff_failures_total`, `docugen_reconciliation_failures_total`, `docugen_pixel_diff_runtime_seconds`.
  - Coordinate with Story 3.4 to surface these metrics in Grafana panels and configure alerts on sustained failures.
- Documentation: Extend `docs/source-files/NAB_Fidelity_Checklist.md` with instructions for updating golden fixtures and interpreting diff reports.

## Cross-epic dependencies
- Epic 1 – Stories 1.3 and 1.5 provide rendering outputs and worker orchestration that reconciliation hooks must inspect.
- Epic 3 – Story 3.4 supplies observability dashboards for publishing fidelity metrics and alerts.

### Testing
- Add integration tests generating intentional mismatches to confirm diff and reconciliation failures block packaging.
- Capture screenshot or PDF diff snapshots in CI artifacts for debugging regressions.

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
