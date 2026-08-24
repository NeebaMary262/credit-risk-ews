from django.urls import path
from .views import PredictRiskView

urlpatterns = [
    # This creates the endpoint: /predict/
    path('predict/', PredictRiskView.as_view(), name='predict_risk'),
]