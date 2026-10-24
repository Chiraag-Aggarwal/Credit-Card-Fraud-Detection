# Credit Card Fraud Detection

A small, end-to-end machine-learning project for detecting potentially fraudulent credit-card transactions. It trains a class-weighted logistic-regression model on the Kaggle credit-card transactions dataset and provides a Streamlit interface for scoring CSV files.

## Requirements

- Python 3.10 or newer
- The `creditcard.csv` dataset from [Kaggle: Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)

The dataset is not included in this repository. Download it from Kaggle and place it at `data/creditcard.csv`.

## Set up and train

In PowerShell, from the project directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python train_model.py
```

Training writes the fitted pipeline to `models/fraud_detection_model.joblib` and evaluation metrics to `models/metrics.json`. The script uses a stratified train/test split and reports precision, recall, F1, ROC-AUC, average precision, and the confusion matrix. Because fraud is rare, review recall and precision rather than relying on accuracy alone.

## Run the app

```powershell
streamlit run app.py
```

Upload a CSV containing the model input columns (`Time`, `V1` through `V28`, and `Amount`). The app displays the predicted fraud probability and a classification at the selected probability threshold. Additional columns are preserved in the results.

## Project files

- `train_model.py` — data validation, model training, and evaluation
- `app.py` — Streamlit prediction interface
- `test_train_model.py` — focused tests for the model pipeline
- `requirements.txt` — Python dependencies

## Notes

The provided threshold is a configurable starting point, not a production decision policy. Tune it against validation data and the costs of false positives and missed fraud before using a model to make real-world decisions. Do not upload real cardholder data to a deployment unless the service and its data-handling practices are approved for that use.
