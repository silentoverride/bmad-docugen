# Story 1.1 Establish Shared Data Schema and Seed Config

## Status
Approved

## Story
**As a** lending operations analyst,
**I want** a canonical applicant and account schema with seed configuration samples,
**so that** every generation run starts from consistent, auditable input structures.

## Acceptance Criteria
1. Schema covers applicant identity, employment, income cadence, accounts, and document selection with TypeScript typings and JSON Schema exports.
2. Seed data set demonstrates multi-income scenarios and configurable statement ranges aligned with brief goals.
3. Config validation rejects missing or ill-formed sections with actionable error messages surfaced through CLI.
4. Documentation explains how to extend the schema for future institutions without breaking deterministic behaviour.

## Tasks / Subtasks
- [ ] Model applicant, employment, and account structures with strict TypeScript definitions and JSON Schema exports (AC: 1)
- [ ] Produce seed configuration samples covering multi-income scenarios and statement range toggles (AC: 2)
- [ ] Implement CLI validation layer with descriptive error responses for malformed configs (AC: 3)
- [ ] Document schema extension guidelines for additional institutions (AC: 4)

## Dev Notes
- Source of truth lives in `packages/shared-types` (per `docs/architecture/coding-standards.md` and `docs/architecture/high-level-architecture.md`). Define Zod schemas that emit both TypeScript types and JSON Schema for the core objects referenced in `docs/architecture/data-models.md`:
  - `ApplicantProfile` (`id`, `fullName`, `dateOfBirth`, `primaryEmployerId`, `addresses`)
  - `FinancialAccount` (`institution`, `accountNumberMasked`, `currency`, `applicantId`)
  - `AccountSnapshot` and `TransactionRecord` (period ranges, opening/closing balances, merchant references)
  - Income structures (`PayslipRecord` with gross/net/tax/super fields, `EmployerProfile` with `legalName` and `abn`)
  - Document selection toggles for `DocumentArtefact.type` (`bank_statement`, `payslip`, `proof_of_balance`)
- Co-locate schema definitions under `packages/shared-types/src/schema/` and add a generator (e.g., `packages/shared-types/scripts/generate-json-schema.ts`) that writes JSON Schema artifacts to `packages/shared-types/schema/*.json` so API, CLI, and UI share identical validation assets. Wire the generator into `package.json` (e.g., `pnpm --filter shared-types run build:schema`) and ensure Story 1.2 consumes the emitted JSON Schema bundle.
- Place seed fixtures in `tests/fixtures/seeds/` (see `default_SEED_FIXTURE` in `docs/architecture/development-workflow.md`) and provide at least:
  - Base salaried applicant
  - Supplemental allowance / bonus stream
  - Contractor or gig worker cadence
  Each seed should reference the shared schema IDs, selected accounts, and configurable date ranges (e.g., `range.months = 3`) so toggles in FR5 are demonstrated.
- Extend the DocuGen CLI in `apps/cli` to expose a validation command (`docugen config validate <path-to-seed.json>`). Command must load the shared Zod schemas / JSON Schema artifacts, surface field-level errors, and exit with non-zero status on failure. Coordinate with Story 1.2 so the orchestration flow consumes these validators rather than duplicating rules.
- Schema packages should publish TypeScript types for downstream imports via `packages/core-domain/configuration` and `packages/shared-types/index.ts` (align folder names with `docs/architecture/unified-project-structure.md`). Update docs under `docs/architecture` with extension guidance (AC4) so future institutions know which modules to extend and how to preserve deterministic hash order.

### Testing
- Add unit tests for schema validators and JSON Schema generation using Vitest per `docs/architecture/testing-strategy.md`.
- Include integration tests that load seed configs through the CLI validation path to confirm error messaging coverage.

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
