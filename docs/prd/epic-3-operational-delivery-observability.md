# Epic 3 Operational Delivery & Observability
Deliver the controls, packaging, and monitoring required for production readiness, enabling rapid operator workflows, secure artefact distribution, and actionable observability for engineering and compliance teams.

## Story 3.0 Bootstrap Admin UI Shell and Foundation
As a frontend platform engineer,
I want an authenticated admin UI shell with shared navigation and design system wiring,
so that subsequent compliance and operator features can plug into a consistent experience.

### Acceptance Criteria
1: Admin UI bootstraps Next.js (or chosen framework) with authentication guardrails, layout scaffolding, and navigation patterns.
2: Shared design system components (e.g., typography, buttons, tables) align with `docs/user-interface-design-goals.md` and are ready for reuse.
3: Role-based routing restricts access to protected views and displays fallback messaging for unauthorised users.
4: Developer documentation describes UI architecture, component conventions, and contribution workflow.

## Story 3.1 Harden Compliance Gating and Operator UX
As a lending operations supervisor,
I want compliance gates and clear operator messaging in the generation workflow,
so that bundles failing policy checks never progress and operators know how to resolve issues quickly.

### Acceptance Criteria
1: CLI and admin UI block progression past validation failures, presenting remediation guidance mapped to rule ids.
2: Role-based access ensures only authorised operators can approve overrides with justification notes logged in manifests.
3: Success path completes within the five-minute operator target for seed scenarios, measured via telemetry.
4: Training mode provides sample runs with annotated feedback for onboarding new operators.

## Story 3.2 Persist Audit Logs and Secure Storage
As a compliance auditor,
I want immutable logs, manifests, and bundle artefacts stored securely,
so that audits can reconstruct any run with full provenance.

### Acceptance Criteria
1: Structured logs emit to AWS CloudWatch (or equivalent) with trace ids linking CLI actions, rule evaluations, and packaging events.
2: Manifests and bundles persist to S3 with KMS encryption, retention policies, and integrity hashes checked on retrieval.
3: Access logs capture every download or manifest view with operator identity and timestamp.
4: Disaster recovery procedure documents restoration steps and validates quarterly via tabletop exercise.

## Story 3.3 Deliver Signed Bundle Packaging and Distribution
As a fintech integrator,
I want signed archives and controlled delivery endpoints,
so that downstream systems can trust and automate bundle ingestion.

### Acceptance Criteria
1: Bundles compress into signed archives containing PDFs, manifest, reconciliation report, and checksums.
2: Delivery endpoint supports expiring pre-signed URLs and optional webhook notification with metadata payload.
3: Integrity verification script allows recipients to confirm signatures and checksums locally.
4: Packaging step maintains ≤30 second SLA when invoked sequentially with two other runs.

## Story 3.4 Surface Observability Dashboards and Alerts
As a site reliability engineer,
I want dashboards and threshold-based alerts for generation health,
so that we detect and resolve SLA or compliance regressions before they impact stakeholders.

### Acceptance Criteria
1: Grafana (or equivalent) dashboard visualises throughput, failure rates, rule violations, and pixel diff metrics in near real-time.
2: Alerting policies trigger notifications when generation duration, failure rate, or fidelity metrics breach agreed thresholds.
3: Dashboard links into run manifests for deep-dive investigation in a single click.
4: Runbook documents remediation steps for top five failure modes and is tested via quarterly drills.
