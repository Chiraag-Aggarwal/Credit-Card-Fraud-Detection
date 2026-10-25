# API Contract

This document defines the request and response shapes used by the Fraud Detection Payment Dashboard. JSON values shown below are illustrative; field names and types define the contract.

## Base URL and conventions

- Configure the API base URL with `VITE_API_URL`.
- Local base URL: `http://localhost:5000`.
- Every endpoint path below starts with `/api`.
- Requests and responses use JSON.
- Protected endpoints require `Authorization: Bearer <token>`. The token is returned by registration or login.
- Errors use this shape: `{ "error": { "message": "...", "code": "..." } }`.
- `401` means unauthenticated, `422` means invalid input, and `429` means rate limited.
- Responses use `id`, not `_id`, and never include the 30 model input features.

## Transaction

| Field | Type / values |
| --- | --- |
| `id` | string |
| `createdAt` | ISO date-time string |
| `displayAmount` | number in major currency units, such as `49.99` |
| `currency` | string, such as `usd` |
| `source` | `stripe` or `simulated` |
| `fraudProbability` | number from `0` to `1`, or `null` when unscored |
| `riskLabel` | `LOW`, `MEDIUM`, `HIGH`, or `UNSCORED` |
| `isFlagged` | boolean |
| `scoringStatus` | `scored` or `pending_review` |
| `modelVersion` | string, such as `xgb-v1` |
| `reviewDecision` | `null`, `confirmed_fraud`, or `legit` |
| `stripePaymentIntentId` | string or `null` |

## Endpoints

### Authentication

#### `POST /api/auth/register` - public

Request:

```json
{
  "name": "Avery Merchant",
  "email": "avery@example.com",
  "password": "at-least-8-characters"
}
```

`password` must be at least 8 characters. Response status is `201`.

```json
{
  "token": "<jwt>",
  "user": {
    "id": "user-id",
    "name": "Avery Merchant",
    "email": "avery@example.com",
    "role": "<role>"
  }
}
```

#### `POST /api/auth/login` - public

Request:

```json
{
  "email": "avery@example.com",
  "password": "password"
}
```

Response:

```json
{
  "token": "<jwt>",
  "user": {
    "id": "user-id",
    "name": "Avery Merchant",
    "email": "avery@example.com",
    "role": "<role>"
  }
}
```

#### `GET /api/auth/me` - token required

Response:

```json
{
  "user": {
    "id": "user-id",
    "name": "Avery Merchant",
    "email": "avery@example.com",
    "role": "<role>"
  }
}
```

### Transactions

#### `GET /api/transactions` - token required

Query parameters:

- `page` (default `1`)
- `limit` (default `20`)
- `riskLabel`
- `flagged` (`true` to show flagged transactions)
- `from` and `to` (ISO dates)

Results are newest first.

```json
{
  "items": [
    {
      "id": "transaction-id",
      "createdAt": "2026-10-25T12:30:00.000Z",
      "displayAmount": 49.99,
      "currency": "usd",
      "source": "stripe",
      "fraudProbability": 0.12,
      "riskLabel": "LOW",
      "isFlagged": false,
      "scoringStatus": "scored",
      "modelVersion": "xgb-v1",
      "reviewDecision": null,
      "stripePaymentIntentId": "pi_example"
    }
  ],
  "page": 1,
  "limit": 20,
  "total": 1
}
```

#### `GET /api/transactions/stats` - token required

```json
{
  "total": 100,
  "flagged": 8,
  "fraudRate": 0.08,
  "avgProbability": 0.12,
  "byRisk": {
    "LOW": 80,
    "MEDIUM": 12,
    "HIGH": 8,
    "UNSCORED": 0
  },
  "series24h": [
    { "t": "2026-10-25T12:00:00.000Z", "total": 4, "flagged": 1 }
  ],
  "series30d": [
    { "t": "2026-10-25T00:00:00.000Z", "total": 12, "flagged": 2 }
  ]
}
```

`fraudRate` and `avgProbability` are numbers from `0` to `1`. `series24h` is hourly and `series30d` is daily; `t` is an ISO date-time string.

#### `GET /api/transactions/score-histogram` - token required

Returns 10 score bins spanning `0.0` to `1.0`.

```json
{
  "bins": [
    { "from": 0.0, "to": 0.1, "count": 12 }
  ]
}
```

#### `POST /api/transactions/simulate` - token required

Request `count` is from `1` to `50`; `mode` is `random` or `fraud`.

```json
{
  "count": 1,
  "mode": "random"
}
```

Response:

```json
{
  "created": 1,
  "items": [
    {
      "id": "transaction-id",
      "createdAt": "2026-10-25T12:30:00.000Z",
      "displayAmount": 49.99,
      "currency": "usd",
      "source": "simulated",
      "fraudProbability": 0.12,
      "riskLabel": "LOW",
      "isFlagged": false,
      "scoringStatus": "scored",
      "modelVersion": "xgb-v1",
      "reviewDecision": null,
      "stripePaymentIntentId": null
    }
  ]
}
```

#### `PATCH /api/transactions/:id/review` - token required

Request `decision` is `confirmed_fraud` or `legit`.

```json
{
  "decision": "confirmed_fraud"
}
```

Response is the updated `Transaction` object.

### Payments

#### `POST /api/payments/checkout-session` - token required

Request `amount` is at least `1`, `currency` is `usd`, and `mode` is `normal` or `fraud-demo`.

```json
{
  "amount": 1,
  "currency": "usd",
  "mode": "normal"
}
```

Response:

```json
{
  "url": "https://checkout.example.com/session"
}
```

### Model information and alerts

#### `GET /api/model-info` - token required

```json
{
  "model_version": "xgb-v1",
  "threshold": 0.5,
  "min_precision": 0.9,
  "trained_at": "2026-10-25T12:30:00.000Z",
  "metrics": {
    "precision": 0.91,
    "recall": 0.84,
    "f1": 0.87,
    "roc_auc": 0.96,
    "pr_auc": 0.73,
    "confusion_matrix": [[980, 20], [8, 42]]
  }
}
```

#### `GET /api/alerts/unread-count` - token required

Returns the number of flagged transactions that have not been reviewed.

```json
{
  "count": 3
}
```