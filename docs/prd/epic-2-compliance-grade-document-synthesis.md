# Epic 2 Compliance-Grade Document Synthesis
Layer responsible lending intelligence, merchant enrichment, and fidelity validation atop the foundation, ensuring every artefact aligns across totals, dates, and external references for regulator-grade confidence.

## Story 2.1 Implement Responsible Lending Alignment Engine
As a credit policy specialist,
I want generation rules that enforce income stability, deposit alignment, and NAB formatting constraints,
so that produced bundles satisfy internal responsible lending reviews.

### Acceptance Criteria
1: Rule engine cross-checks payslip earnings against statement deposits and proof-of-balance totals, raising blocking errors on mismatches.
2: Income smoothing, employment tenure, and minimum balance rules map to codified configuration toggles with defaults from the brief.
3: Compliance diagnostics attach to manifests with references to violated rule ids for audit traceability.
4: Regression suite covers representative edge cases (contractor income, supplemental allowances, irregular deposits).

## Story 2.2 Integrate Merchant and Employer Enrichment
As a document reviewer,
I want merchant and employer details enriched via Google Places with deterministic caching,
so that artefacts display credible Australian entities without external flakiness.

### Acceptance Criteria
1: Google Places integration retrieves legal name, suburb, and ABN-like metadata, storing responses in encrypted cache with configurable TTL.
2: Offline fallback dataset covers top 100 Australian merchant categories relevant to lending use cases.
3: Cache miss, fallback use, and enrichment overrides are logged in manifests for audit replay.
4: Integration tests simulate quota exhaustion and offline modes to confirm deterministic outputs.

## Story 2.3 Enforce Pixel Fidelity and Alignment Validation
As a QA engineer,
I want automated pixel diff and reconciliation checks during generation,
so that inaccuracies are caught before bundles reach compliance reviewers.

### Acceptance Criteria
1: Automated visual diff compares generated PDFs against golden fixtures with ≥95% similarity threshold and stored diff artefacts on failure.
2: Reconciliation step validates totals, dates, and identifiers across all artefacts prior to packaging, halting runs on inconsistencies.
3: CLI surfaces pass/fail summary with links to diff reports and reconciliation logs.
4: CI pipeline publishes fidelity metrics to monitoring dashboards for historical tracking.
