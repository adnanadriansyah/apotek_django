from django.contrib import admin
from .models import Pembelian, LaporanHarian

@admin.register(Pembelian)
class PembelianAdmin(admin.ModelAdmin):
    list_display = ['id', 'nama_barang', 'jumlah_pembelian', 'total_pembayaran', 'tgl_beli']

@admin.register(LaporanHarian)
class LaporanAdmin(admin.ModelAdmin):
    list_display = ['id', 'tgl_laporan', 'total_transaksi', 'total_pendapatan']
