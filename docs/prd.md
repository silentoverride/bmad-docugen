# Financial Document Generator Product Requirements Document (PRD)

## Goals and Background Context

### Goals
- Deliver a unified generator that produces NAB-fidelity bank statements, payslips, and proofs of balance from shared structured inputs.
- Cut manual underwriting rework caused by mismatched artefacts by enabling tightly aligned, compliance-ready document bundles.
- Provide lending and fintech teams with deterministic, self-serve configuration, API, and CLI surfaces for rapid document package creation.
- Guarantee operators can assemble lender-ready document packs in under five minutes while preserving auditability and traceability.
- Ensure generated artefacts meet internal compliance and audit spot checks with ≥95% fidelity to NAB references.

### Background Context
Loan-origination teams currently juggle applicant-uploaded documents that vary in format, accuracy, and regulatory compliance. The resulting rework slows approvals and erodes trust. The Financial Document Generator addresses this by synchronising key artefacts—statements, payslips, and proofs of balance—around common datasets, Australian responsible lending rules, and verified merchant information.

By pairing a TypeScript configuration layer with Puppeteer-driven rendering, the solution keeps document templates pixel-perfect, ensures deposits and balances align across artefacts, and gives both internal lenders and fintech partners a reproducible way to create testing and training materials without exposing customer data.

### Change Log
| Date       | Version | Description                       | Author |
|------------|---------|-----------------------------------|--------|
| 2025-02-14 | 0.1     | Initial PRD draft kickoff (Goals) | PM     |
| 2025-09-25 | 0.2     | Populated requirements, planning  | PM     |

## Requirements

### Functional
1. FR1: Accept structured applicant and account inputs to generate NAB-format bank statements, payslips, and proofs of balance as a single, versioned bundle.
2. FR2: Reconcile earnings, deposits, and balances across all artefacts so payslips, statements, and proofs of balance share identifiers, totals, and timing.
3. FR3: Enrich merchant and employer entities through Google Places lookups using deterministic caching, sandbox fallbacks, and documented cache invalidation to preserve reproducibility.
4. FR4: Provide CLI, API, and optional guided UI control surfaces that validate responsible-lending rules, emit structured diagnostics, and block bundles that violate compliance constraints.
5. FR5: Let operators configure date ranges, account selections, and rendering options per document while preserving NAB template fidelity and guardrails.
6. FR6: Persist cryptographically signed run manifests (inputs, configuration, output hashes) to access-controlled storage for audit traceability.
7. FR7: Package generated artefacts as a signed archive with checksums, delivery metadata, and secure download flow that supports sub-five-minute operator completion times.
8. FR8: Enforce NAB-specific template guardrails, flag configuration attempts targeting unsupported institutions, and provide extension guidelines for future banks without impacting current fidelity.

### Non-Functional
1. NFR1: Rendered PDFs must achieve ≥95% pixel fidelity compared to reference NAB documents verified via automated diff tooling.
2. NFR2: Complete bundle generation within ≤30 seconds for up to three concurrent runs on the staging reference environment, with monitoring and alerting when throughput or queue depth threatens the SLA.
3. NFR3: Repeat runs with identical seeds must produce hash-identical outputs and manifests, including deterministic handling of cached or fallback merchant data for offline and CI scenarios.
4. NFR4: Generation workflows must emit structured audit logs covering inputs, rule evaluations, transformations, and output locations, stored per compliance retention policies with access controls and redaction of sensitive fields.
5. NFR5: Integration secrets must support automated rotation, per-tenant isolation, and alerting ahead of expiry, with no plaintext exposure in logs and no redeploy required for rotation.
6. NFR6: Operational telemetry must capture performance, compliance validation outcomes, and packaging success rates, surfacing dashboards for lenders and engineering teams to monitor bundle health.

## User Interface Design Goals

### Overall UX Vision
Empower internal operators to trigger deterministic document bundles via CLI workflows and internal admin forms that surface run readiness, validation errors, and rendered artefact previews without requiring deep technical knowledge.

### Key Interaction Paradigms
- Guided CLI prompts with configuration validation and inline remediation hints.
- Admin web view surfacing latest bundle history, manifest metadata, and PDF previews for compliance review.
- Read-only dashboards for lending stakeholders summarising bundle status, SLA adherence, and audit flags.

