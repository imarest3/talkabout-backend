from django.shortcuts import render

# Create your views here.
# api/views.py

from rest_framework import viewsets
from .models import User, Activity, TimeSlot, Enrollment
from .serializers import UserSerializer, ActivitySerializer, TimeSlotSerializer, EnrollmentSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Esta vista solo permite 'leer' (listar y ver) usuarios. No permite crearlos ni borrarlos.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ActivityViewSet(viewsets.ModelViewSet):
    """
    Esta vista permite todas las acciones CRUD (Crear, Leer, Actualizar, Borrar)
    para el modelo Activity.
    """
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer


class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
