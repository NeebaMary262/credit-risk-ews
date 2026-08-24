from django.db import models

# Create your models here.


class LoanApplication(models.Model):
    # Applicant Background
    person_age = models.IntegerField()
    person_income = models.IntegerField()
    person_home_ownership = models.CharField(max_length=20)
    person_emp_length = models.FloatField()
    
    # Loan Details
    loan_intent = models.CharField(max_length=50)
    loan_grade = models.CharField(max_length=10)
    loan_amnt = models.IntegerField()
    loan_int_rate = models.FloatField()
    loan_percent_income = models.FloatField()
    
    # Credit History
    cb_person_default_on_file = models.CharField(max_length=1)
    cb_person_cred_hist_length = models.IntegerField()
    
    # Machine Learning Outputs (Generated automatically)
    risk_score = models.FloatField(null=True, blank=True)
    is_high_risk = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application {self.id} - Risk: {self.risk_score}"
