# Coding Standards
- **Type Source of Truth:** Import all TypeScript types from `packages/shared-types`; never redeclare interfaces inside apps.
- **IO Boundaries:** Use shared IO helpers (`apiClient`, `packages/core-domain` job builders) for HTTP and BullMQ payloads; no ad-hoc fetch calls or JSON bodies.
- **Secrets & Config:** Load secrets/signing keys through Vault or env config helpers; never hardcode credentials or reach for `process.env` inside business logic.
- **Standard Error Handling:** Fastify handlers respond via `reply.sendError`/`createHttpError`; workers use the job failure utility so telemetry stays consistent.
- **Structured Logging & Telemetry:** Use the shared pino logger (`packages/core-domain/logger`) with run/bundle IDs; avoid `console.log` in production code.
- **Deterministic Fixtures:** Tests import fixtures from `tests/fixtures` and update via scripts—no inline JSON or random data.
- **Immutable React State:** Local component state must be updated immutably using `setState`/spread patterns; never mutate objects or arrays in place even outside Query/Zustand.

| Element          | Frontend                    | Backend    | Example                    |
|------------------|-----------------------------|------------|----------------------------|
| Components       | PascalCase                  | –          | `BundleRunCard.tsx`        |
| Hooks            | camelCase with 'use'        | –          | `useAuthSession.ts`        |
| API Routes       | –                           | kebab-case | `/api/v1/bundle-runs`      |
| Database Tables  | –                           | snake_case | `document_bundle_runs`     |
