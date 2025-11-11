# api/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# -------------------------------------------------
# MODELO 1: USUARIO PERSONALIZADO
# -------------------------------------------------
# Extendemos el usuario base de Django para añadir los campos que necesitamos.
class User(AbstractUser):
    edx_user_id = models.CharField(max_length=255, unique=True)
    timezone = models.CharField(max_length=100, blank=True)

    # Sobreescribimos el campo email para que sea obligatorio y único.
    email = models.EmailField(unique=True, blank=False)

    def __str__(self):
        return self.email

# -------------------------------------------------
# MODELO 2: ACTIVIDAD
# -------------------------------------------------
# Almacena la información general de una actividad.
class Activity(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='activities'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Descripción en formato HTML.")
    max_participants = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# -------------------------------------------------
# MODELO 3: ARCHIVOS DE ACTIVIDAD
# -------------------------------------------------
# Almacena los enlaces de descarga para una actividad.
class ActivityFile(models.Model):
    # 'ForeignKey' crea una relación. Una Actividad puede tener muchos archivos.
    activity = models.ForeignKey(Activity, related_name='files', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    url = models.URLField()

    def __str__(self):
        return f"{self.name} for {self.activity.title}"

# -------------------------------------------------
# MODELO 4: CONVOCATORIA (SLOT TEMPORAL)
# -------------------------------------------------
# Representa un horario específico para una actividad.
class TimeSlot(models.Model):
    activity = models.ForeignKey(Activity, related_name='timeslots', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        # Formateamos la fecha para que sea legible en el admin
        return f"{self.activity.title} @ {self.start_time.strftime('%Y-%m-%d %H:%M')} UTC"

# -------------------------------------------------
# MODELO 5: INSCRIPCIÓN (ENROLLMENT)
# -------------------------------------------------
# Conecta a un Usuario con una Convocatoria.
class Enrollment(models.Model):
    user = models.ForeignKey(User, related_name='enrollments', on_delete=models.CASCADE)
    timeslot = models.ForeignKey(TimeSlot, related_name='enrollments', on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Esto asegura que un usuario no se pueda inscribir dos veces en la misma convocatoria.
        unique_together = ('user', 'timeslot')

    def __str__(self):
        return f"{self.user.email} enrolled in {self.timeslot}"