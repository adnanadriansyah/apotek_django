from django.db import models
from obat.models import Barang

class Pembelian(models.Model):
    barang = models.ForeignKey(Barang, on_delete=models.CASCADE, related_name='pembelian')
    nama_barang = models.CharField(max_length=100)
    jumlah_pembelian = models.IntegerField()
    harga = models.DecimalField(max_digits=15, decimal_places=2)
    total_pembayaran = models.DecimalField(max_digits=15, decimal_places=2)
    tgl_beli = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pembelian'

    def __str__(self):
        return f"Beli {self.nama_barang} - {self.tgl_beli.date()}"


class LaporanHarian(models.Model):
    tgl_laporan = models.DateField(unique=True)
    total_transaksi = models.IntegerField(default=0)
    total_pendapatan = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    generated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'laporan_harian'

    def __str__(self):
        return f"Laporan {self.tgl_laporan}"
