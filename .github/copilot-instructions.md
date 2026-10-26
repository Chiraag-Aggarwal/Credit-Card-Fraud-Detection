# Project: Fraud Detection Payment Dashboard
Real-time fraud scoring for online payments. Monorepo with three services:
- /client: React (Vite), React Router, Axios, Recharts, Tailwind
- /server: Node.js + Express (ES modules), MongoDB via Mongoose, JWT auth, Stripe test-mode webhooks
- /ml-service: Python 3.11, FastAPI, scikit-learn, XGBoost, imbalanced-learn, joblib

## Data flow
Stripe payment_intent.succeeded webhook -> Express -> POST ml-service /predict -> fraud probability +
risk label -> saved in MongoDB -> React dashboard.

## ML rules (important)
- Dataset: Kaggle Credit Card Fraud (Time, V1..V28, Amount, Class). Fraud is about 0.17% of rows.
- Never use accuracy as the main metric. Use precision, recall, F1, ROC-AUC, PR-AUC and the confusion
matrix.
- Split train/validation/test BEFORE any resampling. SMOTE only on training data, inside an imblearn
Pipeline. Fit scalers on training data only.
- The decision threshold is chosen on the validation set, never on the test set. The test set is used
once at the end.

## Code rules
- Small functions, clear names, comments that explain WHY.
- Validate all inputs. No secrets in code: use .env and keep .env.example updated.
- Handle errors explicitly. The ML service being down must never crash the backend.
- Add or update tests whenever behaviour is added.
- Explain in plain English what you built after each task

## Team rules
- Two people work on this repo. Module A owns `/ml-service`, `/server` and `.github`. Module B owns `/client`, `README.md` and `/docs` (except `API_CONTRACT.md`).
- Only edit files inside the area that the current developer owns. If a task needs a change in the other area, do not make it - write a short note describing what is needed instead.
- `docs/API_CONTRACT.md` is the single source of truth for endpoints and JSON shapes. Never change URLs or field names without updating that file in the same change.
- Never commit `.env` files, `node_modules`, `venv` or `data/creditcard.csv`.
