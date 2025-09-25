#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

SQL=$(cat <<'SQL'
DO $$
DECLARE
  keep_info_days CONSTANT INTEGER := 30;
  keep_important_days CONSTANT INTEGER := 180;
  oldest_keep TIMESTAMP := NOW() - (keep_info_days || ' days')::INTERVAL;
  oldest_important TIMESTAMP := NOW() - (keep_important_days || ' days')::INTERVAL;
BEGIN
  -- Ensure next month partition exists
  PERFORM create_audit_partition(date_trunc('month', NOW()) + INTERVAL '1 month');

  -- Delete informational entries older than 30 days
  DELETE FROM audit_log_entries
  WHERE timestamp < oldest_keep
    AND payload->>'severity' IS NULL;

  -- Delete non-critical entries older than 180 days
  DELETE FROM audit_log_entries
  WHERE timestamp < oldest_important
    AND COALESCE(payload->>'severity', 'info') NOT IN ('warning','error');

  -- Reindex / analyze compact tables
  PERFORM pg_stat_reset_single_table_counters('public', 'audit_log_entries');
END $$;

VACUUM ANALYZE audit_log_entries;
SQL
)

if [[ "${DRY_RUN}" == "true" ]]; then
  echo "-- DRY RUN --"
  echo "$SQL"
  exit 0
fi

psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -c "$SQL"

echo "audit_retention_last_run_seconds $(date +%s)" > /tmp/audit_retention.prom
if [[ -n "${PROM_PUSH_GATEWAY_URL:-}" ]]; then
  curl -s --data-binary @/tmp/audit_retention.prom "$PROM_PUSH_GATEWAY_URL/metrics/job/audit_retention"
fi

echo "[audit-retention] completed at $(date -Iseconds)"
