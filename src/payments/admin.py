from django.contrib import admin

from .models import Payments


@admin.register(Payments)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_id', 'doctor_id', 'title', 'price')
