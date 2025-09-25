# Monitoring and Observability
- **Frontend Monitoring:** Next.js emits custom metrics through `apps/admin/lib/metrics-client` into Prometheus; Grafana dashboards track Core Web Vitals and WebSocket latency.
- **Backend Monitoring:** Fastify’s pino transport streams structured logs to Loki; `/metrics` exposes Prometheus counters for request/queue activity, Vault health (`vault_up`), and audit retention timestamps with Grafana dashboards for bundle throughput.
- **Error Tracking:** Self-hosted Sentry captures admin/API exceptions, tagging each with `requestId`; alerts flow to Slack.
- **Performance Monitoring:** Prometheus + Grafana visualize latency/CPU/memory; k6 scripts optional for load; BullMQ exporter surfaces queue depth and processing durations.

**Frontend Metrics:**
- Core Web Vitals
- JavaScript errors
- API response times
- User interactions

**Backend Metrics:**
- Request rate
- Error rate
- Response time
- Database query performance
