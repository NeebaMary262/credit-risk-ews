import os
import joblib
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoanApplicationSerializer
 # or pickle, depending on what you used
from django.conf import settings

# 1. Dynamically find the artifacts folder
artifacts_dir = os.path.join(settings.BASE_DIR, '../artifacts')

# 2. Load all three files safely on both Windows and AWS Linux
model = joblib.load(os.path.join(artifacts_dir, 'risk_model.pkl'))
encoders = joblib.load(os.path.join(artifacts_dir, 'encoders.pkl'))
feature_names = joblib.load(os.path.join(artifacts_dir, 'feature_names.pkl'))


class PredictRiskView(APIView):
    def post(self, request):
        serializer = LoanApplicationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        
        artifacts_dir = os.path.join(settings.BASE_DIR, '../artifacts')

# 2. Load all three files safely on both Windows and AWS Linux
        model = joblib.load(os.path.join(artifacts_dir, 'risk_model.pkl'))
        encoders = joblib.load(os.path.join(artifacts_dir, 'encoders.pkl'))
        feature_names = joblib.load(os.path.join(artifacts_dir, 'feature_names.pkl'))

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
