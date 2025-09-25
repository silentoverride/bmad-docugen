# Redis Operations Runbook

This runbook covers monitoring and remediation for DocuGen Redis services. The stack uses separate Redis instances for queue processing (`redis-queue`) and caching (`redis-cache`).

## 1. Service Overview
- **redis-queue**: backs BullMQ queues, job scheduling, and pub/sub for worker notifications.
- **redis-cache**: handles JWT introspection cache, merchant lookup cache, and short-lived presigned URLs.
- **Connections**
  - Environment variables: `REDIS_QUEUE_URL`, `REDIS_CACHE_URL` (default `redis://redis-queue:6379` and `redis://redis-cache:6379`).
  - Both services export metrics via the Redis exporter container (`redis-exporter`) scraped by Prometheus.

## 2. Monitoring & Alerts
- Grafana dashboards: "Redis Queue" (latency, queue depth) and "Redis Cache" (command duration).
- Alerts trigger when:
  - Queue latency > 2s for 5 minutes
  - Cache command duration > 50ms p95 for 10 minutes
  - Memory usage > 80%

## 3. Common Tasks
### 3.1 Inspect Queue Depth
```bash
pnpm compose:exec redis-queue redis-cli -- latency  
# or directly query BullMQ metrics
echo "LRANGE bull:bundle:render:wait 0 5" | pnpm compose:exec redis-queue redis-cli
```

### 3.2 Flush Dev Data (never in prod)
```bash
# Queue flush
pnpm compose:exec redis-queue redis-cli FLUSHALL

# Cache flush
pnpm compose:exec redis-cache redis-cli FLUSHALL
```

### 3.3 Promote Priority Jobs
```bash
# Example: move delayed jobs to active immediately
pnpm compose:exec redis-queue redis-cli "ZRANGE bull:bundle:render:delayed 0 -1"
# Use BullMQ admin CLI to promote
pnpm --filter api run queue:promote bundle:render
```

## 4. Incident Response
### Scenario A: redis-queue Unavailable
1. Check container state: `pnpm compose:ps redis-queue`.
2. Review logs: `pnpm compose:logs redis-queue`.
3. Restart service: `pnpm compose:restart redis-queue`.
4. Validate workers reconnect: monitor worker logs for `Queue connection restored`.
5. Backlog recovery: run `pnpm --filter api run queue:drain bundle:render` if necessary.

### Scenario B: redis-cache Latency Spikes
1. Identify offending commands via `SLOWLOG GET 20`.
2. Check cache size: `INFO memory`.
3. If memory pressure, adjust TTLs in config or flush and rebuild caches (`pnpm compose:exec redis-cache redis-cli FLUSHDB`).
4. Ensure JWT cache still populated: trigger CLI login and confirm tokens refresh normally.

### Scenario C: Both Redis Instances Down
1. Restart both containers: `pnpm compose:restart redis-queue redis-cache`.
2. Confirm exporters reconnect: `pnpm compose:logs redis-exporter`.
3. Run smoke test: `pnpm --filter cli run bundle:launch --dry-run`.
4. Monitor Grafana for latency normalization.

## 5. Configuration Changes
- Update `REDIS_QUEUE_URL` / `REDIS_CACHE_URL` in `.env` or Compose overrides to point at external Redis if required.
- To scale vertically, adjust `infra/compose/docker-compose.yml` resource limits or move to managed Redis; document endpoints in the env files.

## 6. References
- `docs/architecture.md` – Backend Architecture & Development Workflow sections
- `docs/runbooks/vault-outage.md` – fallback signage when Redis outage influences queue timing
- `infra/compose/scripts/maintain-audit-retention.sh` – scheduled job referencing redis queues for cleanup notifications
