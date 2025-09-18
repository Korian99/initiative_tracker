import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tracker.settings")

from channels.security.websocket import AllowedHostsOriginValidator
import players.routing
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(AuthMiddlewareStack(
        URLRouter(players.routing.websocket_urlpatterns)
    )),
})
