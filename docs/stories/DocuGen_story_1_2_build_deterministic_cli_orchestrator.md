# Story 1.2 Build Deterministic CLI Orchestrator

## Status
Approved

## Story
**As a** platform engineer,
**I want** a CLI command that ingests config, normalises data, and emits a signed run manifest,
**so that** operators can reproduce bundle generation and trace every input parameter.

## Acceptance Criteria
1. CLI supports dry-run validation and generation modes with consistent exit codes.
2. Manifest records hash of inputs, timestamp, operator id, and selected artefacts with SHA-256 signatures.
3. Deterministic seeding ensures repeated runs with identical inputs produce identical manifests and intermediate datasets.
4. CI job executes CLI against seed data on every merge, storing manifest artefacts as build outputs.

## Tasks / Subtasks
- [ ] Implement CLI entry point with validation and generation modes plus consistent exit codes (AC: 1)
- [ ] Persist signed manifests capturing operator metadata, artefact selection, and SHA-256 hashes (AC: 2)
- [ ] Integrate deterministic seed initialisation to guarantee repeatable outputs (AC: 3)
- [ ] Add CI workflow executing the CLI against reference seeds and archiving manifests (AC: 4)

## Dev Notes
- CLI entry point lives in `apps/cli/src/commands/run.ts`. Provide two subcommands:
  - `docugen run --mode=validate --config <path>` – loads Story 1.1 validation assets and prints field-level errors, exiting `2` on failure.
  - `docugen run --mode=generate --config <path>` – executes orchestration, exiting `0` on success (`1` on runtime error).
- Consume JSON Schema + Zod definitions produced in Story 1.1 from `packages/shared-types/schema/configuration.json`; avoid redefining validation logic in the CLI.
- Deterministic seeding setup:
  - Shared helpers: `packages/core-domain/seeding/` (e.g., `createSeedContext.ts`).
  - Supported fixtures: `tests/fixtures/seeds/*.json` (use `default.json` in documentation and CI).
  - Canonicalise seed JSON (sorted keys) before hashing to keep manifests identical across environments.
- Manifest generation requirements:
  - Include `hash` (SHA-256 input hash), `createdAt` (UTC ISO string), `operatorId` (Keycloak subject), `artefacts` array (ID, type, storage key), `signingKeyId`, and `signature`.
  - Persist manifests to MinIO at `manifests/{bundleRunId}.json` via helpers in `packages/core-domain/manifest/manifest.service.ts`.
  - Use Vault transit key `docugen-manifest` as provisioned in `infra/compose/scripts/bootstrap-vault.sh`; fail fast if Vault unavailable and log fallback behaviour per Epic 3.
- CI enforcement in `.github/workflows/ci.yml`:
  - Run `pnpm --filter cli run lint` and `pnpm --filter cli run test`.
  - Execute `pnpm docugen run --mode=generate --config tests/fixtures/seeds/default.json` twice and diff manifests to prove determinism.
  - Upload manifest files + CLI logs to `artifacts/manifests/` for review.
- Coordinate with Epic 3 for manifest retention/access logging and notify packaging (Story 3.3) that manifests are served from `manifests/{bundleRunId}.json`.

## Cross-epic dependencies
- Epic 3 – Stories 3.2 and 3.3 define manifest storage and packaging endpoints that the CLI orchestrator must publish to.

### Testing
- Create integration tests covering dry-run and generation modes with snapshot verification of manifests.
- Add regression tests ensuring identical seeds produce identical manifest hashes across runs.

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
