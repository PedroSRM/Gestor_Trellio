from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/tablero/(?P<tablero_id>\d+)/$', consumers.TableroConsumer.as_asgi()),
]