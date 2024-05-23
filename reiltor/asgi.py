import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import announcements.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reiltor.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            announcements.routing.websocket_urlpatterns
        )
    ),
})