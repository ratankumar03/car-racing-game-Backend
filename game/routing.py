from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/race/(?P<room_name>\w+)/$', consumers.GameRoomConsumer.as_asgi()),
    re_path(r'ws/game/(?P<player_id>\w+)/$', consumers.GameStateConsumer.as_asgi()),
]
