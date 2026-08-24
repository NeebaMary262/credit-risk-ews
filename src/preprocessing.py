import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os


class DataPreprocessor:
    """Handles data cleaning, feature engineering, and preprocessing for Credit Risk data."""
    
    def __init__(self, raw_data_path: str, artifacts_dir: str = "artifacts"):
        self.raw_data_path = raw_data_path
        self.artifacts_dir = artifacts_dir
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
        os.makedirs(self.artifacts_dir, exist_ok=True)
    
    def load_data(self) -> pd.DataFrame:
        """Loads dataset from path."""
        if not os.path.exists(self.raw_data_path):
            raise FileNotFoundError(f"Data file not found at: {self.raw_data_path}")
        # 1. Load the CSV into a DataFrame
        df = pd.read_csv(self.raw_data_path)
        
        # 2. Print a preview to the terminal so you can verify it worked
        print("\n--- Successfully loaded the CSV! Here is df.head(): ---")
        print(df.head())
        print("------------------------------------------------------\n")
        
        # 3. Return the DataFrame so the rest of the pipeline can use it
        return df
        # return pd.read_csv(self.raw_data_path)
        
    
    def clean_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Removes realistic data errors common in the Kaggle Credit Risk dataset."""
        df = df.copy()
        
        # Remove impossible ages (e.g., person_age > 100)
        df = df[df["person_age"] <= 100]
        
        # Remove impossible employment lengths (e.g., employment > 60 years)
        df = df[df["person_emp_length"] <= 60]
        
        return df
   
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Imputes missing values with medians."""
        df = df.copy()
        
        # Fill missing employment length with median
        emp_median = df["person_emp_length"].median()
        df["person_emp_length"] = df["person_emp_length"].fillna(emp_median)
        
        # Fill missing interest rate with median
        rate_median = df["loan_int_rate"].median()
        df["loan_int_rate"] = df["loan_int_rate"].fillna(rate_median)
        
        return df

    def encode_categorical_features(self, df: pd.DataFrame, is_training: bool = True) -> pd.DataFrame:
        """Encodes string columns to numbers."""
        df = df.copy()
        cat_cols = ["person_home_ownership", "loan_intent", "loan_grade", "cb_person_default_on_file"]

        for col in cat_cols:
            if is_training:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col])
                self.label_encoders[col] = le
            else:
                le = self.label_encoders[col]
                df[col] = le.transform(df[col])
                
        return df

    def process_and_split(self, test_size: float = 0.2, random_state: int = 42):
        """Full pipeline execution returning train/test split data."""
        df = self.load_data()
        df = self.clean_anomalies(df)
        df = self.handle_missing_values(df)
        df = self.encode_categorical_features(df, is_training=True)

        # Target variable: loan_status (1 = Default/High Risk, 0 = Non-Default)
        X = df.drop(columns=["loan_status"])
        y = df["loan_status"]

        # Stratified split to preserve target class balance
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Save transformers for inference in Django
        joblib.dump(self.scaler, os.path.join(self.artifacts_dir, "scaler.pkl"))
        joblib.dump(self.label_encoders, os.path.join(self.artifacts_dir, "encoders.pkl"))
        joblib.dump(list(X.columns), os.path.join(self.artifacts_dir, "feature_names.pkl"))

        print(f"Data preprocessing complete. Features shape: {X_train_scaled.shape}")
        return X_train_scaled, X_test_scaled, y_train, y_test