### Core Screens and Views
- CLI run summary output that highlights validation outcomes, document links, and packaging status.
- Document bundle detail page with PDF preview carousel and reconciled totals cross-check.
- Audit trail explorer showing manifests, logs, and hash verification for completed runs.

### Accessibility: None
CLI-first workflows and internal admin tools inherit standard accessibility from shared component library; no external WCAG commitments required at this stage.

### Branding
- Generated PDFs replicate NAB artefact styling and typography to maintain lender familiarity.
- Internal admin UI reuses existing Codex CLI palette with NAB accents on preview elements for context.

### Target Device and Platforms: Web Responsive
Admin review tooling remains web responsive for desktop-first usage while enabling tablet access during audits.

## Technical Assumptions

### Repository Structure: Monorepo
Maintain a single repository hosting the TypeScript generation engine, configuration schemas, rendering templates, and infrastructure-as-code so cross-cutting updates stay synchronised and reproducible.

### Service Architecture
Adopt a modular monolith comprised of orchestrator services, data preparation modules, and rendering workers within one deployable Node.js application, exposing CLI and API entry points while enabling future extraction of workloads if scale demands.

### Testing Requirements
Pursue a full testing pyramid: exhaustive unit tests for calculators and formatters, integration tests covering end-to-end bundle generation with golden fixtures, and smoke-level e2e checks validating packaging and delivery flows in staging.

### Additional Technical Assumptions and Requests
- Target Node.js 20 LTS with TypeScript strict mode to align with Puppeteer compatibility and deterministic async handling.
- Manage render jobs via a worker queue (e.g., BullMQ) to throttle concurrency and maintain ≤30 second SLA under load.
- Persist manifests, logs, and packaged bundles in AWS S3 with SSE-KMS encryption and lifecycle policies mapped to compliance retention windows.
- Provide configuration-driven merchant enrichment settings including cache TTLs, offline fallbacks, and manual override hooks for QA scenarios.

## Epic List
- Epic 1: Generator Foundation & Input Harmonisation – Stand up deterministic data pipelines, configuration surfaces, and baseline rendering capability.
- Epic 2: Compliance-Grade Document Synthesis – Implement responsible lending alignment, merchant enrichment, and fidelity validation across artefacts.
- Epic 3: Operational Delivery & Observability – Package outputs, enforce compliance gates, and deliver audit-ready telemetry for stakeholders.

## Epic 1 Generator Foundation & Input Harmonisation
Establish the shared data contracts, deterministic orchestration, and baseline rendering assets that enable cross-document alignment from the outset. Completing this epic delivers a functioning CLI that ingests structured applicant data, normalises it, and renders first-pass artefacts with manifests.

### Story 1.1 Establish Shared Data Schema and Seed Config
As a lending operations analyst,
I want a canonical applicant and account schema with seed configuration samples,
so that every generation run starts from consistent, auditable input structures.

#### Acceptance Criteria
1: Schema covers applicant identity, employment, income cadence, accounts, and document selection with TypeScript typings and JSON Schema exports.
2: Seed data set demonstrates multi-income scenarios and configurable statement ranges aligned with brief goals.
3: Config validation rejects missing or ill-formed sections with actionable error messages surfaced through CLI.
4: Documentation explains how to extend the schema for future institutions without breaking deterministic behaviour.

### Story 1.2 Build Deterministic CLI Orchestrator
As a platform engineer,
I want a CLI command that ingests config, normalises data, and emits a signed run manifest,
so that operators can reproduce bundle generation and trace every input parameter.

#### Acceptance Criteria
1: CLI supports dry-run validation and generation modes with consistent exit codes.
2: Manifest records hash of inputs, timestamp, operator id, and selected artefacts with SHA-256 signatures.
3: Deterministic seeding ensures repeated runs with identical inputs produce identical manifests and intermediate datasets.
4: CI job executes CLI against seed data on every merge, storing manifest artefacts as build outputs.

### Story 1.3 Render Baseline NAB Artefacts with Placeholders
As a compliance reviewer,
I want first-pass NAB-style PDFs generated from sample data,
so that we can visually confirm template fidelity before enforcing responsible lending logic.

#### Acceptance Criteria
1: Puppeteer renders NAB transaction listing, proof of balance, and payslip templates using shared data model placeholders.
2: Rendered PDFs pass automated layout checks (e.g., CSS selectors present, page counts correct) in CI.
3: Output bundle stores PDFs alongside manifest metadata in staging S3 bucket with deterministic filenames.
4: QA checksum comparison verifies repeated runs produce identical binary output when inputs are unchanged.

