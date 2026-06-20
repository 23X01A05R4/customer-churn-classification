import os
import sys
import pandas as pd
import joblib

def main():
    # Load pipeline
    model_path = 'churn_model_pipeline.joblib'
    if not os.path.exists(model_path):
        model_path = os.path.join(os.path.dirname(__file__), 'churn_model_pipeline.joblib')
        
    if not os.path.exists(model_path):
        print(f"Error: Model file '{model_path}' not found. Please train the model first by running train.py.")
        sys.exit(1)
        
    try:
        pipeline = joblib.load(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)
        
    print("=" * 60)
    print("           CUSTOMER CHURN INTERACTIVE PREDICTOR CLI     ")
    print("=" * 60)
    print("Model loaded successfully.")
    
    # Run loop
    while True:
        # Default customer features matching the column structure
        custom_data = {
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
        
        print("\nEnter customer details below (or press ENTER to use default values):")
        try:
            tenure_in = input(f"1. Tenure in months (Default: {custom_data['tenure']}): ")
            if tenure_in.strip():
                custom_data['tenure'] = int(tenure_in)
                
            monthly_in = input(f"2. Monthly Charges in $ (Default: {custom_data['MonthlyCharges']}): ")
            if monthly_in.strip():
                custom_data['MonthlyCharges'] = float(monthly_in)
                
            contract_in = input(f"3. Contract [Month-to-month, One year, Two year] (Default: {custom_data['Contract']}): ")
            if contract_in.strip() in ['Month-to-month', 'One year', 'Two year']:
                custom_data['Contract'] = contract_in
                
            custom_data['TotalCharges'] = custom_data['tenure'] * custom_data['MonthlyCharges']
        except ValueError:
            print("\n[Error] Invalid input format. Using default values.")
            
        # Convert to DF
        input_df = pd.DataFrame([custom_data])
        
        # Predict
        try:
            prediction = pipeline.predict(input_df)[0]
            probability = pipeline.predict_proba(input_df)[0][1]
            
            print("-" * 50)
            print("PREDICTION RESULT:")
            print("-" * 50)
            if prediction == 1:
                print(f"⚠️  HIGH RISK: Customer is LIKELY TO CHURN.")
                print(f"Churn Probability: {probability:.2%}")
            else:
                print(f"✅  SAFE: Customer is LIKELY TO STAY.")
                print(f"Churn Probability: {probability:.2%}")
            print("-" * 50)
        except Exception as e:
            print(f"Prediction failed: {e}")
            
        choice = input("\nDo you want to predict another customer? (y/n, Default: y): ")
        if choice.strip().lower() == 'n':
            print("Goodbye!")
            break

if __name__ == '__main__':
    main()
