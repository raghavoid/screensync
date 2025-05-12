from django.urls import re_path
from sharing.consumers import RoomConsumer

websocket_urlpatterns = [
    re_path("ws/room/(?P<room_id>[\w-]+)/$", RoomConsumer.as_asgi()),
]
