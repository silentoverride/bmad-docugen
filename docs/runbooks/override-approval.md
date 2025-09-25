# Override Approval Runbook

This document defines the mandatory dual-approval flow for DocuGen validation overrides. Overrides allow compliance reviewers to waive blocking errors; they must be tightly controlled.

## 1. Roles & Permissions
- **Initiator (Reviewer)**: Must have Keycloak role `bundle.override.request`. Can request an override with justification.
- **Approver (Compliance Lead)**: Requires `bundle.override.approve`. Reviews requests and either approves or rejects.
- **Audit Observer**: Any user with `bundle.read` can view the override history but cannot modify it.

## 2. Override Lifecycle
1. **Request**
   - Reviewer opens bundle detail → "Override validation".
   - Provides mandatory justification (minimum 50 chars) and selects rule code(s) to override.
   - System creates record in `override_requests` table with status `pending` and logs audit entry (`action=override.requested`).
2. **Approval**
   - Compliance Lead receives Slack notification via webhook.
   - Approver reviews context (diff links, validation details) and either approves or rejects.
   - Approval requires second factor: the approver re-enters Keycloak password.
   - On approval, status becomes `approved`; queue enqueues `bundle:validate` job with override directives. Audit log records `override.approved` with approver details.
3. **Execution**
   - Validation worker re-runs rule; if pass → bundle marks override applied, else remains failed.
   - CLI/admin surfaces final status and includes override metadata in manifest.
4. **Rejection**
   - Status `rejected`; reviewer receives notification. Audit log `override.rejected` stored.

## 3. Operational Procedures
- **Emergency Override Suspension**: Toggle `ALLOW_OVERRIDES=false` in API env to disable new requests; existing approvals unaffected.
- **Manual Cleanup**: Use `pnpm --filter api run overrides:list --status pending` to review stale requests; reject if older than 24h.
- **Reporting**: Weekly summary job exports overrides to `reports/overrides-weekly.csv` for compliance review.

## 4. Incident Handling
- If approver unavailable, assign temporary approver by granting `bundle.override.approve` role and logging change in audit system.
- If override applied in error, create counter-override by rejecting and re-running validation, or revert bundle to previous state (CLI `bundle revert --run-id ...`).

## 5. References
- `docs/architecture.md` – Core Workflows section
- `docs/runbooks/vault-outage.md` – ensures manifest signing still occurs after override
- Slack channel `#docugen-compliance` – notifications & approvals
