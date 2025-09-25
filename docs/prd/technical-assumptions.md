# Technical Assumptions

## Repository Structure: Monorepo
Maintain a single repository hosting the TypeScript generation engine, configuration schemas, rendering templates, and infrastructure-as-code so cross-cutting updates stay synchronised and reproducible.

## Service Architecture
Adopt a modular monolith comprised of orchestrator services, data preparation modules, and rendering workers within one deployable Node.js application, exposing CLI and API entry points while enabling future extraction of workloads if scale demands.

## Testing Requirements
Pursue a full testing pyramid: exhaustive unit tests for calculators and formatters, integration tests covering end-to-end bundle generation with golden fixtures, and smoke-level e2e checks validating packaging and delivery flows in staging.

## Additional Technical Assumptions and Requests
- Target Node.js 20 LTS with TypeScript strict mode to align with Puppeteer compatibility and deterministic async handling.
- Manage render jobs via a worker queue (e.g., BullMQ) to throttle concurrency and maintain ≤30 second SLA under load.
- Persist manifests, logs, and packaged bundles in AWS S3 with SSE-KMS encryption and lifecycle policies mapped to compliance retention windows.
- Provide configuration-driven merchant enrichment settings including cache TTLs, offline fallbacks, and manual override hooks for QA scenarios.
