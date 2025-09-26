# Introduction
This document outlines the complete fullstack architecture for DocuGen, covering backend services, frontend experiences, and their integration across the CLI and admin surfaces that power the DocuGen platform. It serves as the single source of truth for Codex automation agents to execute deterministic, compliance-ready builds that uphold NAB fidelity requirements.

By replacing separate backend and frontend architecture docs, we keep operations, compliance, and integration stakeholders aligned on one blueprint, ensuring regulatory guardrails, audit traceability, and automation guardrails remain front-and-center. This unified approach also streamlines coordination for engineers extending DocuGen’s APIs and UI surfaces.

The next section evaluates whether DocuGen should leverage an existing starter template or repository baseline so any inherited decisions inform the architecture choices documented here.

## Starter Template or Existing Project
N/A – Greenfield project. The PRD and UX spec make no reference to existing starter repos or vendor templates, and the current repository only contains documentation assets. We’ll design DocuGen’s architecture with full flexibility while keeping room to introduce an Nx/Turborepo-style monorepo starter later if we decide to accelerate developer tooling.

## Change Log
| Date       | Version | Description             | Author             |
|------------|---------|-------------------------|--------------------|
| 2025-09-26 | 0.1     | Initial fullstack draft | Winston (Architect) |
