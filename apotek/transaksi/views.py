import json
from datetime import date, datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count
from django.utils import timezone
from obat.models import Barang, StokBarang, DaftarHarga
from .models import Pembelian, LaporanHarian


# ─── PEMBELIAN ────────────────────────────────────────────
@csrf_exempt
def pembelian_list(request):
    if request.method == 'GET':
        data = list(Pembelian.objects.values(
            'id', 'barang_id', 'nama_barang', 'jumlah_pembelian',
            'harga', 'total_pembayaran', 'tgl_beli'
        ).order_by('-tgl_beli'))
        for d in data:
            d['harga'] = float(d['harga'])
            d['total_pembayaran'] = float(d['total_pembayaran'])
            d['tgl_beli'] = str(d['tgl_beli'])
        return JsonResponse({'status': 'ok', 'data': data})

    if request.method == 'POST':
        body = json.loads(request.body)
        id_barang = body['id_barang']

        try:
            barang = Barang.objects.get(pk=id_barang)
            stok = StokBarang.objects.get(barang=barang)
            harga_obj = DaftarHarga.objects.get(barang=barang)
        except (Barang.DoesNotExist, StokBarang.DoesNotExist, DaftarHarga.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Barang tidak ditemukan'}, status=404)

        jumlah = int(body['jumlah_pembelian'])
        if stok.jumlah_stok < jumlah:
            return JsonResponse({'status': 'error', 'message': f'Stok tidak cukup. Stok tersedia: {stok.jumlah_stok}'}, status=400)

        harga = float(harga_obj.harga_satuan)
        total = harga * jumlah

        p = Pembelian.objects.create(
            barang=barang,
            nama_barang=barang.nama_barang,
            jumlah_pembelian=jumlah,
            harga=harga,
            total_pembayaran=total,
        )

        # Kurangi stok otomatis
        stok.jumlah_stok -= jumlah
        stok.save()
        barang.jumlah_barang = stok.jumlah_stok
        barang.save()

        return JsonResponse({
            'status': 'ok',
            'message': 'Pembelian berhasil',
            'data': {
                'id': p.id,
                'nama_barang': p.nama_barang,
                'jumlah': jumlah,
                'harga_satuan': harga,
                'total': total
            }
        }, status=201)


@csrf_exempt
def pembelian_detail(request, pk):
    try:
        p = Pembelian.objects.get(pk=pk)
    except Pembelian.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Data tidak ditemukan'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'status': 'ok', 'data': {
            'id': p.id, 'id_barang': p.barang_id,
            'nama_barang': p.nama_barang, 'jumlah_pembelian': p.jumlah_pembelian,
            'harga': float(p.harga), 'total_pembayaran': float(p.total_pembayaran),
            'tgl_beli': str(p.tgl_beli)
        }})

    if request.method == 'DELETE':
        p.delete()
        return JsonResponse({'status': 'ok', 'message': 'Data pembelian dihapus'})


# ─── SINKRONISASI LAPORAN HARIAN ─────────────────────────
@csrf_exempt
def sinkronisasi_laporan(request):
    if request.method == 'POST':
        body = json.loads(request.body) if request.body else {}
        tgl = body.get('tgl_laporan', str(date.today()))

        tgl_date = datetime.strptime(tgl, '%Y-%m-%d').date()
        tgl_start = timezone.make_aware(datetime.combine(tgl_date, datetime.min.time()))
        tgl_end = timezone.make_aware(datetime.combine(tgl_date + timedelta(days=1), datetime.min.time()))

        total_transaksi = Pembelian.objects.filter(tgl_beli__gte=tgl_start, tgl_beli__lt=tgl_end).count()
        total_pendapatan = Pembelian.objects.filter(tgl_beli__gte=tgl_start, tgl_beli__lt=tgl_end).aggregate(
            total=Sum('total_pembayaran')
        )['total'] or 0

        laporan, created = LaporanHarian.objects.update_or_create(
            tgl_laporan=tgl_date,
            defaults={
                'total_transaksi': total_transaksi,
                'total_pendapatan': total_pendapatan,
            }
        )

        return JsonResponse({
            'status': 'ok',
            'message': f'Laporan {"dibuat" if created else "diperbarui"} — {total_transaksi} transaksi, Rp {float(total_pendapatan):,.0f}',
            'data': {
                'tgl_laporan': str(laporan.tgl_laporan),
                'total_transaksi': laporan.total_transaksi,
                'total_pendapatan': float(laporan.total_pendapatan),
            }
        })

    if request.method == 'GET':
        data = list(LaporanHarian.objects.values(
            'id', 'tgl_laporan', 'total_transaksi', 'total_pendapatan', 'generated_at'
        ).order_by('-tgl_laporan'))
        for d in data:
            d['tgl_laporan'] = str(d['tgl_laporan'])
            d['total_pendapatan'] = float(d['total_pendapatan'])
            d['generated_at'] = str(d['generated_at'])
        return JsonResponse({'status': 'ok', 'data': data})
