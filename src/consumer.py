import os
import json
import math
import joblib
import pandas as pd
import torch
import torch.nn as nn
from kafka import KafkaConsumer
from dotenv import load_dotenv
import pg8000.dbapi 

load_dotenv()

# 🚨 THIS IS WHAT WAS MISSING: The PyTorch Model & Artifacts 🚨
class RiskNet(nn.Module):
    def __init__(self, input_size):
        super(RiskNet, self).__init__()
        self.layer1 = nn.Linear(input_size, 16)
        self.relu = nn.ReLU()
        self.output = nn.Linear(16, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.layer1(x)
        x = self.relu(x)
        x = self.output(x)
        return self.sigmoid(x)

# Load artifacts (Update paths if your files are in a folder like 'artifacts/')
# Load artifacts from the artifacts folder
import os

# --- AWS-READY DYNAMIC PATHING ---
# 1. Get the exact folder where consumer.py lives (the 'src' folder)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Go up one level to the project root, then into the 'artifacts' folder
ARTIFACTS_DIR = os.path.join(CURRENT_DIR, '..', 'artifacts')

# 3. Load all files safely using os.path.join (Works on Windows \ and AWS Linux /)
encoders = joblib.load(os.path.join(ARTIFACTS_DIR, 'encoders.pkl'))
scaler = joblib.load(os.path.join(ARTIFACTS_DIR, 'scaler.pkl'))
feature_names = joblib.load(os.path.join(ARTIFACTS_DIR, 'feature_names.pkl'))

model = RiskNet(len(feature_names))

# Change this line:
model.load_state_dict(torch.load(os.path.join(ARTIFACTS_DIR, 'pytorch_risk_model.pth')))

# To this:
model.load_state_dict(torch.load(os.path.join(ARTIFACTS_DIR, 'pytorch_risk_model.pth'), weights_only=True))
model.eval()





# -------------------------------------------------------------

# --- 2. DATABASE CONNECTION ---
db_conn = pg8000.dbapi.connect(
    database=os.getenv('DB_NAME', 'credit_risk_db'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST', 'localhost'),
    port=int(os.getenv('DB_PORT', 5432)) # pg8000 requires port as an integer
)
cursor = db_conn.cursor()


# --- 3. DATA FIREWALL ---
def clean_and_impute_data(data):
    for key, value in data.items():
        if isinstance(value, float) and math.isnan(value):
            data[key] = None

    age = int(data.get('person_age') or 18)
    max_possible_history = max(0, age - 18)
    
    current_history = int(data.get('cb_person_cred_hist_length') or 0)
    if current_history > max_possible_history:
        data['cb_person_cred_hist_length'] = max_possible_history
    elif data.get('cb_person_cred_hist_length') is None:
        data['cb_person_cred_hist_length'] = min(5, max_possible_history)

    if data.get('person_emp_length') is None or data.get('person_emp_length') == '':
        data['person_emp_length'] = 0 if age < 22 else (3 if age < 30 else 7)

    grade_rates = {'A': 6.5, 'B': 9.5, 'C': 13.5, 'D': 16.5, 'E': 19.5, 'F': 22.5, 'G': 25.5}
    if data.get('loan_int_rate') is None or data.get('loan_int_rate') == '':
        grade = data.get('loan_grade', 'B')
        data['loan_int_rate'] = grade_rates.get(grade, 11.0)

    if data.get('cb_person_default_on_file') is None or data.get('cb_person_default_on_file') == '':
        data['cb_person_default_on_file'] = 'N'

    if data.get('person_income') is None: data['person_income'] = 45000
    if data.get('loan_amnt') is None: data['loan_amnt'] = 5000
    if data.get('loan_percent_income') is None: 
        data['loan_percent_income'] = round(float(data['loan_amnt']) / float(data['person_income']), 2)

    return data

# --- 4. KAFKA INGESTION & PYTORCH INFERENCE ---
consumer = KafkaConsumer(
    'loan_applications',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    group_id='pytorch_production_group',
    auto_offset_reset='latest'
)

print("PyTorch Consumer running. Processing Kafka messages into PostgreSQL...")

for message in consumer:
    raw_data = message.value
    clean_app = clean_and_impute_data(raw_data)
    
    # Extract the shared identifier
    batch_identifier = clean_app.get('batch_id', 'UNKNOWN_BATCH')

    # Formatting for PyTorch
    df = pd.DataFrame([clean_app])
    for col in ["person_home_ownership", "loan_intent", "loan_grade", "cb_person_default_on_file"]:
        df[col] = encoders[col].transform(df[col])

    df_scaled = scaler.transform(df[feature_names])
    input_tensor = torch.tensor(df_scaled, dtype=torch.float32)

    with torch.no_grad():
        score = model(input_tensor).item()

    decision = "HIGH RISK - REJECT" if score > 0.5 else "LOW RISK - APPROVE"

    # Insert into Table 2 using pg8000
    cursor.execute("""
        INSERT INTO risk_model_pytorchbulkresult 
        (batch_id, person_age, person_income, loan_amnt, loan_intent, pytorch_risk_score, decision, processed_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
    """, (
        batch_identifier,
        clean_app['person_age'],
        clean_app['person_income'],
        clean_app['loan_amnt'],
        clean_app.get('loan_intent', 'PERSONAL'),
        score,
        decision
    ))
    db_conn.commit()

    print(f"Stored PyTorch Prediction [{batch_identifier}] -> Score: {score:.4f} | Decision: {decision}")
    # import json
# import requests
# import math
# from kafka import KafkaConsumer

# def clean_and_impute_data(data):
#     """
#     The Data Firewall: Cleans messy Kafka data using logical rules 
#     and simulates KNN demographic grouping for missing values.
#     """
#     # --- NEW: NaN SANITIZER ---
#     # Convert 'NaN' (Not a Number) to standard Python 'None'
#     for key, value in data.items():
#         if isinstance(value, float) and math.isnan(value):
#             data[key] = None

#     # 1. LOGICAL RULE: Credit history cannot be mathematically older than Age - 18
#     # (Using 'or' handles cases where age or history might still be None)
#     age = int(data.get('person_age') or 18)
#     max_possible_history = max(0, age - 18)
    
#     current_history = int(data.get('cb_person_cred_hist_length') or 0)
#     if current_history > max_possible_history:
#         data['cb_person_cred_hist_length'] = max_possible_history
#     elif data.get('cb_person_cred_hist_length') is None:
#         data['cb_person_cred_hist_length'] = min(5, max_possible_history)

#     # 2. KNN SIMULATION: Demographic Grouping for Missing Employment Length
#     if data.get('person_emp_length') is None or data.get('person_emp_length') == '':
#         if age < 22:
#             data['person_emp_length'] = 0  # Student demographic
#         elif age < 30:
#             data['person_emp_length'] = 3  # Early career demographic
#         else:
#             data['person_emp_length'] = 7  # Mid-career demographic

#     # 3. DOMAIN LOGIC: Missing Interest Rate defaults to the Grade Average
#     grade_rates = {'A': 6.5, 'B': 9.5, 'C': 13.5, 'D': 16.5, 'E': 19.5, 'F': 22.5, 'G': 25.5}
#     if data.get('loan_int_rate') is None or data.get('loan_int_rate') == '':
#         grade = data.get('loan_grade', 'B')
#         data['loan_int_rate'] = grade_rates.get(grade, 11.0)

#     # 4. SAFETY RULE: Missing Default status always assumes 'No'
#     if data.get('cb_person_default_on_file') is None or data.get('cb_person_default_on_file') == '':
#         data['cb_person_default_on_file'] = 'N'

#     # Catch any remaining None values for numerical fields to prevent crashes
#     if data.get('person_income') is None: data['person_income'] = 45000
#     if data.get('loan_amnt') is None: data['loan_amnt'] = 5000
#     if data.get('loan_percent_income') is None: 
#         data['loan_percent_income'] = round(data['loan_amnt'] / data['person_income'], 2)

#     return data


# # --- KAFKA CONSUMER SETUP ---
# # --- KAFKA CONSUMER SETUP ---
# consumer = KafkaConsumer(
#     'loan_applications',
#     bootstrap_servers=['localhost:9092'],
#     value_deserializer=lambda x: json.loads(x.decode('utf-8')),
#     group_id='fresh_test_group',       # NEW: Creates a brand new identity
#     auto_offset_reset='latest'         # CHANGED: Ignores the past, only reads new data
# )

# print("Consumer started. Acting as Data Firewall and sending to AI...")

# for message in consumer:
#     raw_application = message.value
#     clean_application = clean_and_impute_data(raw_application)
    
#     try:
#         response = requests.post('http://127.0.0.1:8000/api/predict/', json=clean_application)
        
#         # Django DRF returns 201 (Created) for a successful POST request!
#         if response.status_code in [200, 201]:
#             result = response.json()
#             print(f"Success: {result['status']} | Score: {result['risk_score']}")
#         else:
#             print(f"Django Rejected Payload: {response.status_code} - {response.text}")
            
#     except requests.exceptions.ConnectionError:
#         print("Error: Could not connect to Django. Is the server running?")