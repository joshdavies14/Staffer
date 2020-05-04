from django.contrib import admin
from .models import ShiftTemplate, ShiftPreference, Shift

admin.site.register(ShiftTemplate)
admin.site.register(ShiftPreference)
admin.site.register(Shift)