"""Streamlit interface for scoring credit-card transaction CSV files."""

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from train_model import FEATURE_COLUMNS, MODEL_PATH


st.set_page_config(page_title="Credit Card Fraud Detection", page_icon="💳")
st.title("Credit Card Fraud Detection")
st.write(
    "Score transaction records with the trained model. Predictions are "
    "estimates and should not be used as the sole basis for financial decisions."
)

threshold = st.slider(
    "Fraud probability threshold",
    min_value=0.05,
    max_value=0.95,
    value=0.5,
    step=0.05,
)

if not Path(MODEL_PATH).is_file():
    st.info("No trained model found. Place the Kaggle dataset at `data/creditcard.csv` and run `python train_model.py`.")
    st.stop()

uploaded_file = st.file_uploader("Upload transaction data (CSV)", type=["csv"])
if uploaded_file is not None:
    transactions = pd.read_csv(uploaded_file)
    missing = [column for column in FEATURE_COLUMNS if column not in transactions.columns]

    if missing:
        st.error(f"CSV is missing required model inputs: {', '.join(missing)}")
    elif transactions.empty:
        st.error("The uploaded CSV contains no transaction rows.")
    else:
        model = joblib.load(MODEL_PATH)
        probabilities = model.predict_proba(transactions[FEATURE_COLUMNS])[:, 1]
        results = transactions.copy()
        results["Fraud probability"] = probabilities
        results["Predicted fraud"] = probabilities >= threshold

        st.metric("Transactions scored", len(results))
        st.dataframe(results, use_container_width=True)
        st.download_button(
            "Download predictions",
            data=results.to_csv(index=False).encode("utf-8"),
            file_name="fraud_predictions.csv",
            mime="text/csv",
        )
