from .models import BarangLelang, TransaksiLelang
from rest_framework import serializers
from django.utils import timezone

class BarangSerializers(serializers.ModelSerializer):
    class Meta:
        model = BarangLelang
        fields = '__all__'

class RiwayatBidSerializers(serializers.ModelSerializer):
    class Meta:
        model = TransaksiLelang
        fields = '__all__'

class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransaksiLelang
        fields = ['barang', 'pelelang', 'harga_bid']
    def validate(self, data):
        barang = data['barang']
        harga_bid = data['harga_bid']
        if barang.lelang_ditutup < timezone.now():
            raise serializers.ValidationError("Lelang sudah ditutup.")
        if harga_bid <= barang.harga_saatini:
            raise serializers.ValidationError("Harga bid harus lebih tinggi dari harga saat ini.")
        return data

class TambahBarangSerializers(serializers.ModelSerializer):
    class Meta:
        model = BarangLelang
        fields = ["nama", "deskripsi", "kategori", "harga_buka", "harga_saatini", "gambar", "lelang_dibuka", "lelang_ditutup", "penjual" ]
        read_only_fields = ["harga_saatini"]
    def validate(self, data):
        if 'harga_buka' in data:
            data['harga_saatini'] = data['harga_buka']
        return data