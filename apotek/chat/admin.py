from django.contrib import admin
from .models import ChatPemesanan

@admin.register(ChatPemesanan)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['id', 'nama_pengirim', 'role', 'pesan', 'tgl_chat']
