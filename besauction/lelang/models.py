from django.db import models
import random

class BarangLelang(models.Model):
    kode = models.CharField(editable=False, max_length=25, unique=True, primary_key=True, null=False)
    nama = models.CharField(max_length=255)
    deskripsi = models.TextField()
    kategori = models.CharField(max_length=255)
    harga_buka = models.IntegerField(default=0, null=False)
    harga_saatini = models.IntegerField(editable=False, default=0, null=False)
    gambar = models.ImageField(upload_to='gambar_lelang/', null=True, blank=True)
    lelang_dibuka = models.DateTimeField(null=False)
    lelang_ditutup = models.DateTimeField(null=False)
    penjual = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.kode:
            while True:
                generated_code = ''.join(random.choices('0123456789', k=12))  # Kode angka sepanjang 12
                if not BarangLelang.objects.filter(kode=generated_code).exists():
                    self.kode = generated_code
                    break
                # Set harga_saatini sama dengan harga_buka saat pertama kali dibuat
        if self.pk is None or self.harga_saatini == 0:
            self.harga_saatini = self.harga_buka
        super(BarangLelang, self).save(*args, **kwargs)

    def __str__(self):
        return f"nama Barang: {self.nama} - Saat ini: {self.harga_saatini}"


class TransaksiLelang(models.Model):
    barang = models.ForeignKey('BarangLelang', on_delete=models.CASCADE, related_name='transaksi')
    pelelang = models.CharField(max_length=255, null=False)
    harga_bid = models.IntegerField(null=False)
    waktu_bid = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Validasi: Pastikan harga_bid lebih besar dari harga_saatini
        if self.harga_bid <= self.barang.harga_saatini:
            raise ValueError("Harga bid harus lebih besar dari harga saat ini!")

        super(TransaksiLelang, self).save(*args, **kwargs)

        # Perbarui harga_saatini di BarangLelang
        self.barang.harga_saatini = self.harga_bid
        self.barang.save()

    def __str__(self):
        return f"{self.pelelang} - {self.barang.nama} - {self.harga_bid}"
