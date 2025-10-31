# api/cron.py

from django_cron import CronJobBase, Schedule
from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta
from django.conf import settings

from .models import TimeSlot, Enrollment

class SendReminderCronJob(CronJobBase):
    """
    Este Cron Job se ejecuta periódicamente (ej. cada 10 min) 
    y envía recordatorios por email.
    """

    # Configura cada cuánto queremos que se ejecute este job
    RUN_EVERY_MINS = 10 

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'api.send_reminder_cron_job'    # Un nombre único

    def do(self):
        # 1. Obtenemos la hora actual en UTC
        now = timezone.now()

        # 2. Definimos nuestra "ventana de recordatorio"
        #    Queremos encontrar convocatorias que empiecen en...
        #    ...más de 30 minutos (para no spamear si es en 2 min)
        #    ...y menos de 60 minutos (nuestra ventana de 1 hora)
        #    (Estos valores son configurables)

        start_window = now + timedelta(minutes=30)
        end_window = now + timedelta(minutes=60)

        print(f"--- Cron Job: Buscando convocatorias entre {start_window} y {end_window} ---")

        # 3. Buscamos convocatorias que empiecen en esa ventana
        #    Y que no hayamos enviado ya un recordatorio (¡importante!)
        slots_to_remind = TimeSlot.objects.filter(
            start_time__gte=start_window,
            start_time__lte=end_window
            # Más adelante añadiremos un campo "reminder_sent"
            # Por ahora, esto funciona para la prueba.
        )

        if not slots_to_remind.exists():
            print("--- Cron Job: No hay convocatorias que necesiten recordatorio. ---")
            return

        print(f"--- Cron Job: ¡Se encontraron {slots_to_remind.count()} convocatorias! ---")

        # 4. Por cada convocatoria, buscamos a los inscritos
        for slot in slots_to_remind:
            enrollments = Enrollment.objects.filter(timeslot=slot)

            if not enrollments.exists():
                print(f"    > '{slot.activity.title}' encontrado, pero no hay inscritos. Saltando.")
                continue # Siguiente convocatoria si esta no tiene inscritos

            print(f"--- Cron Job: Enviando {enrollments.count()} correos para {slot.activity.title} ---")

            # 5. Preparamos y enviamos los correos
            for enrollment in enrollments:
                user_email = enrollment.user.email
                activity_title = slot.activity.title
                start_time_str = slot.start_time.strftime("%Y-%m-%d a las %H:%M UTC")

                try:
                    send_mail(
                        f'Recordatorio: Tu actividad "{activity_title}" va a comenzar',

                        f'¡Hola!\n\n'
                        f'Este es un recordatorio de que tu actividad "{activity_title}" '
                        f'está programada para comenzar el {start_time_str}.\n\n'
                        f'¡Prepárate para la sesión!',

                        settings.DEFAULT_FROM_EMAIL, # El remitente de SendGrid
                        [user_email], # El destinatario
                        fail_silently=False,
                    )
                    print(f"    > Correo enviado a {user_email}")

                except Exception as e:
                    print(f"    > ERROR al enviar a {user_email}: {e}")

        print("--- Cron Job: Finalizado. ---")