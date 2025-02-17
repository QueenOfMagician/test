import os
import django

# **Setup Django sebelum import lain**
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")
django.setup()

# **Sekarang aman untuk import Django & Channels**
from django.core.asgi import get_asgi_application
import socketio
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# **Import websocket URL setelah setup**
from lelang.routing import websocket_urlpatterns  # Pastikan file ini ada dan benar

# **Setup Socket.IO Server**
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=['http://localhost:5173']  # Sesuaikan dengan frontend-mu
)

# **Django ASGI App**
django_asgi_app = get_asgi_application()

# **Gabungkan semuanya dalam satu ASGI Application**
application = ProtocolTypeRouter({
    "http": django_asgi_app,  # Untuk request HTTP
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)  # WebSocket URL routing
    ),
})

# **Tambahkan Socket.IO sebagai middleware**
application = socketio.ASGIApp(sio, application)
