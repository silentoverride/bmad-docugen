# Story 1.3 Render Baseline NAB Artefacts with Placeholders

## Status
Approved

## Story
**As a** compliance reviewer,
**I want** first-pass NAB-style PDFs generated from sample data,
**so that** we can visually confirm template fidelity before enforcing responsible lending logic.

## Acceptance Criteria
1. Puppeteer renders NAB transaction listing, proof of balance, and payslip templates using shared data model placeholders.
2. Rendered PDFs pass automated layout checks (e.g., CSS selectors present, page counts correct) in CI.
3. Output bundle stores PDFs alongside manifest metadata in staging S3 bucket with deterministic filenames.
4. QA checksum comparison verifies repeated runs produce identical binary output when inputs are unchanged.

## Tasks / Subtasks
- [ ] Implement placeholder NAB templates and rendering pipeline via Puppeteer (AC: 1)
- [ ] Add automated layout assertions validating selectors, page counts, and key elements (AC: 2)
- [ ] Persist rendered PDFs and manifests to staging storage with deterministic naming (AC: 3)
- [ ] Introduce checksum comparison guard to detect rendering drift across runs (AC: 4)

## Dev Notes
- Rendering entry points live in `packages/renderers/nab/src/index.ts`, exporting `renderTransactionListing`, `renderProofOfBalance`, and `renderPayslip`. Templates sit under `packages/renderers/nab/templates/*.hbs` and consume shared schema DTOs from `packages/shared-types` (Story 1.1).
- Puppeteer worker setup reuses `apps/worker/src/jobs/render-nab.ts`; register a BullMQ job `render:nab` so Story 1.5 can queue work immediately.
- Deterministic storage: upload PDFs to MinIO under `artefacts/{bundleRunId}/{documentType}.pdf` where `documentType` ∈ `transaction_listing`, `proof_of_balance`, `payslip`. Update manifest artefact entries accordingly (alignment with Story 1.2).
- Layout assertions: add Playwright-based checks in `packages/renderers/nab/tests/layout/` verifying CSS selectors, page counts, and key text anchors; wire via `pnpm --filter renderers run test:layout` in CI.
- Checksum guard: expose a CLI command `docugen checksum --path artefacts/{bundleRunId}` (implemented in `apps/cli/src/commands/checksum.ts`) that hashes PDFs and compares against stored digests to detect drift. CI should invoke `pnpm docugen checksum --path artefacts/{bundleRunId}` after each render to assert identical output.
- Reference `docs/source-files/NAB_Styling_Guide.md` for font, spacing, and branding requirements; ensure documentation updates accompany template edits for future institutions.

## Cross-epic dependencies
- Epic 3 – Stories 3.2 and 3.3 establish the secure storage and packaging flows used for rendered PDF artefacts.

### Testing
- Add integration tests that render sample seeds and verify layout assertions are triggered on failure.
- Include checksum-based regression checks in CI to detect binary drift.

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
