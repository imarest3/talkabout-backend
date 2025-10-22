# api/serializers.py

from rest_framework import serializers
from .models import User, Activity, ActivityFile, TimeSlot, Enrollment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Campos que queremos exponer en la API
        fields = ['id', 'username', 'email', 'edx_user_id', 'timezone']


class ActivityFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityFile
        fields = ['id', 'name', 'url']


class ActivitySerializer(serializers.ModelSerializer):
    # 'files' es el 'related_name' que definimos en el modelo ActivityFile
    # 'many=True' significa que una actividad puede tener muchos archivos.
    # 'read_only=True' significa que se mostrarán, pero no se podrán crear desde aquí.
    files = ActivityFileSerializer(many=True, read_only=True)

    class Meta:
        model = Activity
        fields = ['id', 'title', 'description', 'max_participants', 'created_at', 'files']


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'activity', 'start_time', 'end_time']


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'user', 'timeslot', 'attended', 'enrolled_at']