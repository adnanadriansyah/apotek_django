import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ChatPemesanan


@csrf_exempt
def chat_list(request):
    """Ambil semua chat atau kirim pesan baru"""
    if request.method == 'GET':
        data = list(ChatPemesanan.objects.values(
            'id', 'nama_pengirim', 'pesan', 'role', 'tgl_chat'
        ).order_by('tgl_chat'))
        for d in data:
            d['tgl_chat'] = str(d['tgl_chat'])
        return JsonResponse({'status': 'ok', 'data': data})

    if request.method == 'POST':
        body = json.loads(request.body)
        c = ChatPemesanan.objects.create(
            nama_pengirim=body['nama_pengirim'],
            pesan=body['pesan'],
            role=body.get('role', 'user'),
        )
        return JsonResponse({
            'status': 'ok',
            'message': 'Pesan terkirim',
            'data': {
                'id': c.id,
                'nama_pengirim': c.nama_pengirim,
                'pesan': c.pesan,
                'role': c.role,
                'tgl_chat': str(c.tgl_chat)
            }
        }, status=201)


@csrf_exempt
def chat_admin_reply(request):
    """Endpoint khusus admin membalas pesan"""
    if request.method == 'POST':
        body = json.loads(request.body)
        c = ChatPemesanan.objects.create(
            nama_pengirim=body.get('nama_pengirim', 'Admin Apotek'),
            pesan=body['pesan'],
            role='admin',
        )
        return JsonResponse({
            'status': 'ok',
            'message': 'Balasan admin terkirim',
            'data': {
                'id': c.id,
                'nama_pengirim': c.nama_pengirim,
                'pesan': c.pesan,
                'role': c.role,
                'tgl_chat': str(c.tgl_chat)
            }
        }, status=201)


@csrf_exempt
def chat_detail(request, pk):
    try:
        c = ChatPemesanan.objects.get(pk=pk)
    except ChatPemesanan.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Pesan tidak ditemukan'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'status': 'ok', 'data': {
            'id': c.id, 'nama_pengirim': c.nama_pengirim,
            'pesan': c.pesan, 'role': c.role, 'tgl_chat': str(c.tgl_chat)
        }})

    if request.method == 'DELETE':
        c.delete()
        return JsonResponse({'status': 'ok', 'message': 'Pesan dihapus'})
