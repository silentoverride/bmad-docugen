# Security and Performance
## Security Requirements
- **Frontend:** Strict CSP (`default-src 'self'` etc.), React strict mode, DOMPurify for dynamic content, session tokens stored in HttpOnly `docugen_session` cookie only.
- **Backend:** zod validation on every route, OWASP sanitizers for free text, Fastify rate limiting (100 req/min/IP) backed by Redis, CORS locked to known hosts, queue concurrency caps.
- **Vault Fallback:** API/worker retries transit signing, and if `ALLOW_FALLBACK_SIGNING=true`, a temporary signer activates while raising audit warnings; see `docs/runbooks/vault-outage.md`.
- **Authentication:** Keycloak-managed tokens with 60-minute access / 45-minute refresh window, Redis cache invalidated on logout, forced logout on role change, Keycloak password policy requiring ≥12 chars with complexity.

## Performance Optimization
- **Frontend:** Target <250 KB JS on first load, use streaming + Suspense skeletons, lazy-load heavy charts, TanStack Query SWR caching, Traefik caches static assets (1 hour max-age).
- **Backend:** Keep config/bundle GET endpoints under 150 ms p95 (500 ms for launch), maintain indexes on status/started_at, monthly partition audit logs, dedicate `redis-queue` to BullMQ and `redis-cache` to introspection/lookup workloads, BullMQ exporter tracks queue depth.
