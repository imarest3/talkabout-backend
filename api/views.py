from django.shortcuts import render

# Create your views here.
# api/views.py
# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

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


class EdxLoginView(APIView):
    """
    Vista personalizada para loguear o crear un usuario
    con su edx_user_id y email.
    """
    # Como este es el endpoint de login, no debe estar protegido.
    permission_classes = [] 
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        edx_id = request.data.get('edx_user_id')
        email = request.data.get('email')

        if not edx_id or not email:
            return Response(
                {'error': 'edx_user_id y email son requeridos.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Usamos get_or_create para buscar o crear al usuario
        user, created = User.objects.get_or_create(
            edx_user_id=edx_id,
            defaults={
                'email': email,
                # Usamos el edx_id como username, ya que es único
                'username': edx_id, 
                'is_active': True
            }
        )

        # Generamos los tokens JWT para este usuario
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'created': created
        })