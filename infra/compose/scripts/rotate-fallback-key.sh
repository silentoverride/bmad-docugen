#!/usr/bin/env bash
set -euo pipefail

: "${VAULT_ADDR:?Missing VAULT_ADDR}"
: "${VAULT_TOKEN:?Missing VAULT_TOKEN}"

FALLBACK_PATH="secret/data/docugen/fallback-signing"
NEW_KEY=$(openssl rand -base64 32)

cat <<JSON >/tmp/fallback-key.json
{
  "data": {
    "key": "${NEW_KEY}"
  }
}
JSON

curl -s \
  --header "X-Vault-Token: $VAULT_TOKEN" \
  --request POST \
  --data @/tmp/fallback-key.json \
  "$VAULT_ADDR/v1/$FALLBACK_PATH" >/dev/null

echo "Generated new fallback signing key"
cat <<EOFJSON >infra/compose/env/vault-fallback.json
{
  "signingKey": "${NEW_KEY}"
}
EOFJSON

rm -f /tmp/fallback-key.json
