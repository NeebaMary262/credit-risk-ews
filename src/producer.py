import pandas as pd
from kafka import KafkaProducer
import json
import time

# 1. Connect to the Kafka container running in Docker
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    # This automatically converts our Python data into JSON format for the network
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

topic_name = 'loan_applications'

# 2. Load your original CSV dataset

# producer.py

csv_file_path = r"D:\credit_risk_ews\data\credit_risk_dataset.csv\credit_risk_dataset.csv" 
print(f"Loading data from {csv_file_path}...")
df = pd.read_csv(csv_file_path)

# ADD THIS LINE: Drop any rows with missing data (NaNs)
df = df.dropna()

print("Starting the real-time data stream...")
# ... rest of the code remains the same

# 3. Loop through the CSV and stream it to Kafka line-by-line
print("Starting the real-time data stream...")
for index, row in df.head(100).iterrows(): # We use .head(100) just to test the first 100 rows
    
    # Convert the pandas row into a clean Python dictionary
    application = row.to_dict()
    
    # Fire the data into the Kafka topic
    producer.send(topic_name, application)
    
    print(f"Sent Application {index} to Kafka")
    
    # Pause for 2 seconds between each row to simulate real human traffic
    time.sleep(2)

print("Test streaming complete!")