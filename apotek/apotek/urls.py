from django.contrib import admin
from django.urls import path
from obat import views as obat_views
from transaksi import views as transaksi_views
from chat import views as chat_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('login/', obat_views.login_view, name='login'),
    path('logout/', obat_views.logout_view, name='logout'),

    # Halaman Profil Perusahaan (landing page)
    path('', obat_views.company_profile, name='company-profile'),

    # Dashboard (dilindungi login)
    path('dashboard/', obat_views.dashboard, name='dashboard'),

    # ── API: Barang ──────────────────────────────────────
    path('api/barang/', obat_views.barang_list, name='barang-list'),
    path('api/barang/<int:pk>/', obat_views.barang_detail, name='barang-detail'),

    # ── API: Stok ────────────────────────────────────────
    path('api/stok/', obat_views.stok_list, name='stok-list'),
    path('api/stok/<int:pk>/', obat_views.stok_detail, name='stok-detail'),

    # ── API: Harga ───────────────────────────────────────
    path('api/harga/', obat_views.harga_list, name='harga-list'),
    path('api/harga/<int:pk>/', obat_views.harga_detail, name='harga-detail'),

    # ── API: Pembelian ────────────────────────────────────
    path('api/pembelian/', transaksi_views.pembelian_list, name='pembelian-list'),
    path('api/pembelian/<int:pk>/', transaksi_views.pembelian_detail, name='pembelian-detail'),

    # ── API: Laporan (Sinkronisasi) ───────────────────────
    path('api/laporan/', transaksi_views.sinkronisasi_laporan, name='laporan-list'),

    # ── API: Chat Pemesanan ───────────────────────────────
    path('api/chat/', chat_views.chat_list, name='chat-list'),
    path('api/chat/<int:pk>/', chat_views.chat_detail, name='chat-detail'),
    path('api/chat/admin/reply/', chat_views.chat_admin_reply, name='chat-admin-reply'),
]
