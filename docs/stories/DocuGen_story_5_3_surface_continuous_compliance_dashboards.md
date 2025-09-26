# Story 5.3 Surface Continuous Compliance Dashboards

## Status
Draft (Multi-sprint)

## Story
**As a** risk officer,
**I want** dashboards that track control health, outstanding violations, and remediation velocity,
**so that** I can govern DocuGen without digging into raw logs.

## Acceptance Criteria
1. Admin UI ships a compliance dashboard summarising rule pass/fail trends, waiver counts, and time-to-resolution metrics.
2. Prometheus/Grafana dashboards visualise compliance KPIs and feed alert thresholds for sustained failures.
3. Dashboard tiles link to evidence bundles and manifests for drill-down investigations.
4. Access control ensures only authorised compliance roles can view sensitive metrics and waive findings.

## Tasks / Subtasks
- [ ] Design compliance dashboard layout in admin UI with requisite metrics (AC: 1)
  - [ ] Implement API endpoints aggregating rule pass/fail trends and remediation data (AC: 1)
- [ ] Configure Prometheus/Grafana dashboards and alerts for compliance KPIs (AC: 2)
  - [ ] Document dashboard expectations in `docs/architecture/monitoring-and-observability.md` (AC: 2)
- [ ] Link dashboard tiles to evidence bundles/manifests with secure download flows (AC: 3)
- [ ] Enforce RBAC in admin UI and API for compliance views and waivers (AC: 4)

## Delivery plan
- Sprint 1: design the compliance dashboard UI and implement API aggregations for rule trends and remediation metrics.
- Sprint 2: configure Prometheus/Grafana dashboards, alert thresholds, and telemetry exports tied to compliance KPIs.
- Sprint 3: link dashboard tiles to evidence bundles/manifests and tighten RBAC enforcement for compliance-only access.

## Dev Notes
- Admin UI architecture and state patterns are documented in `docs/architecture/frontend-architecture.md` and `docs/architecture/components.md#admin-web-app`.
- Compliance telemetry expectations originate from `docs/prd/epic-3-operational-delivery-observability.md` and `docs/prd/epic-5-compliance-automation-continuous-assurance.md`.
- RBAC requirements align with Keycloak usage described in `docs/architecture/backend-architecture.md#authentication-authorization`.
- Ensure evidence bundle links reuse flows defined in Story 5.2 to avoid duplication.

## Cross-epic dependencies
- Epic 3 – Story 3.4 provides shared observability dashboards and alerting foundations for compliance metrics.

### Testing
- Add UI tests (Playwright) covering dashboard visuals, filters, and restricted access per `docs/architecture/testing-strategy.md`.
- Create integration tests verifying API aggregates and RBAC enforcement.
- Validate Prometheus/Grafana dashboards via snapshot exports or automated assertions.

## Change Log
| Date       | Version | Description            | Author |
|------------|---------|------------------------|--------|
| 2025-09-27 | 0.1     | Initial story draft    | PO     |
| 2025-09-27 | 0.2     | Promoted to Approved; added observability documentation task | PO |

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
