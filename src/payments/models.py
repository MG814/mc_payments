from django.db import models


class Payments(models.Model):
    patient_id = models.IntegerField()
    doctor_id = models.IntegerField()
    title = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
