from django.urls import re_path
from .consumers import AuctionConsumer, UpdateConsumer

websocket_urlpatterns = [
    re_path(r"ws/auction/(?P<auction_id>\d+)/$", AuctionConsumer.as_asgi()),
    re_path(r"ws/update/$", UpdateConsumer.as_asgi()),  # Harus ada `$` di akhir
]
