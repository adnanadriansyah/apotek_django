import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Barang, StokBarang, DaftarHarga


# ─── BARANG ──────────────────────────────────────────────
@csrf_exempt
def barang_list(request):
    if request.method == 'GET':
        data = list(Barang.objects.values(
            'id', 'nama_barang', 'pemasok', 'jumlah_barang', 'tgl_expired', 'created_at'
        ))
        for d in data:
            d['tgl_expired'] = str(d['tgl_expired'])
            d['created_at'] = str(d['created_at'])
        return JsonResponse({'status': 'ok', 'data': data})

    if request.method == 'POST':
        body = json.loads(request.body)
        b = Barang.objects.create(
            nama_barang=body['nama_barang'],
            pemasok=body['pemasok'],
            jumlah_barang=body['jumlah_barang'],
            tgl_expired=body['tgl_expired'],
        )
        # Auto-create stok & harga entry
        StokBarang.objects.create(barang=b, nama_barang=b.nama_barang, jumlah_stok=b.jumlah_barang)
        DaftarHarga.objects.create(barang=b, nama_barang=b.nama_barang, harga_satuan=body.get('harga_satuan', 0))
        return JsonResponse({'status': 'ok', 'message': 'Barang berhasil ditambah', 'id': b.id}, status=201)


@csrf_exempt
def barang_detail(request, pk):
    try:
        b = Barang.objects.get(pk=pk)
    except Barang.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Barang tidak ditemukan'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'status': 'ok', 'data': {
            'id': b.id, 'nama_barang': b.nama_barang, 'pemasok': b.pemasok,
            'jumlah_barang': b.jumlah_barang, 'tgl_expired': str(b.tgl_expired)
        }})

    if request.method == 'PUT':
        body = json.loads(request.body)
        b.nama_barang = body.get('nama_barang', b.nama_barang)
        b.pemasok = body.get('pemasok', b.pemasok)
        b.jumlah_barang = body.get('jumlah_barang', b.jumlah_barang)
        b.tgl_expired = body.get('tgl_expired', b.tgl_expired)
        b.save()
        return JsonResponse({'status': 'ok', 'message': 'Barang berhasil diupdate'})

    if request.method == 'DELETE':
        b.delete()
        return JsonResponse({'status': 'ok', 'message': 'Barang berhasil dihapus'})


# ─── STOK ─────────────────────────────────────────────────
@csrf_exempt
def stok_list(request):
    if request.method == 'GET':
        data = list(StokBarang.objects.values(
            'id', 'barang_id', 'nama_barang', 'jumlah_stok', 'updated_at'
        ))
        for d in data:
            d['updated_at'] = str(d['updated_at'])
        return JsonResponse({'status': 'ok', 'data': data})


@csrf_exempt
def stok_detail(request, pk):
    try:
        s = StokBarang.objects.get(pk=pk)
    except StokBarang.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Stok tidak ditemukan'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'status': 'ok', 'data': {
            'id': s.id, 'id_barang': s.barang_id,
            'nama_barang': s.nama_barang, 'jumlah_stok': s.jumlah_stok
        }})

    if request.method == 'PUT':
        body = json.loads(request.body)
        s.jumlah_stok = body.get('jumlah_stok', s.jumlah_stok)
        s.save()
        # Sync ke tabel barang
        s.barang.jumlah_barang = s.jumlah_stok
        s.barang.save()
        return JsonResponse({'status': 'ok', 'message': 'Stok berhasil diupdate'})


# ─── HARGA ────────────────────────────────────────────────
@csrf_exempt
def harga_list(request):
    if request.method == 'GET':
        data = list(DaftarHarga.objects.values(
            'id', 'barang_id', 'nama_barang', 'harga_satuan', 'updated_at'
        ))
        for d in data:
            d['harga_satuan'] = float(d['harga_satuan'])
            d['updated_at'] = str(d['updated_at'])
        return JsonResponse({'status': 'ok', 'data': data})


@csrf_exempt
def harga_detail(request, pk):
    try:
        h = DaftarHarga.objects.get(pk=pk)
    except DaftarHarga.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Harga tidak ditemukan'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'status': 'ok', 'data': {
            'id': h.id, 'id_barang': h.barang_id,
            'nama_barang': h.nama_barang, 'harga_satuan': float(h.harga_satuan)
        }})

    if request.method == 'PUT':
        body = json.loads(request.body)
        h.harga_satuan = body.get('harga_satuan', h.harga_satuan)
        h.save()
        return JsonResponse({'status': 'ok', 'message': 'Harga berhasil diupdate'})


# ─── AUTH ──────────────────────────────────────────────────
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is None:
            from django.contrib.auth.models import User
            try:
                u = User.objects.get(email=username)
                user = authenticate(request, username=u.username, password=password)
            except User.DoesNotExist:
                pass
        if user is not None:
            login(request, user)
            return redirect('/dashboard/')
        return render(request, 'login.html', {'error': 'Username/Email atau password salah!'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('/')

# ─── DASHBOARD VIEW ───────────────────────────────────────
@login_required(login_url='/login/')
def dashboard(request):
    return render(request, 'dashboard.html')

def company_profile(request):
    return render(request, 'company_profile.html', {'active_page': 'beranda'})

def tentang(request):
    return render(request, 'tentang.html', {'active_page': 'tentang'})

def layanan(request):
    return render(request, 'layanan.html', {'active_page': 'layanan'})

def tim(request):
    return render(request, 'tim.html', {'active_page': 'tim'})

def testimoni(request):
    return render(request, 'testimoni.html', {'active_page': 'testimoni'})

def kontak(request):
    return render(request, 'kontak.html', {'active_page': 'kontak'})
