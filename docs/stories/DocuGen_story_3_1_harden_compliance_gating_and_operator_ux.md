# Story 3.1 Harden Compliance Gating and Operator UX

## Status
Draft

## Story
**As a** lending operations supervisor,
**I want** compliance gates and clear operator messaging in the generation workflow,
**so that** bundles failing policy checks never progress and operators know how to resolve issues quickly.

## Acceptance Criteria
1. CLI and admin UI block progression past validation failures, presenting remediation guidance mapped to rule ids.
2. Role-based access ensures only authorised operators can approve overrides with justification notes logged in manifests.
3. Success path completes within the five-minute operator target for seed scenarios, measured via telemetry.
4. Training mode provides sample runs with annotated feedback for onboarding new operators.

## Tasks / Subtasks
- [ ] Add gate enforcement in CLI and admin UI, displaying remediation guidance linked to rule ids (AC: 1)
- [ ] Implement RBAC enforcement for overrides and capture justification in manifests (AC: 2)
- [ ] Instrument telemetry for operator journey timing and tune flow to meet five-minute target (AC: 3)
- [ ] Build training mode with annotated sample runs accessible via CLI and UI (AC: 4)

## Dev Notes
- Coordinate with compliance diagnostics from Story 2.1 to surface rule identifiers and remediation hints.
- Ensure RBAC aligns with Keycloak configuration described in `docs/architecture/backend-architecture.md#authentication-authorization`.
- Training mode should reuse fixtures from Epic 4 to minimise asset duplication.

## Cross-epic dependencies
- Epic 2 – Story 2.1 provides the compliance rule diagnostics consumed by gating and remediation flows.
- Epic 4 – Story 4.2 supplies sample fixtures leveraged in operator training mode.

### Testing
- Add end-to-end tests ensuring failed runs block progression and display remediation details.
- Simulate override flows in integration tests to verify RBAC enforcement and manifest logging.

## Change Log
| Date       | Version | Description         | Author |
|------------|---------|---------------------|--------|
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
