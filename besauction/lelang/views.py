from rest_framework.permissions import AllowAny
from .consumers import broadcast_update
from .serializers import BarangSerializers, BidSerializer, RiwayatBidSerializers, TambahBarangSerializers
from rest_framework.views import APIView
from rest_framework import generics, status
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from rest_framework.response import Response
from .models import BarangLelang, TransaksiLelang
from fuzzywuzzy import process
# Create your views here.

class BarangViews(APIView):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        barang = BarangLelang.objects.all()
        serializer = BarangSerializers(barang, many=True)
        return Response(serializer.data)

class RiwayatLelangView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        barang_kode = request.query_params.get('barang_kode', None)
        if barang_kode:
            barang = get_object_or_404(BarangLelang, kode=barang_kode)
            transaksi = TransaksiLelang.objects.filter(barang=barang)
        else:
            transaksi = TransaksiLelang.objects.all()
        if not transaksi.exists():
            return Response({"message": "Tidak ada transaksi ditemukan."}, status=status.HTTP_404_NOT_FOUND)
        serializer = RiwayatBidSerializers(transaksi, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BidView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = BidSerializer(data=request.data)
        if serializer.is_valid():
            bid_data = serializer.validated_data
            barang = bid_data['barang']
            pelelang = bid_data['pelelang']
            harga_bid = bid_data['harga_bid']
            if barang.lelang_ditutup < timezone.now():
                return Response({"error": "Lelang sudah ditutup."}, status=status.HTTP_400_BAD_REQUEST)
            if harga_bid <= barang.harga_saatini:
                return Response({"error": "Harga bid harus lebih tinggi dari harga saat ini."}, status=status.HTTP_400_BAD_REQUEST)

            # Simpan transaksi bid
            transaksi = TransaksiLelang.objects.create(
                barang=barang,
                pelelang=pelelang,
                harga_bid=harga_bid,
            )
            barang.harga_saatini = harga_bid
            barang.save()
            # Kirim update harga melalui WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"auction_{barang.kode}",
                {
                    "type": "update_auction_price",
                    "harga_baru": harga_bid,
                    "barang_id": barang.kode,
                }
            )
            return Response({"message": "Bid berhasil!", "harga_baru": harga_bid}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TambahBarangView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = BarangLelang.objects.all()
    serializer_class = TambahBarangSerializers

    def perform_create(self, serializer):
        item = serializer.save()
        broadcast_update(item)


class BarangSearchView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        query = request.query_params.get('q', '')
        if query:
            # Ambil semua nama barang dari model
            barang_list = BarangLelang.objects.all()
            nama_barang_list = [barang.nama for barang in barang_list]

            # Fuzzy matching untuk nama barang
            matched_names = process.extract(query, nama_barang_list, limit=5)  # Ambil 5 hasil terbaik

            # Ambil barang yang cocok berdasarkan fuzzy match
            matched_barang = []
            for match in matched_names:
                barang = BarangLelang.objects.filter(nama=match[0]).first()
                matched_barang.append(barang)

            # Serialize hasil barang yang ditemukan
            serializer = BarangSerializers(matched_barang, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"message": "Query parameter 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)
