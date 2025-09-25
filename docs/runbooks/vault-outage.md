# Vault Outage Runbook

This runbook describes how to keep DocuGen bundle signing operational when the local Vault dev server is unavailable. Follow the steps in order and record actions in the incident log.

## 1. Detect the Incident
- Check the Grafana "Vault Health" panel (fed by the `vault_up` Prometheus gauge).
- CLI/admin alerts: banner "Vault offline" or audit log entries with `signing.fallback=true`.
- API logs (`infra/compose/logs/vault.log`) showing connection errors such as `connection refused` or `status 503`.

## 2. Immediate Mitigation
1. **Retry & Backoff**
   - The API/worker code automatically retries transit requests with exponential backoff (3 attempts). No manual intervention required unless retries fail.
2. **Enable Fallback Signer**
   - Ensure the environment variable `ALLOW_FALLBACK_SIGNING=true` is set for `api` and `worker` containers.
   - Verify the fallback key file exists: `infra/compose/env/vault-fallback.json` (generated during `pnpm compose:setup`).
   - Restart only the affected services to apply env changes:
     ```bash
     pnpm compose:restart api worker
     ```
3. **Confirm Fallback Active**
   - Tail API logs: look for `signing_mode=fallback` messages.
   - Trigger a test bundle run via CLI and confirm the manifest is produced. Audit log should record `signingMode: fallback`.

## 3. Restore Vault
1. Inspect the Vault container:
   ```bash
   docker logs docugen_vault
   docker exec -it docugen_vault vault status
   ```
2. If sealed, unseal using the keys stored in `infra/compose/env/vault-unseal-keys.txt` (created during setup):
   ```bash
   docker exec -it docugen_vault vault operator unseal <key1>
   docker exec -it docugen_vault vault operator unseal <key2>
   docker exec -it docugen_vault vault operator unseal <key3>
   ```
3. If the container crashed, restart it:
   ```bash
   pnpm compose:restart vault
   ```
4. Re-run the bootstrap script to re-create transit keys if necessary:
   ```bash
   pnpm compose:exec vault ./scripts/bootstrap-vault.sh
   ```

## 4. Roll Back Fallback Mode
1. Once Vault is healthy (`vault_up=1` and `vault status` is "Initialized"/"Unsealed"), disable fallback signing:
   ```bash
   pnpm compose:exec api bash -lc 'unset ALLOW_FALLBACK_SIGNING'
   pnpm compose:exec worker bash -lc 'unset ALLOW_FALLBACK_SIGNING'
   pnpm compose:restart api worker
   ```
2. Run a validation bundle to confirm manifests are signed by Vault (audit log `signingMode: vault`).
3. Archive the incident details and metrics snapshots in `docs/runbooks/incidents/` (create directory if needed).

## 5. Post-Incident Checklist
- [ ] Record incident timeline and remediation in the engineering notebook.
- [ ] Rotate fallback key by re-running `pnpm compose:exec vault ./scripts/rotate-fallback-key.sh`.
- [ ] Verify Grafana alerts reset and no further fallback audit entries appear.
- [ ] Notify the team via Slack `#docugen-alerts` with summary and next steps.

## Appendix
- **Key files**
  - Fallback key: `infra/compose/env/vault-fallback.json`
  - Vault token: `infra/compose/env/vault-root-token.txt`
  - Unseal keys: `infra/compose/env/vault-unseal-keys.txt`
- **Related Docs**
  - `docs/architecture.md` – Security & Performance section
  - `docs/runbooks/redis-operations.md` – Redis restart procedures
  - `docs/runbooks/audit-retention.md` – Audit pruning tasks
