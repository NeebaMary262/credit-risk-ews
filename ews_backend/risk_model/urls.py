
from django.urls import path
from . import views
from .views import PredictRiskView # Import the class

urlpatterns = [
    # 🚨 Updated mapping for the Single Application Class View
    path('predict/', PredictRiskView.as_view(), name='predict'),
    
    # Existing routes for Bulk functionality
    path('upload-csv/', views.bulk_upload_to_kafka, name='upload_csv'),
    path('check-batch/', views.check_batch_status, name='check_batch_status'),
    path('download-csv/', views.download_pytorch_csv, name='download_csv'),
]