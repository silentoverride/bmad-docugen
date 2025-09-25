# Audit Log Retention Runbook

This runbook explains how to manage the growth of `audit_log_entries` and the associated S3/MinIO artefact hashes to maintain compliance without exhausting local resources.

## 1. Retention Policy
- Retain high-value audit entries (override approvals, manifest signing, bundle completion) for 180 days.
- Purge routine informational entries (status polling, CLI reads) older than 30 days.
- Maintain manifest hash history indefinitely (kept in `manifests` table and MinIO) but compact indexes monthly.

## 2. Automation Script
- Script: `infra/compose/scripts/maintain-audit-retention.sh`
- Schedule: run nightly via `pnpm compose:exec scheduler ./scripts/maintain-audit-retention.sh` or add to local cron.
- Actions performed:
  1. Creates next month’s partition (rolling window).
  2. Deletes partitions older than retention thresholds.
  3. Vacuum/analyze affected tables.
  4. Emits metrics to Prometheus (`audit_retention_last_run_seconds`).

## 3. Manual Execution
```bash
pnpm compose:exec postgres bash -lc './scripts/maintain-audit-retention.sh --dry-run'
# Review planned actions, then execute without --dry-run.
```

## 4. Verifying Success
- Check API logs for `audit.retention=completed` entry.
- Review Prometheus metric `audit_retention_last_run_seconds` and Grafana alert "Audit retention missed".
- Run `SELECT count(*) FROM audit_log_entries WHERE timestamp < now() - interval '30 days';` to ensure cleanup succeeded.

## 5. Failure Handling
- If script errors, inspect logs in `infra/compose/logs/audit-retention.log`.
- Common causes: partitions missing, long-running transactions preventing drop. Resolve by ending conflicting sessions (`pg_terminate_backend`).
- Re-run script after fix. Document outcome in incident log.

## 6. References
- `docs/architecture.md` – Database Schema & Operations sections
- `docs/runbooks/redis-operations.md` – queue cleanup related to retention notifications
- Crontab example (macOS/Linux):
  ```cron
  0 2 * * * cd ~/projects/docugen && pnpm compose:exec postgres bash -lc './scripts/maintain-audit-retention.sh'
  ```
