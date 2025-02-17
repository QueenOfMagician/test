import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class AuctionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.barang_id = self.scope['url_route']['kwargs']['auction_id']
        self.group_name = f"auction_{self.barang_id}"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group when disconnected
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # This method is called when a message is received from the WebSocket
    async def receive(self, text_data):
        pass  # You don't need to handle messages sent by the frontend for this use case

    # This method handles the 'update_auction_price' messages from the backend
    async def update_auction_price(self, event):
        harga_baru = event['harga_baru']
        barang_id = event['barang_id']

        # Send the updated price to the WebSocket client
        await self.send(text_data=json.dumps({
            'harga_baru': harga_baru,
            'barang_id': barang_id
        }))


class UpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("update_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("update_group", self.channel_name)

    async def send_update(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps(data))


def broadcast_update(item):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "update_group", {
            "type": "send_update",
            "data": {
                "message": "Barang baru ditambahkan",
                "item": {
                    "kode": item.kode,
                    "nama": item.nama,
                    "deskripsi": item.deskripsi,
                    "kategori": item.kategori,
                    "harga_buka": item.harga_buka,
                    "harga_saatini": item.harga_saatini,
                    "gambar": item.gambar.url if item.gambar else None,
                    "lelang_dibuka": item.lelang_dibuka.isoformat(),
                    "lelang_ditutup": item.lelang_ditutup.isoformat(),
                    "penjual": item.penjual,
                }
            }
        }
    )
