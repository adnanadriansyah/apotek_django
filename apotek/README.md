# 🏥 Sistem Apotek - Django + MySQL

## Tahap Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Buat Database MySQL
```sql
CREATE DATABASE db_apotek CHARACTER SET utf8mb4;
```

### 3. Konfigurasi Database
Edit `apotek/settings.py` pada bagian DATABASES:
```python
DATABASES = {
    'default': {
        'ENGINE': 'mysql.connector.django',
        'NAME': 'db_apotek',
        'USER': 'root',
        'PASSWORD': 'password_mysql_anda',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

### 4. Migrasi Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Buat Superuser (Django Admin)
```bash
python manage.py createsuperuser
```

### 6. Jalankan Server
```bash
python manage.py runserver
```
Buka: http://127.0.0.1:8000

---

## 📡 API Endpoints (Postman)

### Barang
| Method | URL | Keterangan |
|--------|-----|------------|
| GET    | /api/barang/ | Ambil semua barang |
| POST   | /api/barang/ | Tambah barang baru |
| GET    | /api/barang/{id}/ | Detail barang |
| PUT    | /api/barang/{id}/ | Update barang |
| DELETE | /api/barang/{id}/ | Hapus barang |

**Body POST Barang:**
```json
{
  "nama_barang": "Paracetamol 500mg",
  "pemasok": "PT Kimia Farma",
  "jumlah_barang": 200,
  "tgl_expired": "2026-12-31",
  "harga_satuan": 2500
}
```

### Stok
| Method | URL | Keterangan |
|--------|-----|------------|
| GET    | /api/stok/ | Ambil semua stok |
| PUT    | /api/stok/{id}/ | Update stok |

### Harga
| Method | URL | Keterangan |
|--------|-----|------------|
| GET    | /api/harga/ | Ambil semua harga |
| PUT    | /api/harga/{id}/ | Update harga |

### Pembelian
| Method | URL | Keterangan |
|--------|-----|------------|
| GET    | /api/pembelian/ | Riwayat pembelian |
| POST   | /api/pembelian/ | Buat transaksi baru |
| DELETE | /api/pembelian/{id}/ | Hapus transaksi |

**Body POST Pembelian:**
```json
{
  "id_barang": 1,
  "jumlah_pembelian": 3
}
```

### Laporan Harian (Sinkronisasi)
| Method | URL | Keterangan |
|--------|-----|------------|
| GET    | /api/laporan/ | Lihat semua laporan |
| POST   | /api/laporan/ | Sinkronisasi laporan |

**Body POST Laporan:**
```json
{
  "tgl_laporan": "2024-11-15"
}
```

### Chat Pemesanan
| Method | URL | Keterangan |
|--------|-----|------------|
| GET    | /api/chat/ | Ambil semua chat |
| POST   | /api/chat/ | Kirim pesan user |
| POST   | /api/chat/admin/reply/ | Balas pesan (admin) |
| DELETE | /api/chat/{id}/ | Hapus pesan |

**Body POST Chat:**
```json
{
  "nama_pengirim": "Budi Santoso",
  "pesan": "Apakah tersedia Amoxicillin 500mg?",
  "role": "user"
}
```
