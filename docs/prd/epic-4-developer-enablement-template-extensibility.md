# Epic 4 Developer Enablement & Template Extensibility
Equip internal squads and partner teams with the tooling, documentation, and guardrails needed to extend DocuGen templates safely. Delivering this epic ensures new institutions or artefact variations can be onboarded without destabilising deterministic runs or compliance guarantees.

## Story 4.1 Ship Template Authoring Toolkit
As a platform enablement engineer,
I want a CLI workflow that scaffolds and validates custom template packages,
so that teams can extend DocuGen without breaking bundle alignment or manifests.

### Acceptance Criteria
1: `docugen templates scaffold` generates a versioned package with renderer stubs, manifest metadata, and test harness aligned to Turborepo conventions.
2: Scaffolded packages register with shared-type exports, ensuring CLI/API surfaces detect new artefacts without manual wiring.
3: Integration tests exercise the scaffold command end-to-end, including preview rendering and deterministic checksum verification.
4: Developer docs walk through extending NAB templates and highlight guardrails for future institutions.

## Story 4.2 Publish Developer Workspace and Sample Bundles
As a partner integration engineer,
I want curated sample seeds, fixtures, and automation scripts,
so that I can prototype DocuGen extensions quickly and understand expected outputs.

### Acceptance Criteria
1: Versioned fixture bundles with aligned manifests live under `tests/fixtures/templates` and cover multi-artefact runs.
2: `pnpm workspace:demo` spins up the Compose stack, loads fixtures, and renders bundles for inspection within ten minutes.
3: Documentation explains how to swap fixtures, update manifests, and replay runs via CLI and admin UI.
4: Telemetry tags fixture-driven runs to separate them from production-like workloads for observability dashboards.

## Story 4.3 Enable Template Preview and Validation Mode
As a docops specialist,
I want a sandboxed preview mode for templates with reconciliation checkpoints,
so that I can validate layout changes and data alignment before promoting them to production use.

### Acceptance Criteria
1: `docugen templates preview` executes a dry-run render with deterministic seeds, producing PDFs and diff artefacts without touching production manifests.
2: Preflight validation checks ensure new templates respect reconciliation, identifier reuse, and compliance flagging rules.
3: Admin UI surfaces preview artefacts, diff reports, and validation status for stakeholder review.
4: Monitoring emits preview run metrics (duration, diff outcomes, rule violations) and retains them for 30 days.

## Story 4.4 Enable Partner Onboarding and API Access
As a partner success manager,
I want a streamlined onboarding flow for API consumers with sample assets and governance guardrails,
so that external teams can integrate DocuGen quickly while respecting compliance constraints.

### Acceptance Criteria
1: Partner onboarding checklist covers account creation, API credential issuance, and environment access approvals.
2: Starter kits (Postman collection, sample configs, walkthrough video) demonstrate end-to-end API usage.
3: Rate limits, quota policies, and support escalation paths are documented and surfaced to partners.
4: Compliance review ensures onboarding materials and credential workflows meet audit requirements.
