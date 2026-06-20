import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, roc_curve
import joblib

def main():
    print("=" * 60)
    print("CUSTOMER CHURN MODEL TRAINING & EXPORT")
    print("=" * 60)

    # 1. Load dataset
    data_path = 'customer_churn_data.csv'
    if not os.path.exists(data_path):
        data_path = os.path.join(os.path.dirname(__file__), 'customer_churn_data.csv')
    
    print(f"Loading dataset from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")

    # 2. Data Preprocessing
    print("\nProcessing data...")
    # Drop customerID
    df_processed = df.drop(columns=['customerID'])
    # Map Churn to numeric explicitly
    df_processed['Churn'] = df_processed['Churn'].map({'Yes': 1, 'No': 0}).astype(int)
    # Parse TotalCharges as numeric and fill missing values with the median
    df_processed['TotalCharges'] = pd.to_numeric(df_processed['TotalCharges'], errors='coerce')
    median_charges = df_processed['TotalCharges'].median()
    df_processed['TotalCharges'] = df_processed['TotalCharges'].fillna(median_charges)

    # Identify feature types
    cat_features = df_processed.select_dtypes(include=['object']).columns.tolist()
    num_features = df_processed.select_dtypes(include=['int64', 'float64']).columns.tolist()
    if 'Churn' in num_features:
        num_features.remove('Churn')

    print(f"✓ Categorical features: {len(cat_features)}")
    print(f"✓ Numerical features: {len(num_features)}")

    # 3. Train/Test Split (80/20 Stratified)
    X = df_processed[cat_features + num_features]
    y = df_processed['Churn']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"✓ Train/Test split: {X_train.shape[0]} train samples, {X_test.shape[0]} test samples")

    # 4. Preprocessing Pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_features),
            ('num', StandardScaler(), num_features)
        ]
    )

    # 5. Define Models
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
    }

    # 6. Train and Evaluate
    best_roc_auc = -1.0
    best_model_name = None
    best_pipeline = None
    test_results = {}

    plt.figure(figsize=(10, 8))
    sns.set_theme(style="whitegrid")

    for name, model in models.items():
        print(f"\nTraining model: {name}...")
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', model)
        ])
        
        # Fit model
        pipeline.fit(X_train, y_train)

        # Predict
        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]

        # Calculate metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)

        test_results[name] = {
            'Accuracy': acc,
            'Precision': prec,
            'Recall': rec,
            'F1 Score': f1,
            'ROC-AUC': auc
        }

        print(f"  Accuracy:  {acc:.4f}")
        print(f"  Precision: {prec:.4f}")
        print(f"  Recall:    {rec:.4f}")
        print(f"  F1 Score:  {f1:.4f}")
        print(f"  ROC-AUC:   {auc:.4f}")

        # Track best model based on ROC-AUC
        if auc > best_roc_auc:
            best_roc_auc = auc
            best_model_name = name
            best_pipeline = pipeline

        # Plot ROC Curve
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        plt.plot(fpr, tpr, label=f"{name} (AUC = {auc:.4f})")

    # Plot baseline
    plt.plot([0, 1], [0, 1], 'k--', label='Baseline (AUC = 0.5000)')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC) Curves')
    plt.legend(loc='lower right')
    
    # Save ROC Comparison plot
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plot_path = os.path.join(script_dir, 'static', 'models_performance_comparison.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"\n✓ Saved ROC Curves comparison plot to: {plot_path}")

    # 7. Export Best Pipeline
    model_export_path = os.path.join(script_dir, 'churn_model_pipeline.joblib')
    print(f"\n🏆 Best model identified: {best_model_name} with ROC-AUC of {best_roc_auc:.4f}")
    print(f"Saving the complete pipeline to: {model_export_path}")
    
    # Save pipeline
    joblib.dump(best_pipeline, model_export_path)
    print("✓ Model pipeline successfully saved!")
    print("=" * 60)

if __name__ == '__main__':
    main()
