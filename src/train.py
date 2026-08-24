import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from preprocessing import DataPreprocessor

def train_model():
    # 1. Define exact Windows absolute paths
    raw_data_path = r"D:\credit_risk_ews\data\credit_risk_dataset.csv\credit_risk_dataset.csv" 
    artifacts_dir = r"D:\credit_risk_ews\artifacts"
    
    # 2. Initialize the preprocessor and get the cleaned, split data
    print("Starting data preprocessing...")
    preprocessor = DataPreprocessor(raw_data_path=raw_data_path, artifacts_dir=artifacts_dir)
    X_train, X_test, y_train, y_test = preprocessor.process_and_split()

    # 3. Train the Random Forest Classifier
    print("Training the Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        class_weight="balanced", # Helps with imbalanced default data
        random_state=42
    )
    model.fit(X_train, y_train)

    # 4. Evaluate the model's accuracy
    print("Evaluating model performance...")
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print(f"ROC-AUC Score: {roc_auc_score(y_test, y_prob):.4f}")

    # 5. Save the trained model next to your preprocessor artifacts
    model_path = os.path.join(artifacts_dir, "risk_model.pkl")
    joblib.dump(model, model_path)
    print(f"\nSuccess! Model saved to {model_path}")

if __name__ == "__main__":
    train_model()