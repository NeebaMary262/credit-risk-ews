from rest_framework import serializers
from .models import LoanApplication

class LoanApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplication
        fields = '__all__'
        # The user cannot submit these; our backend ML model generates them
        read_only_fields = ['risk_score', 'is_high_risk']