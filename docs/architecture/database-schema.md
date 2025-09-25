# Database Schema
```sql
CREATE TYPE bundle_status AS ENUM ('pending', 'running', 'completed', 'failed', 'blocked');
CREATE TYPE seed_source AS ENUM ('uploaded', 'fixture', 'api');
CREATE TYPE validation_severity AS ENUM ('info', 'warning', 'error');
CREATE TYPE validation_status AS ENUM ('pass', 'fail', 'blocked');

CREATE TABLE configuration_sets (
    id UUID PRIMARY KEY,
    seed_source seed_source NOT NULL,
    seed_payload JSONB NOT NULL,
    render_options JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_by_type TEXT NOT NULL CHECK (created_by_type IN ('cli-user','admin-user','automation')),
    created_by_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX configuration_sets_seed_source_idx ON configuration_sets(seed_source);
CREATE INDEX configuration_sets_created_at_idx ON configuration_sets(created_at DESC);

CREATE TABLE document_bundle_runs (
    id UUID PRIMARY KEY,
    configuration_id UUID NOT NULL REFERENCES configuration_sets(id) ON DELETE RESTRICT,
    seed_hash TEXT NOT NULL,
    status bundle_status NOT NULL DEFAULT 'pending',
    triggered_by_type TEXT NOT NULL CHECK (triggered_by_type IN ('cli-user','admin-user','automation')),
    triggered_by_id TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    manifest_id UUID,
    run_parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (manifest_id)
);

CREATE INDEX bundle_runs_configuration_idx ON document_bundle_runs(configuration_id);
CREATE INDEX bundle_runs_status_idx ON document_bundle_runs(status);
CREATE INDEX bundle_runs_started_at_idx ON document_bundle_runs(started_at DESC);

CREATE TABLE employers (
    id UUID PRIMARY KEY,
    legal_name TEXT NOT NULL,
    abn TEXT UNIQUE,
    address JSONB NOT NULL,
    places_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE applicant_profiles (
    id UUID PRIMARY KEY,
    full_name TEXT NOT NULL,
    date_of_birth DATE NOT NULL,
    primary_employer_id UUID,
    addresses JSONB NOT NULL DEFAULT '[]'::jsonb,
    CONSTRAINT applicant_primary_employer_fk FOREIGN KEY (primary_employer_id) REFERENCES employers(id)
        DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE financial_accounts (
    id UUID PRIMARY KEY,
    applicant_id UUID NOT NULL REFERENCES applicant_profiles(id) ON DELETE CASCADE,
    institution JSONB NOT NULL,
    account_number_masked TEXT NOT NULL,
    currency TEXT NOT NULL CHECK (char_length(currency) = 3),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX financial_accounts_applicant_idx ON financial_accounts(applicant_id);

CREATE TABLE account_snapshots (
    id UUID PRIMARY KEY,
    bundle_run_id UUID NOT NULL REFERENCES document_bundle_runs(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES financial_accounts(id) ON DELETE CASCADE,
    period JSONB NOT NULL,
    opening_balance NUMERIC(16,2) NOT NULL,
    closing_balance NUMERIC(16,2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (bundle_run_id, account_id)
);

CREATE INDEX account_snapshots_bundle_idx ON account_snapshots(bundle_run_id);

CREATE TABLE merchants (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    places_id TEXT UNIQUE,
    address JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE transaction_records (
    id UUID PRIMARY KEY,
    snapshot_id UUID NOT NULL REFERENCES account_snapshots(id) ON DELETE CASCADE,
    merchant_id UUID REFERENCES merchants(id),
    amount NUMERIC(16,2) NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    description TEXT NOT NULL,
    extra_metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX transaction_records_snapshot_idx ON transaction_records(snapshot_id);
CREATE INDEX transaction_records_occurred_at_idx ON transaction_records(occurred_at);
CREATE INDEX transaction_records_merchant_idx ON transaction_records(merchant_id);

CREATE TABLE payslip_records (
    id UUID PRIMARY KEY,
    bundle_run_id UUID NOT NULL REFERENCES document_bundle_runs(id) ON DELETE CASCADE,
    employer_id UUID NOT NULL REFERENCES employers(id) ON DELETE RESTRICT,
    period JSONB NOT NULL,
    gross_pay NUMERIC(16,2) NOT NULL,
    net_pay NUMERIC(16,2) NOT NULL,
    tax_withheld NUMERIC(16,2) NOT NULL,
    super_contribution NUMERIC(16,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX payslip_bundle_idx ON payslip_records(bundle_run_id);

CREATE TABLE document_artefacts (
    id UUID PRIMARY KEY,
    bundle_run_id UUID NOT NULL REFERENCES document_bundle_runs(id) ON DELETE CASCADE,
    artefact_type TEXT NOT NULL CHECK (artefact_type IN ('bank_statement','payslip','proof_of_balance')),
    storage_key TEXT NOT NULL,
    checksum TEXT NOT NULL,
    render_version TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (bundle_run_id, artefact_type)
);

CREATE INDEX document_artefacts_bundle_idx ON document_artefacts(bundle_run_id);

CREATE TABLE manifests (
    id UUID PRIMARY KEY,
    bundle_run_id UUID NOT NULL UNIQUE REFERENCES document_bundle_runs(id) ON DELETE CASCADE,
    hash TEXT NOT NULL,
    signature TEXT NOT NULL,
    signing_key_id TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE validation_results (
    id UUID PRIMARY KEY,
    bundle_run_id UUID NOT NULL REFERENCES document_bundle_runs(id) ON DELETE CASCADE,
    rule_code TEXT NOT NULL,
    severity validation_severity NOT NULL,
    status validation_status NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (bundle_run_id, rule_code)
);

CREATE INDEX validation_results_bundle_idx ON validation_results(bundle_run_id);
CREATE INDEX validation_results_status_idx ON validation_results(status);

CREATE TABLE audit_log_entries (
    id UUID PRIMARY KEY,
    bundle_run_id UUID REFERENCES document_bundle_runs(id) ON DELETE CASCADE,
    actor_type TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    action TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    payload JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX audit_bundle_idx ON audit_log_entries(bundle_run_id);
CREATE INDEX audit_action_idx ON audit_log_entries(action);
CREATE INDEX audit_timestamp_idx ON audit_log_entries(timestamp DESC);
```

Automated retention is handled by `infra/compose/scripts/maintain-audit-retention.sh`, invoked nightly via cron or the scheduler service. It seeds future partitions, removes stale data following the retention policy, and exports a Prometheus timestamp gauge. Operational steps are documented in `docs/runbooks/audit-retention.md`.
