# External APIs
- **Purpose:** Enrich merchant and employer entities with canonical metadata so statements, payslips, and proofs of balance stay synchronized.
- **API:** Google Places Web Service (`https://places.googleapis.com/v1/`)
- **Authentication:** API key pulled from Vault dev server (production: service-account credentials). Backend proxy keeps keys off clients.
- **Rate Limits:** Default 90k QPD; locally throttle to 5 QPS with exponential backoff and cache-first strategy.

**Endpoints Used:**
- `POST /places:searchText`
- `GET /places/{placeId}`
- `POST /places:searchNearby`

**Integration Notes:** Backend services cache responses in Postgres + Redis for deterministic reruns. Offline/CI runs stub responses from fixtures.
