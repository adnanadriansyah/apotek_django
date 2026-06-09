from django.db import models

class Barang(models.Model):
    nama_barang = models.CharField(max_length=100)
    pemasok = models.CharField(max_length=100)
    jumlah_barang = models.IntegerField(default=0)
    tgl_expired = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'barang'

    def __str__(self):
        return self.nama_barang


class StokBarang(models.Model):
    barang = models.OneToOneField(Barang, on_delete=models.CASCADE, related_name='stok')
    nama_barang = models.CharField(max_length=100)
    jumlah_stok = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stok_barang'

    def __str__(self):
        return f"Stok {self.nama_barang}"


class DaftarHarga(models.Model):
    barang = models.OneToOneField(Barang, on_delete=models.CASCADE, related_name='harga')
    nama_barang = models.CharField(max_length=100)
    harga_satuan = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'daftar_harga'

    def __str__(self):
        return f"Harga {self.nama_barang}"
