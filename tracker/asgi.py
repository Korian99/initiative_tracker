import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tracker.settings")

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import players.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(players.routing.websocket_urlpatterns)
    ),
})
