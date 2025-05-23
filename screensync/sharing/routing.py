from django.urls import re_path
from sharing.consumers import RoomConsumer

websocket_urlpatterns = [
    re_path(r'ws/room/(?P<room_id>[\w-]+)/$', RoomConsumer.as_asgi()),
]
