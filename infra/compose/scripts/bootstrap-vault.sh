#!/usr/bin/env bash
set -euo pipefail

: "${VAULT_ADDR:?Missing VAULT_ADDR}"
: "${VAULT_TOKEN:?Missing VAULT_TOKEN}"

TRANSIT_PATH="transit/keys/docugen-manifest"
FALLBACK_PATH="secret/data/docugen/fallback-signing"

# Enable transit if not enabled
if ! curl -s \
  --header "X-Vault-Token: $VAULT_TOKEN" \
  "$VAULT_ADDR/v1/sys/mounts/transit" | jq -e '.data' >/dev/null; then
  curl -s --header "X-Vault-Token: $VAULT_TOKEN" --request POST \
    --data '{"type":"transit"}' "$VAULT_ADDR/v1/sys/mounts/transit" >/dev/null
fi

# Create transit key if missing
curl -s --header "X-Vault-Token: $VAULT_TOKEN" \
  --request POST \
  --data '{"type":"ecdsa-p256","exportable":true}' \
  "$VAULT_ADDR/v1/$TRANSIT_PATH" >/dev/null

# Seed fallback key file if absent
if [ ! -f infra/compose/env/vault-fallback.json ]; then
  openssl rand -base64 32 > /tmp/fallback.key
  cat <<JSON >infra/compose/env/vault-fallback.json
{
  "signingKey": "$(cat /tmp/fallback.key)"
}
JSON
  rm /tmp/fallback.key
fi

echo "Vault bootstrap complete"
