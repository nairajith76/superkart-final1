"""
Flask backend for the SuperKart Product-Store Sales Forecast model.

Endpoints
---------
GET  /            -> simple liveness message
GET  /health       -> health check (used by Docker/monitoring)
POST /predict      -> single-record prediction (JSON body)
POST /predict_batch -> batch prediction (CSV file upload), returns a CSV of predictions
"""

import io

import joblib
import pandas as pd
from flask import Flask, jsonify, request, send_file

app = Flask(__name__)

MODEL_PATH = "superkart_best_model.joblib"
model = joblib.load(MODEL_PATH)

# The exact feature columns / order the model pipeline was trained on
FEATURE_COLUMNS = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "SuperKart Sales Prediction API is up and running."})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/predict", methods=["POST"])
def predict():
    """Single-record prediction. Expects a JSON body with all FEATURE_COLUMNS as keys."""
    try:
        payload = request.get_json(force=True)
        if payload is None:
            return jsonify({"error": "Request body must be valid JSON."}), 400

        missing = [c for c in FEATURE_COLUMNS if c not in payload]
        if missing:
            return jsonify({"error": f"Missing required fields: {missing}"}), 400

        input_df = pd.DataFrame([payload])[FEATURE_COLUMNS]
        prediction = model.predict(input_df)[0]

        return jsonify({"Product_Store_Sales_Total_Prediction": float(prediction)})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 500


@app.route("/predict_batch", methods=["POST"])
def predict_batch():
    """Batch prediction. Expects a CSV file uploaded under the form field 'file',
    with the FEATURE_COLUMNS present as columns. Returns a CSV with an added
    Product_Store_Sales_Total_Prediction column."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part named 'file' in the request."}), 400

        file = request.files["file"]
        input_df = pd.read_csv(file)

        missing = [c for c in FEATURE_COLUMNS if c not in input_df.columns]
        if missing:
            return jsonify({"error": f"Missing required columns: {missing}"}), 400

        predictions = model.predict(input_df[FEATURE_COLUMNS])
        input_df["Product_Store_Sales_Total_Prediction"] = predictions

        buffer = io.StringIO()
        input_df.to_csv(buffer, index=False)
        buffer.seek(0)

        return send_file(
            io.BytesIO(buffer.getvalue().encode()),
            mimetype="text/csv",
            as_attachment=True,
            download_name="superkart_batch_predictions.csv",
        )
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
