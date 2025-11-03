# api/consumers.py
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import TimeSlot, Enrollment, User
from asgiref.sync import sync_to_async
from django.utils import timezone

class WaitingRoomConsumer(AsyncWebsocketConsumer):
    """
    Gestiona la sala de espera de una convocatoria (TimeSlot).
    """

    async def connect(self):
        # Obtenemos el ID de la convocatoria desde la URL
        self.room_id = self.scope['url_route']['kwargs']['timeslot_id']
        self.room_group_name = f'waiting_room_{self.room_id}'

        # Unirse al grupo de la sala
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # TODO: Autenticar al usuario
        # Por ahora, nos conectamos anónimamente.

        print(f"Usuario conectado a la sala {self.room_id}")

        # Enviar mensaje de bienvenida
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'¡Conectado a la sala de espera {self.room_id}!'
        }))

    async def disconnect(self, close_code):
        # Salir del grupo de la sala
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"Usuario desconectado de la sala {self.room_id}")

    async def receive(self, text_data):
        # Esta función se activa cuando el cliente envía un mensaje
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'user_joined':
            # Un usuario (probablemente el primero) inicia la cuenta atrás
            # O podríamos iniciarla en `connect` si es el primer usuario.
            # Esta lógica la refinaremos, por ahora solo retransmitimos.
            await self.start_countdown()

    async def start_countdown(self):
        # Esta es la lógica central. 
        # El primer usuario en entrar podría disparar esto.

        # TODO: Evitar que esto se dispare varias veces.

        print(f"Iniciando cuenta atrás para la sala {self.room_id}...")

        # Simulamos el tiempo de espera (configurable en el requisito)
        # Por ahora, 10 segundos para la prueba.
        WAIT_SECONDS = 10 

        for i in range(WAIT_SECONDS, 0, -1):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'countdown_tick',
                    'time_left': i
                }
            )
            await asyncio.sleep(1) # Espera 1 segundo

        # ¡Tiempo agotado!
        await self.launch_call()

    async def launch_call(self):
        # Lógica de agrupación y lanzamiento de Jitsi
        print(f"¡Tiempo agotado para {self.room_id}! Lanzando llamadas.")

        # 1. Obtener la convocatoria y el máximo de participantes
        # Como estamos en un método async, necesitamos helpers sync_to_async
        timeslot, max_participants = await self.get_timeslot_details()

        # 2. Obtener los usuarios que SÍ se presentaron (los 'attended=True')
        # (Por ahora, buscaremos a todos los inscritos)
        enrollments = await self.get_enrollments()

        # 3. Lógica de agrupación
        # Esta es la lógica que pediste: (ej. 5 usuarios, max 4 -> grupos de 3 y 2)
        # ¡Esta lógica es compleja! Empecemos con algo simple:
        # TODO: Implementar la lógica de agrupación compleja.

        # Por ahora, solo creamos UNA sala de Jitsi para todos
        jitsi_room_name = f'talkabout_{self.room_id}_{timezone.now().timestamp()}'
        jitsi_url = f'https://meet.jit.si/{jitsi_room_name}'

        # 4. Enviar la URL a todos en el grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'call_launched',
                'url': jitsi_url
            }
        )

    # --- Funciones de Ayuda (para hablar con la BBDD) ---

    @sync_to_async
    def get_timeslot_details(self):
        slot = TimeSlot.objects.get(id=self.room_id)
        return slot, slot.activity.max_participants

    @sync_to_async
    def get_enrollments(self):
        # Idealmente, aquí filtraríamos por `attended=True`
        return list(Enrollment.objects.filter(timeslot_id=self.room_id))


    # --- Controladores de Mensajes del Grupo ---

    async def countdown_tick(self, event):
        # Enviar el "tick" de la cuenta atrás al cliente
        await self.send(text_data=json.dumps({
            'type': 'countdown',
            'time_left': event['time_left']
        }))

    async def call_launched(self, event):
        # Enviar la URL de la llamada al cliente
        await self.send(text_data=json.dumps({
            'type': 'redirect',
            'url': event['url']
        }))