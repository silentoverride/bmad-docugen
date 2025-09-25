# Requirements

## Functional
1. FR1: Accept structured applicant and account inputs to generate NAB-format bank statements, payslips, and proofs of balance as a single, versioned bundle.
2. FR2: Reconcile earnings, deposits, and balances across all artefacts so payslips, statements, and proofs of balance share identifiers, totals, and timing.
3. FR3: Enrich merchant and employer entities through Google Places lookups using deterministic caching, sandbox fallbacks, and documented cache invalidation to preserve reproducibility.
4. FR4: Provide CLI, API, and optional guided UI control surfaces that validate responsible-lending rules, emit structured diagnostics, and block bundles that violate compliance constraints.
5. FR5: Let operators configure date ranges, account selections, and rendering options per document while preserving NAB template fidelity and guardrails.
6. FR6: Persist cryptographically signed run manifests (inputs, configuration, output hashes) to access-controlled storage for audit traceability.
7. FR7: Package generated artefacts as a signed archive with checksums, delivery metadata, and secure download flow that supports sub-five-minute operator completion times.
8. FR8: Enforce NAB-specific template guardrails, flag configuration attempts targeting unsupported institutions, and provide extension guidelines for future banks without impacting current fidelity.

## Non-Functional
1. NFR1: Rendered PDFs must achieve ≥95% pixel fidelity compared to reference NAB documents verified via automated diff tooling.
2. NFR2: Complete bundle generation within ≤30 seconds for up to three concurrent runs on the staging reference environment, with monitoring and alerting when throughput or queue depth threatens the SLA.
3. NFR3: Repeat runs with identical seeds must produce hash-identical outputs and manifests, including deterministic handling of cached or fallback merchant data for offline and CI scenarios.
4. NFR4: Generation workflows must emit structured audit logs covering inputs, rule evaluations, transformations, and output locations, stored per compliance retention policies with access controls and redaction of sensitive fields.
5. NFR5: Integration secrets must support automated rotation, per-tenant isolation, and alerting ahead of expiry, with no plaintext exposure in logs and no redeploy required for rotation.
6. NFR6: Operational telemetry must capture performance, compliance validation outcomes, and packaging success rates, surfacing dashboards for lenders and engineering teams to monitor bundle health.
