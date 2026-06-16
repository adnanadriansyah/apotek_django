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
    produk_list = [
        {
            'icon': '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563a8" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 002 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>',
            'badge': 'Antibiotik',
            'nama': 'Amoxicillin 500mg',
            'deskripsi': 'Antibiotik spektrum luas untuk infeksi bakteri. Tersedia dalam kemasan strip 10 kapsul.',
            'harga': 'Rp45.000',
            'status': 'Tersedia',
        },
        {
            'icon': '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563a8" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
            'badge': 'Suplemen',
            'nama': 'Vitamin C 1000mg',
            'deskripsi': 'Suplemen daya tahan tubuh dengan vitamin C dosis tinggi. Kemasan botol 60 tablet.',
            'harga': 'Rp85.000',
            'status': 'Tersedia',
        },
        {
            'icon': '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563a8" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
            'badge': 'Herbal',
            'nama': 'Jahe Merah Kapsul',
            'deskripsi': 'Ekstrak jahe merah berkhasiat untuk menghangatkan tubuh dan meredakan masuk angin.',
            'harga': 'Rp65.000',
            'status': 'Tersedia',
        },
        {
            'icon': '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563a8" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="10" r="3"/><path d="M12 21.7C17.3 17 20 13 20 10a8 8 0 10-16 0c0 3 2.7 6.9 8 11.7z"/></svg>',
            'badge': 'First Aid',
            'nama': 'P3K Kit Lengkap',
            'deskripsi': 'Paket pertolongan pertama lengkap dengan perban, plester, antiseptik, dan gunting.',
            'harga': 'Rp120.000',
            'status': 'Tersedia',
        },
        {
            'icon': '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563a8" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>',
            'badge': 'Alat Kesehatan',
            'nama': 'Termometer Digital',
            'deskripsi': 'Termometer digital dengan layar LCD, akurat, dan respons cepat dalam 10 detik.',
            'harga': 'Rp55.000',
            'status': 'Tersedia',
        },
        {
            'icon': '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563a8" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
            'badge': 'Kecantikan',
            'nama': 'Sunscreen SPF 50',
            'deskripsi': 'Tabir surya dengan SPF 50 PA+++, ringan di kulit, dan tahan air hingga 80 menit.',
            'harga': 'Rp95.000',
            'status': 'Tersedia',
        },
    ]
    return render(request, 'company_profile.html', {
        'active_page': 'beranda',
        'produk_list': produk_list,
    })

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
