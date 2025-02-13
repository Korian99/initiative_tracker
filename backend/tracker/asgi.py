import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from players.routing import websocket_urlpatterns
# TODO - NOT WORKING
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tracker.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(websocket_urlpatterns),
})

