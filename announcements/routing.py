from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'serverdestination/ws/counter/(?P<token>\w+)$', consumers.CounterConsumer.as_asgi()),
]
