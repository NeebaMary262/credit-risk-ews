from kafka import KafkaProducer
import json

# Connect to Kafka
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# 🚨 THE MESSY DATA 🚨
bad_application = {
    "person_age": 20,                
    "person_income": 25000,
    "person_home_ownership": "RENT",
    "person_emp_length": None,       # MISSING! (Should become 0 for a 20yo)
    "loan_intent": "EDUCATION",
    "loan_grade": "C",               
    "loan_amnt": 5000,
    "loan_int_rate": None,           # MISSING! (Should become 13.5 for Grade C)
    "loan_percent_income": 0.20,
    "cb_person_default_on_file": "", # BLANK! (Should default to 'N')
    "cb_person_cred_hist_length": 10 # IMPOSSIBLE! (A 20yo cannot have a 10yr history. Should cap at 2)
}

producer.send('loan_applications', bad_application)
producer.flush()

print("Sent 1 severely broken application to Kafka!")