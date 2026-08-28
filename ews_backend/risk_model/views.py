import os
import csv
import json
import joblib
import pandas as pd
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse

# Django REST Framework Imports
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from kafka import KafkaProducer

# Your Models and Serializers
from .models import LoanApplication, PyTorchBulkResult
from .serializers import LoanApplicationSerializer

# --- 1. LOAD ML ARTIFACTS GLOBALLY (RUNS ONCE ON SERVER START) ---
artifacts_dir = os.path.join(settings.BASE_DIR, '../artifacts')

model = joblib.load(os.path.join(artifacts_dir, 'risk_model.pkl'))
encoders = joblib.load(os.path.join(artifacts_dir, 'encoders.pkl'))
feature_names = joblib.load(os.path.join(artifacts_dir, 'feature_names.pkl'))
scaler = joblib.load(os.path.join(artifacts_dir, 'scaler.pkl')) 

# --- 2. SINGLE APPLICANT PREDICTION (YOUR AWS CODE) ---
class PredictRiskView(APIView):
    def post(self, request):
        serializer = LoanApplicationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        
        df = pd.DataFrame([data])
        for col in ["person_home_ownership", "loan_intent", "loan_grade", "cb_person_default_on_file"]:
            le = encoders[col]
            df[col] = le.transform(df[col])

        df = df[feature_names]
        
        df_scaled = scaler.transform(df)

        risk_score = model.predict_proba(df_scaled)[0][1]
        is_high_risk = bool(risk_score > 0.5)

        application = serializer.save(risk_score=risk_score, is_high_risk=is_high_risk)

        return Response({
            "message": "Application processed successfully",
            "application_id": application.id,
            "risk_score": round(risk_score, 4),
            "status": "HIGH RISK - REJECT" if is_high_risk else "LOW RISK - APPROVE"
        }, status=status.HTTP_201_CREATED)

# --- 3. BULK UPLOAD TO KAFKA ---
@api_view(['POST'])
def bulk_upload_to_kafka(request):
    try:
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    except Exception:
        return Response({"error": "Kafka is offline. Please start Docker."}, status=503)

    file = request.FILES.get('file')
    if not file:
        return Response({"error": "No file uploaded"}, status=400)

    decoded_file = file.read().decode('utf-8').splitlines()
    reader = csv.DictReader(decoded_file)
    
    timeframe_id = datetime.now().strftime("BATCH_%Y%m%d_%H%M%S")

    count = 0
    for row in reader:
        LoanApplication.objects.create(
            batch_id=timeframe_id,
            person_age=int(row.get('person_age') or 0),
            person_income=int(row.get('person_income') or 0),
            person_home_ownership=row.get('person_home_ownership', 'RENT'),
            person_emp_length=float(row.get('person_emp_length') or 0.0),
            loan_intent=row.get('loan_intent', 'PERSONAL'),
            loan_grade=row.get('loan_grade', 'B'),
            loan_amnt=int(row.get('loan_amnt') or 0),
            loan_int_rate=float(row.get('loan_int_rate') or 0.0),
            loan_percent_income=float(row.get('loan_percent_income') or 0.0),
            cb_person_default_on_file=row.get('cb_person_default_on_file', 'N'),
            cb_person_cred_hist_length=int(row.get('cb_person_cred_hist_length') or 0)
        )
        
        row['batch_id'] = timeframe_id
        producer.send('loan_applications', row)
        count += 1

    producer.flush()
    return Response({
        "message": f"Queued {count} applications for PyTorch.",
        "batch_id": timeframe_id,
        "expected_count": count
    })

# --- 4. CHECK BATCH STATUS FOR REACT POLLING ---
@api_view(['GET'])
def check_batch_status(request):
    batch_id = request.GET.get('batch_id')
    expected_count = int(request.GET.get('expected', 0))
    
    actual_count = PyTorchBulkResult.objects.filter(batch_id=batch_id).count()
    
    is_ready = actual_count >= expected_count and expected_count > 0
    return Response({
        "is_ready": is_ready, 
        "processed": actual_count
    })

# --- 5. DOWNLOAD PYTORCH RESULTS ---
@api_view(['GET'])
def download_pytorch_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pytorch_batch_predictions.csv"'

    writer = csv.writer(response)
    writer.writerow(['Batch ID', 'Age', 'Income', 'Loan Amount', 'Intent', 'PyTorch Risk Score', 'Decision', 'Processed At'])

    results = PyTorchBulkResult.objects.all().order_by('-processed_at')
    for item in results:
        writer.writerow([
            item.batch_id,
            item.person_age,
            item.person_income,
            item.loan_amnt,
            item.loan_intent,
            round(item.pytorch_risk_score, 4),
            item.decision,
            item.processed_at.strftime("%Y-%m-%d %H:%M:%S")
        ])

    return response