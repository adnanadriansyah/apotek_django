from django.contrib import admin
from .models import Barang, StokBarang, DaftarHarga

@admin.register(Barang)
class BarangAdmin(admin.ModelAdmin):
    list_display = ['id', 'nama_barang', 'pemasok', 'jumlah_barang', 'tgl_expired']

@admin.register(StokBarang)
class StokAdmin(admin.ModelAdmin):
    list_display = ['id', 'barang', 'jumlah_stok', 'updated_at']

@admin.register(DaftarHarga)
class HargaAdmin(admin.ModelAdmin):
    list_display = ['id', 'barang', 'harga_satuan', 'updated_at']
