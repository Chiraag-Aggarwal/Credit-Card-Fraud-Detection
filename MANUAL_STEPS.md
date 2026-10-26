# Manual Setup and Deployment Checklist

This checklist covers actions that require a person to use hosting accounts, supply secrets, or coordinate with the team. Never put real secrets in source control or share them in chat.

## Before deployment

- [ ] Choose hosting providers for the ML service and backend, and create the required accounts.
- [ ] Create a MongoDB Atlas database and allow the backend host to connect to it.
- [ ] Prepare the production environment values listed below. Store them in each hosting provider's secret/environment-variable settings, not in committed files.
- [ ] Coordinate with the frontend developer so they can configure the backend URL in the deployed client.

## Deploy in this order

1. [ ] Deploy `/ml-service`; wait for it to become healthy and record its public base URL.
2. [ ] Deploy `/server` and configure its environment variables. Set `ML_SERVICE_URL` to the ML service URL from step 1.
3. [ ] Send the deployed backend URL to the frontend developer.
4. [ ] Deploy `/client` with `VITE_API_URL` set to the backend URL and `VITE_USE_MOCK=false`.
5. [ ] Set the backend's `CLIENT_URL` to the deployed client URL, then redeploy/restart the backend.
6. [ ] In Stripe's test-mode dashboard, create a webhook endpoint pointing to `<backend URL>/api/webhooks/stripe` and subscribe to `payment_intent.succeeded`.
7. [ ] Copy that endpoint's signing secret (`whsec_...`) into the backend's `STRIPE_WEBHOOK_SECRET`, then redeploy/restart the backend.

## Backend environment variables

Set these in the backend host's environment settings:

- `PORT` — port supplied by the hosting provider.
- `MONGODB_URI` — MongoDB Atlas connection string.
- `JWT_SECRET` — a long, randomly generated secret.
- `CLIENT_URL` — exact deployed client origin.
- `ML_SERVICE_URL` — deployed ML service base URL.
- `ML_API_KEY` — key shared with the ML service configuration.
- `ML_TIMEOUT_MS` — request timeout in milliseconds; keep it configurable because free hosts may take 30+ seconds to wake after idle.
- `STRIPE_SECRET_KEY` — Stripe test-mode secret key.
- `STRIPE_WEBHOOK_SECRET` — signing secret for the deployed Stripe webhook endpoint.
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM` — SMTP settings for email alerts. If SMTP is not configured, alerts are logged instead of emailed.

Use the deployment provider's Python 3.11 runtime for `/ml-service`. Do not upload or commit `data/creditcard.csv` or `data/processed`.

## Stripe CLI for local testing

- [ ] Install and authenticate the Stripe CLI.
- [ ] Start forwarding local test events:

  ```text
  stripe listen --forward-to localhost:5000/api/webhooks/stripe
  ```

- [ ] Put the `whsec_...` value printed by this command into the local server's `STRIPE_WEBHOOK_SECRET`. The CLI secret is for local forwarding; use the separate endpoint signing secret for the deployed webhook.
- [ ] Trigger or complete a Stripe test-mode payment and confirm the backend receives it.

## End-to-end verification

- [ ] Open the deployed client and register/login with a test merchant.
- [ ] Confirm the dashboard loads data from the real backend (not mock data).
- [ ] Simulate transactions and confirm they appear in the dashboard.
- [ ] Confirm flagged transactions appear in the review view and can be marked as fraud or legitimate.
- [ ] Complete a Stripe test-mode checkout and confirm one transaction is recorded for the payment.
- [ ] Confirm the unread alert count updates for unreviewed flagged transactions.
- [ ] Check backend and ML health endpoints after deployment.
- [ ] Verify that no real secrets, `.env` files, or prohibited dataset files were committed.

## Team handoff

- [ ] Module B owner: finish the remaining client and documentation work, including the narrow-screen layout issue and the observed rate-limit (`429`) UX, then provide any requested screenshots/demo materials.
- [ ] Team: complete the knowledge swap and confirm who owns each remaining deployment and demo task.
