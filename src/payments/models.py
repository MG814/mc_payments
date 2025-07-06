from django.db import models


class Payments(models.Model):
    patient_id = models.IntegerField()
    doctor_id = models.IntegerField()
    title = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_session_id = models.CharField(max_length=255, null=True, blank=True)
    visit_id = models.IntegerField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
