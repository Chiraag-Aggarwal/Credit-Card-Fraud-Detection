# API Contract (source of truth for frontend and backend)

- Base URL: VITE_API_URL (local: http://localhost:5000). Every path below starts with /api. JSON only.
- Protected routes need the header Authorization: Bearer <token> (token comes from login/register).
- Errors always look like {"error":{"message":"...","code":"..."}}. Status 401 = not logged in (UI goes to /login), 422 = bad input, 429 = too many requests.
- The API returns id (not _id) and never returns the 30 model features.

## Transaction object

- id: string
- createdAt: ISO date string
- displayAmount: number (major units, e.g. 49.99)
- currency: string, e.g. "usd"
- source: "stripe" or "simulated"
- fraudProbability: number 0 to 1, or null when UNSCORED
- riskLabel: "LOW" | "MEDIUM" | "HIGH" | "UNSCORED"
- isFlagged: boolean
- scoringStatus: "scored" or "pending_review" (ML service was down)
- modelVersion: string, e.g. "xgb-v1"
- reviewDecision: null | "confirmed_fraud" | "legit"
- stripePaymentIntentId: string or null

## Endpoints

### POST /auth/register [auth: public]

Request: `{name, email, password (min 8)}`

Response: `201 {token, user}` where user = `{id, name, email, role}`

### POST /auth/login [auth: public]

Request: `{email, password}`

Response: `{token, user}`

### GET /auth/me [auth: token]

Request:

Fraud Detection Dashboard  |  Module A (ML + Backend) Page 6  
PROMPT T0.1 - Write the API contract file

Response: `{user}`

### GET /transactions [auth: token]

Request: query: page (1), limit (20), riskLabel, flagged (true), from, to (ISO dates). Newest first.

Response: `{items: [Transaction], page, limit, total}`

### GET /transactions/stats [auth: token]

Request:

Response: `{total, flagged, fraudRate (0-1), avgProbability (0-1), byRisk: {LOW, MEDIUM, HIGH, UNSCORED}, series24h: [{t, total, flagged}], series30d: [{t, total, flagged}]} (t = ISO date; hourly for 24h, daily for 30d)`

### GET /transactions/score-histogram [auth: token]

Request:

Response: `{bins: [{from, to, count}]}` (10 bins from 0.0 to 1.0)

### POST /transactions/simulate [auth: token]

Request: `{count (1-50), mode: "random" | "fraud"}`

Response: `{created, items: [Transaction]}`

### PATCH /transactions/:id/review [auth: token]

Request: `{decision: "confirmed_fraud" | "legit"}`

Response: `Transaction (updated)`

### POST /payments/checkout-session [auth: token]

Request: `{amount (>= 1), currency ("usd"), mode: "normal" | "fraud-demo"}`

Response: `{url}` (browser redirects to Stripe)

### GET /model-info [auth: token]

Request:

Response: `{model_version, threshold, min_precision, trained_at, metrics: {precision, recall, f1, roc_auc, pr_auc, confusion_matrix: [[tn, fp], [fn, tp]]}}`

### GET /alerts/unread-count [auth: token]

Request:

Response: `{count}` (flagged transactions not yet reviewed)

Rule: nobody changes this file silently. If a shape must change, update this file, commit, and message the other person
