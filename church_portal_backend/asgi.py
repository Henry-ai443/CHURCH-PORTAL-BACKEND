import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import Api.routing  # assuming your app is called `api`

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_portal_backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(Api.routing.websocket_urlpatterns),
})