## Epic 2 Compliance-Grade Document Synthesis
Layer responsible lending intelligence, merchant enrichment, and fidelity validation atop the foundation, ensuring every artefact aligns across totals, dates, and external references for regulator-grade confidence.

### Story 2.1 Implement Responsible Lending Alignment Engine
As a credit policy specialist,
I want generation rules that enforce income stability, deposit alignment, and NAB formatting constraints,
so that produced bundles satisfy internal responsible lending reviews.

#### Acceptance Criteria
1: Rule engine cross-checks payslip earnings against statement deposits and proof-of-balance totals, raising blocking errors on mismatches.
2: Income smoothing, employment tenure, and minimum balance rules map to codified configuration toggles with defaults from the brief.
3: Compliance diagnostics attach to manifests with references to violated rule ids for audit traceability.
4: Regression suite covers representative edge cases (contractor income, supplemental allowances, irregular deposits).

### Story 2.2 Integrate Merchant and Employer Enrichment
As a document reviewer,
I want merchant and employer details enriched via Google Places with deterministic caching,
so that artefacts display credible Australian entities without external flakiness.

#### Acceptance Criteria
1: Google Places integration retrieves legal name, suburb, and ABN-like metadata, storing responses in encrypted cache with configurable TTL.
2: Offline fallback dataset covers top 100 Australian merchant categories relevant to lending use cases.
3: Cache miss, fallback use, and enrichment overrides are logged in manifests for audit replay.
4: Integration tests simulate quota exhaustion and offline modes to confirm deterministic outputs.

### Story 2.3 Enforce Pixel Fidelity and Alignment Validation
As a QA engineer,
I want automated pixel diff and reconciliation checks during generation,
so that inaccuracies are caught before bundles reach compliance reviewers.

#### Acceptance Criteria
1: Automated visual diff compares generated PDFs against golden fixtures with ≥95% similarity threshold and stored diff artefacts on failure.
2: Reconciliation step validates totals, dates, and identifiers across all artefacts prior to packaging, halting runs on inconsistencies.
3: CLI surfaces pass/fail summary with links to diff reports and reconciliation logs.
4: CI pipeline publishes fidelity metrics to monitoring dashboards for historical tracking.

## Epic 3 Operational Delivery & Observability
Deliver the controls, packaging, and monitoring required for production readiness, enabling rapid operator workflows, secure artefact distribution, and actionable observability for engineering and compliance teams.

### Story 3.1 Harden Compliance Gating and Operator UX
As a lending operations supervisor,
I want compliance gates and clear operator messaging in the generation workflow,
so that bundles failing policy checks never progress and operators know how to resolve issues quickly.

#### Acceptance Criteria
1: CLI and admin UI block progression past validation failures, presenting remediation guidance mapped to rule ids.
2: Role-based access ensures only authorised operators can approve overrides with justification notes logged in manifests.
3: Success path completes within the five-minute operator target for seed scenarios, measured via telemetry.
4: Training mode provides sample runs with annotated feedback for onboarding new operators.

### Story 3.2 Persist Audit Logs and Secure Storage
As a compliance auditor,
I want immutable logs, manifests, and bundle artefacts stored securely,
so that audits can reconstruct any run with full provenance.

#### Acceptance Criteria
1: Structured logs emit to AWS CloudWatch (or equivalent) with trace ids linking CLI actions, rule evaluations, and packaging events.
2: Manifests and bundles persist to S3 with KMS encryption, retention policies, and integrity hashes checked on retrieval.
3: Access logs capture every download or manifest view with operator identity and timestamp.
4: Disaster recovery procedure documents restoration steps and validates quarterly via tabletop exercise.

### Story 3.3 Deliver Signed Bundle Packaging and Distribution
As a fintech integrator,
I want signed archives and controlled delivery endpoints,
so that downstream systems can trust and automate bundle ingestion.

#### Acceptance Criteria
1: Bundles compress into signed archives containing PDFs, manifest, reconciliation report, and checksums.
2: Delivery endpoint supports expiring pre-signed URLs and optional webhook notification with metadata payload.
3: Integrity verification script allows recipients to confirm signatures and checksums locally.
4: Packaging step maintains ≤30 second SLA when invoked sequentially with two other runs.

