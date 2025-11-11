from django.shortcuts import render

# Create your views here.
# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from rest_framework import viewsets
from .models import User, Activity, TimeSlot, Enrollment
from .serializers import UserSerializer, ActivitySerializer, TimeSlotSerializer, EnrollmentSerializer
from . import permissions
from rest_framework.permissions import IsAuthenticated
from zoneinfo import ZoneInfo
from django.utils import timezone
from rest_framework.decorators import action
from datetime import datetime, time, timedelta


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Esta vista solo permite 'leer' (listar y ver) usuarios. No permite crearlos ni borrarlos.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class ActivityViewSet(viewsets.ModelViewSet):
    """
    - Todos pueden LEER.
    - Solo Profesores/Admins pueden CREAR.
    - Solo el 'dueño' o Admin puede MODIFICAR/BORRAR.
    """
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsOwnerOrStaffReadOnly]

    def perform_create(self, serializer):
        """
        Asigna automáticamente al usuario (profesor) que hace la petición
        como el 'owner' de la nueva actividad.
        """
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def create_bulk_slots(self, request, pk=None):
        """
        Crea convocatorias (TimeSlots) en masa para esta actividad.

        Espera un JSON con:
        {
            "start_date": "2025-11-01",
            "end_date": "2025-11-30",
            "start_time": "14:00",
            "end_time": "15:00",
            "weekdays": [0, 2, 4] 
        }
        Donde weekdays: 0=Lunes, 1=Martes, ..., 6=Domingo
        """
        try:
            activity = self.get_object() # Obtiene la actividad (ej. /api/activities/1/...)

            # 1. Leer y validar los datos de entrada
            data = request.data
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            start_time = datetime.strptime(data['start_time'], '%H:%M').time()
            end_time = datetime.strptime(data['end_time'], '%H:%M').time()
            weekdays = data['weekdays'] # Lista de enteros [0, 1, 2, 3, 4, 5, 6]

            if not weekdays:
                return Response({'error': 'La lista de "weekdays" no puede estar vacía.'}, status=status.HTTP_400_BAD_REQUEST)

            # 2. Bucle para crear las convocatorias
            current_date = start_date
            slots_created = []

            while current_date <= end_date:
                # Comprobamos si el día de la semana está en nuestra lista
                if current_date.weekday() in weekdays:
                    # Creamos los objetos datetime en UTC
                    # (Asumimos que las horas recibidas son UTC, como dice el requisito)
                    slot_start_datetime_utc = timezone.make_aware(
                        datetime.combine(current_date, start_time), 
                        timezone.utc
                    )
                    slot_end_datetime_utc = timezone.make_aware(
                        datetime.combine(current_date, end_time), 
                        timezone.utc
                    )

                    # Creamos la convocatoria en la BBDD
                    slot = TimeSlot.objects.create(
                        activity=activity,
                        start_time=slot_start_datetime_utc,
                        end_time=slot_end_datetime_utc
                    )
                    slots_created.append(TimeSlotSerializer(slot).data)

                # Avanzamos al siguiente día
                current_date += timedelta(days=1)

            return Response(
                {'message': f'{len(slots_created)} convocatorias creadas con éxito.', 'slots': slots_created},
                status=status.HTTP_201_CREATED
            )

        except KeyError as e:
            return Response({'error': f'Falta el campo requerido: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Ha ocurrido un error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


class TimeSlotViewSet(viewsets.ModelViewSet):
    """
    Los permisos de TimeSlot se heredan de su Actividad.
    Usamos el mismo permiso.
    (Necesitaremos ajustar el modelo TimeSlot para que tenga un 'owner'
    o comprobar el 'owner' de la actividad padre).

    Por ahora, usaremos este permiso, pero lo ajustaremos.
    """
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    # De momento, solo profesores/admins pueden gestionar convocatorias.
    permission_classes = [permissions.IsStaffUser]


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    - Alumnos solo pueden crear (inscribirse) y borrar sus propias inscripciones.
    - Profesores/Admins pueden ver y gestionar todas las inscripciones.
    """
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]


class EdxLoginView(APIView):
    """
    Vista personalizada para loguear o crear un usuario
    con su edx_user_id y email.
    """
    # Como este es el endpoint de login, no debe de estar protegido.
    permission_classes = [] 
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        edx_id = request.data.get('edx_user_id')
        email = request.data.get('email')
        timezone = request.data.get('timezone')

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
                'is_active': True,
                'timezone': timezone or ''
            }
        )

        if not created and timezone and user.timezone != timezone:
            user.timezone = timezone
            # Guardamos solo ese campo para ser eficientes
            user.save(update_fields=['timezone'])

        # Generamos los tokens JWT para este usuario
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'created': created,
            'user': {
                'id': user.id,
                'email': user.email,
                'edx_user_id': user.edx_user_id,
                'timezone': user.timezone,
            }
        })