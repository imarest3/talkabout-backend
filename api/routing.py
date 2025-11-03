# api/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # La URL para nuestra sala de espera
    re_path(r'ws/waitroom/(?P<timeslot_id>\d+)/$', consumers.WaitingRoomConsumer.as_asgi()),
]