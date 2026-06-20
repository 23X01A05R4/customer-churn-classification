import os
import sys
import pandas as pd
import joblib
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Locate and load the model pipeline
MODEL_PATH = 'churn_model_pipeline.joblib'
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = os.path.join(os.path.dirname(__file__), 'churn_model_pipeline.joblib')

pipeline = None
if os.path.exists(MODEL_PATH):
    try:
        pipeline = joblib.load(MODEL_PATH)
        print("✓ Model pipeline loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
else:
    print(f"Warning: Model file '{MODEL_PATH}' not found. Please train the model using train.py first.")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if pipeline is None:
        return jsonify({
            'error': 'Model pipeline is not loaded on the server. Please run train.py to train the model.'
        }), 500

    try:
        # Get data from request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Define standard base customer features with defaults
        customer_features = {
            'gender': 'Female',
            'SeniorCitizen': 0,
            'Partner': 'No',
            'Dependents': 'No',
            'tenure': 12,
            'PhoneService': 'Yes',
            'MultipleLines': 'No',
            'InternetService': 'Fiber optic',
            'OnlineSecurity': 'No',
            'OnlineBackup': 'No',
            'DeviceProtection': 'No',
            'TechSupport': 'No',
            'StreamingTV': 'No',
            'StreamingMovies': 'No',
            'Contract': 'Month-to-month',
            'PaperlessBilling': 'Yes',
            'PaymentMethod': 'Electronic check',
            'MonthlyCharges': 75.00,
            'TotalCharges': 900.00
        }

        # Override defaults with values provided by user
        for key in customer_features.keys():
            if key in data:
                if key in ['SeniorCitizen', 'tenure']:
                    customer_features[key] = int(data[key])
                elif key in ['MonthlyCharges', 'TotalCharges']:
                    customer_features[key] = float(data[key])
                else:
                    customer_features[key] = str(data[key])

        # Automatically calculate TotalCharges based on tenure and monthly charges if not explicitly supplied
        if 'TotalCharges' not in data:
            customer_features['TotalCharges'] = customer_features['tenure'] * customer_features['MonthlyCharges']

        # Create 1-row DataFrame
        input_df = pd.DataFrame([customer_features])

        # Run prediction
        prediction = int(pipeline.predict(input_df)[0])
        probability = float(pipeline.predict_proba(input_df)[0][1])

        # Formulate insights and risk levels
        risk_level = "Low"
        if probability >= 0.7:
            risk_level = "Critical"
        elif probability >= 0.5:
            risk_level = "High"
        elif probability >= 0.3:
            risk_level = "Medium"

        return jsonify({
            'churn': prediction,
            'probability': probability,
            'risk_level': risk_level,
            'metrics': {
                'tenure': customer_features['tenure'],
                'MonthlyCharges': customer_features['MonthlyCharges'],
                'Contract': customer_features['Contract']
            }
        })

    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

if __name__ == '__main__':
    # Run server locally on port 5000
    app.run(debug=True, port=5000)
