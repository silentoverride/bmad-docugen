# Epic 1 Generator Foundation & Input Harmonisation
Establish the shared data contracts, deterministic orchestration, and baseline rendering assets that enable cross-document alignment from the outset. Completing this epic delivers a functioning CLI that ingests structured applicant data, normalises it, and renders first-pass artefacts with manifests.

## Story 1.1 Establish Shared Data Schema and Seed Config
As a lending operations analyst,
I want a canonical applicant and account schema with seed configuration samples,
so that every generation run starts from consistent, auditable input structures.

### Acceptance Criteria
1: Schema covers applicant identity, employment, income cadence, accounts, and document selection with TypeScript typings and JSON Schema exports.
2: Seed data set demonstrates multi-income scenarios and configurable statement ranges aligned with brief goals.
3: Config validation rejects missing or ill-formed sections with actionable error messages surfaced through CLI.
4: Documentation explains how to extend the schema for future institutions without breaking deterministic behaviour.

## Story 1.2 Build Deterministic CLI Orchestrator
As a platform engineer,
I want a CLI command that ingests config, normalises data, and emits a signed run manifest,
so that operators can reproduce bundle generation and trace every input parameter.

### Acceptance Criteria
1: CLI supports dry-run validation and generation modes with consistent exit codes.
2: Manifest records hash of inputs, timestamp, operator id, and selected artefacts with SHA-256 signatures.
3: Deterministic seeding ensures repeated runs with identical inputs produce identical manifests and intermediate datasets.
4: CI job executes CLI against seed data on every merge, storing manifest artefacts as build outputs.

## Story 1.3 Render Baseline NAB Artefacts with Placeholders
As a compliance reviewer,
I want first-pass NAB-style PDFs generated from sample data,
so that we can visually confirm template fidelity before enforcing responsible lending logic.

### Acceptance Criteria
1: Puppeteer renders NAB transaction listing, proof of balance, and payslip templates using shared data model placeholders.
2: Rendered PDFs pass automated layout checks (e.g., CSS selectors present, page counts correct) in CI.
3: Output bundle stores PDFs alongside manifest metadata in staging S3 bucket with deterministic filenames.
4: QA checksum comparison verifies repeated runs produce identical binary output when inputs are unchanged.
