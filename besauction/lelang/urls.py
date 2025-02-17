from django.urls import path
from .views import BarangViews, BidView, RiwayatLelangView, TambahBarangView, BarangSearchView

urlpatterns = [
    path("list-barang/", BarangViews.as_view(), name="listbarang"),
    path("bid/", BidView.as_view(), name="Bidding"),
    path("riwayat/", RiwayatLelangView.as_view(), name="riwayat"),
    path("tambahbarang/", TambahBarangView.as_view(), name="tambahbarang"),
    path('search/', BarangSearchView.as_view(), name='search'),
]

