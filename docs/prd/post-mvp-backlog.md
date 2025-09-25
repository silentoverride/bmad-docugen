# Post-MVP Backlog

| Backlog Item | Priority | Rationale | Key Dependencies | Suggested Release Window |
|--------------|----------|-----------|-------------------|--------------------------|
| Multi-bank expansion (additional Australian institutions with reusable templates and rule packs) | P1 | Unlocks the primary growth lever once NAB fidelity is proven; leverages existing deterministic engine with moderate incremental effort. | Completion of Epic 2 compliance tooling; template authoring guide. | Release 1.1 (immediately after MVP hardening) |
| Partner SDK for fintech integrators (embed generation flows) | P2 | Drives adoption and ecosystem stickiness; reuses manifests and packaging work with focused developer experience polish. | Epic 3 packaging APIs; documentation baseline. | Release 1.2 |
| Operator UI enhancements (bulk scheduling, inline diff previews, workflow notifications) | P2 | Reduces operational toil and accelerates compliance review, but depends on stable telemetry and bundle APIs. | Observability dashboards from Epic 3; UX spec. | Release 1.2 |
| Real-time bank API ingestion (live data pulls) | P3 | High strategic value but requires additional security, consent, and rate-limit work; should follow stability and audit learnings. | External API contracts; security/legal review; secrets rotation maturity. | Release 1.3 |
| Analytics & anomaly detection module (borrower insights, compliance trends) | P3 | Supports long-term differentiation, built atop telemetry and historical manifests once sufficient data volume exists. | Observability data warehouse; retention policies. | Release 1.3+ |

Prioritisation aligns with current epics: Release 1.1 extends compliance wins into broader bank coverage, Release 1.2 emphasises partner and operator experience once packaging stabilises, and Release 1.3 tackles data- and integration-heavy initiatives after telemetry matures.
