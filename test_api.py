import requests

# 1. The exact URL of your API
url = 'http://127.0.0.1:8000/api/predict/'

# 2. A dummy loan application matching your Kaggle data
dummy_application = {
    "person_age": 28,
    "person_income": 65000,
    "person_home_ownership": "RENT",
    "person_emp_length": 5.0,
    "loan_intent": "EDUCATION",
    "loan_grade": "B",
    "loan_amnt": 15000,
    "loan_int_rate": 10.5,
    "loan_percent_income": 0.23,
    "cb_person_default_on_file": "N",
    "cb_person_cred_hist_length": 4
}

# 3. Send the POST request with the JSON payload
print("Sending application to the API...")
response = requests.post(url, json=dummy_application)

# 4. Print the API's decision
print(f"Status Code: {response.status_code}")
print("Response from Server:")
print(response.json())