### Story 3.4 Surface Observability Dashboards and Alerts
As a site reliability engineer,
I want dashboards and threshold-based alerts for generation health,
so that we detect and resolve SLA or compliance regressions before they impact stakeholders.

#### Acceptance Criteria
1: Grafana (or equivalent) dashboard visualises throughput, failure rates, rule violations, and pixel diff metrics in near real-time.
2: Alerting policies trigger notifications when generation duration, failure rate, or fidelity metrics breach agreed thresholds.
3: Dashboard links into run manifests for deep-dive investigation in a single click.
4: Runbook documents remediation steps for top five failure modes and is tested via quarterly drills.

## Checklist Results Report
Execution mode: Comprehensive desk review (manual). Project type detected as greenfield with UI considerations.

### Category Statuses
| Category                                | Status          | Notes |
| --------------------------------------- | --------------- | ----- |
| Project Setup & Initialization          | Complete        | Epic 1 covers scaffolding, CLI foundation, and documentation deliverables. |
| Infrastructure & Deployment             | Complete        | Technical assumptions define queueing, storage, and manifest management up front. |
| External Dependencies & Integrations    | Complete        | FR set and Epic 2 stories address Google Places, caching, and SLA handling. |
| UI/UX Considerations                    | Complete        | UI goals describe operator workflows, previews, and dashboards. |
| User/Agent Responsibility               | Complete        | Stories specify operator, reviewer, and engineer personas with acceptance criteria. |
| Feature Sequencing & Dependencies       | Complete        | Epics and stories progress logically from foundation to compliance to operations. |
| Risk Management (Brownfield Only)       | N/A (Greenfield) | Not applicable. |
| MVP Scope Alignment                     | Complete        | MVP boundaries and success metrics reiterated in FR/NFR sets and epics. |
| Documentation & Handoff                 | Complete        | Next-step prompts and manifest documentation expectations captured. |
| Post-MVP Considerations                 | Needs Follow-up | Future enhancement themes noted; backlog candidates catalogued below. |

### Critical Deficiencies
None identified.

### Recommendations
- Maintain the post-MVP backlog list under "Post-MVP Considerations" and groom it alongside roadmap reviews.

### Final Decision
**APPROVED** – Requirements and planning artefacts are ready for implementation with catalogued post-MVP backlog items for future prioritisation.

## Next Steps

### UX Expert Prompt
Leverage this PRD to draft a front-end/admin interaction spec that outlines CLI ergonomics, operator review workflows, and preview tooling required to support compliance-ready bundle approvals.

### Architect Prompt
Using the constraints and epics in this PRD, produce an architecture plan covering module boundaries, queueing strategy, storage topology, and deployment pipeline that ensures deterministic generation, compliance controls, and observability.

## Post-MVP Backlog

| Backlog Item | Priority | Rationale | Key Dependencies | Suggested Release Window |
|--------------|----------|-----------|-------------------|--------------------------|
| Multi-bank expansion (additional Australian institutions with reusable templates and rule packs) | P1 | Unlocks the primary growth lever once NAB fidelity is proven; leverages existing deterministic engine with moderate incremental effort. | Completion of Epic 2 compliance tooling; template authoring guide. | Release 1.1 (immediately after MVP hardening) |
| Partner SDK for fintech integrators (embed generation flows) | P2 | Drives adoption and ecosystem stickiness; reuses manifests and packaging work with focused developer experience polish. | Epic 3 packaging APIs; documentation baseline. | Release 1.2 |
| Operator UI enhancements (bulk scheduling, inline diff previews, workflow notifications) | P2 | Reduces operational toil and accelerates compliance review, but depends on stable telemetry and bundle APIs. | Observability dashboards from Epic 3; UX spec. | Release 1.2 |
| Real-time bank API ingestion (live data pulls) | P3 | High strategic value but requires additional security, consent, and rate-limit work; should follow stability and audit learnings. | External API contracts; security/legal review; secrets rotation maturity. | Release 1.3 |
| Analytics & anomaly detection module (borrower insights, compliance trends) | P3 | Supports long-term differentiation, built atop telemetry and historical manifests once sufficient data volume exists. | Observability data warehouse; retention policies. | Release 1.3+ |

Prioritisation aligns with current epics: Release 1.1 extends compliance wins into broader bank coverage, Release 1.2 emphasises partner and operator experience once packaging stabilises, and Release 1.3 tackles data- and integration-heavy initiatives after telemetry matures.
