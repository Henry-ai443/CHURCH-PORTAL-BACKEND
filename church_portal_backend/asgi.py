import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import Api.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_portal_backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            Api.routing.websocket_urlpatterns
        )
    ),
})
