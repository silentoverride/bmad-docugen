# Story 4.1 Ship Template Authoring Toolkit

## Status
Draft

## Story
**As a** platform enablement engineer,
**I want** a CLI workflow that scaffolds and validates custom template packages,
**so that** teams can extend DocuGen without breaking bundle alignment or manifests.

## Acceptance Criteria
1. `docugen templates scaffold` generates a versioned package with renderer stubs, manifest metadata, and test harness aligned to Turborepo conventions.
2. Scaffolded packages register with shared-type exports, ensuring CLI/API surfaces detect new artefacts without manual wiring.
3. Integration tests exercise the scaffold command end-to-end, including preview rendering and deterministic checksum verification.
4. Developer docs walk through extending NAB templates and highlight guardrails for future institutions.

## Tasks / Subtasks
- [ ] Design scaffolding blueprint covering renderer stubs, manifest metadata, and test harness (AC: 1)
- [ ] Implement `docugen templates scaffold` command within `apps/cli` (AC: 1)
  - [ ] Wire manifest registration to shared type exports in `packages/shared-types` (AC: 2)
  - [ ] Auto-populate renderer entry points bridging to `packages/renderers` (AC: 2)
- [ ] Create integration workflow that runs scaffold command, preview render, and checksum assertion (AC: 3)
  - [ ] Add CI job executing the workflow using seed data from `tests/fixtures` (AC: 3)
- [ ] Document extension process and guardrails in developer workspace docs (AC: 4)
  - [ ] Update `docs/architecture/development-workflow.md` and `docs/brief.md` with new scaffold workflow (AC: 4)

## Dev Notes
- Monorepo structure with `apps/cli`, `packages/renderers`, and `packages/shared-types` is defined in `docs/architecture/unified-project-structure.md`.
- CLI orchestrator patterns, including manifest generation and deterministic runs, are outlined in `docs/prd/epic-1-generator-foundation-input-harmonisation.md` (Story 1.2) and should be reused.
- Rendering workers rely on Puppeteer per `docs/architecture/components.md#render-worker-pool`; ensure scaffolded templates conform to existing worker contract.
- Update `docs/architecture/development-workflow.md` if new scripts or environment variables are introduced.

## Cross-epic dependencies
- Epic 1 – Story 1.2 exposes manifest orchestration and deterministic seeding logic that the scaffold command must integrate with.

### Testing
- Follow guidance in `docs/architecture/testing-strategy.md` for unit, integration, and snapshot coverage expectations.
- Use `pnpm test:unit` and `pnpm test:integration` for automated verification; add scenario coverage to Playwright harness if preview rendering impacts UI (`pnpm test:e2e`).
- Include checksum fixtures under `tests/fixtures/templates` to validate deterministic outputs.

## Change Log
| Date       | Version | Description            | Author |
|------------|---------|------------------------|--------|
| 2025-09-27 | 0.1     | Initial story draft    | PO     |
| 2025-09-27 | 0.2     | Promoted to Approved; expanded documentation tasks | PO |

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
