import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import Api.routing
from Api.middleware import TokenAuthMiddleware  # your custom middleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_portal_backend.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddleware(  # <-- apply middleware here
        URLRouter(
            Api.routing.websocket_urlpatterns
        )
    ),
})
