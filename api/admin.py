# api/admin.py

from django.contrib import admin
from .models import User, Activity, ActivityFile, TimeSlot, Enrollment

# Registramos cada modelo para que aparezca en el panel de admin
admin.site.register(User)
admin.site.register(Activity)
admin.site.register(ActivityFile)
admin.site.register(TimeSlot)
admin.site.register(Enrollment)