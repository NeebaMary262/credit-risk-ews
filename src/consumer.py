import json
import requests
import math
from kafka import KafkaConsumer

def clean_and_impute_data(data):
    """
    The Data Firewall: Cleans messy Kafka data using logical rules 
    and simulates KNN demographic grouping for missing values.
    """
    # --- NEW: NaN SANITIZER ---
    # Convert 'NaN' (Not a Number) to standard Python 'None'
    for key, value in data.items():
        if isinstance(value, float) and math.isnan(value):
            data[key] = None

    # 1. LOGICAL RULE: Credit history cannot be mathematically older than Age - 18
    # (Using 'or' handles cases where age or history might still be None)
    age = int(data.get('person_age') or 18)
    max_possible_history = max(0, age - 18)
    
    current_history = int(data.get('cb_person_cred_hist_length') or 0)
    if current_history > max_possible_history:
        data['cb_person_cred_hist_length'] = max_possible_history
    elif data.get('cb_person_cred_hist_length') is None:
        data['cb_person_cred_hist_length'] = min(5, max_possible_history)

    # 2. KNN SIMULATION: Demographic Grouping for Missing Employment Length
    if data.get('person_emp_length') is None or data.get('person_emp_length') == '':
        if age < 22:
            data['person_emp_length'] = 0  # Student demographic
        elif age < 30:
            data['person_emp_length'] = 3  # Early career demographic
        else:
            data['person_emp_length'] = 7  # Mid-career demographic

    # 3. DOMAIN LOGIC: Missing Interest Rate defaults to the Grade Average
    grade_rates = {'A': 6.5, 'B': 9.5, 'C': 13.5, 'D': 16.5, 'E': 19.5, 'F': 22.5, 'G': 25.5}
    if data.get('loan_int_rate') is None or data.get('loan_int_rate') == '':
        grade = data.get('loan_grade', 'B')
        data['loan_int_rate'] = grade_rates.get(grade, 11.0)

    # 4. SAFETY RULE: Missing Default status always assumes 'No'
    if data.get('cb_person_default_on_file') is None or data.get('cb_person_default_on_file') == '':
        data['cb_person_default_on_file'] = 'N'

    # Catch any remaining None values for numerical fields to prevent crashes
    if data.get('person_income') is None: data['person_income'] = 45000
    if data.get('loan_amnt') is None: data['loan_amnt'] = 5000
    if data.get('loan_percent_income') is None: 
        data['loan_percent_income'] = round(data['loan_amnt'] / data['person_income'], 2)

    return data


# --- KAFKA CONSUMER SETUP ---
# --- KAFKA CONSUMER SETUP ---
consumer = KafkaConsumer(
    'loan_applications',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    group_id='fresh_test_group',       # NEW: Creates a brand new identity
    auto_offset_reset='latest'         # CHANGED: Ignores the past, only reads new data
)

print("Consumer started. Acting as Data Firewall and sending to AI...")

for message in consumer:
    raw_application = message.value
    clean_application = clean_and_impute_data(raw_application)
    
    try:
        response = requests.post('http://127.0.0.1:8000/api/predict/', json=clean_application)
        
        # Django DRF returns 201 (Created) for a successful POST request!
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"Success: {result['status']} | Score: {result['risk_score']}")
        else:
            print(f"Django Rejected Payload: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Django. Is the server running?")