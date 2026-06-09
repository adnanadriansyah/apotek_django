from django.db import models

class ChatPemesanan(models.Model):
    ROLE_CHOICES = [('user', 'User'), ('admin', 'Admin')]
    nama_pengirim = models.CharField(max_length=100)
    pesan = models.TextField()
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    tgl_chat = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_pemesanan'

    def __str__(self):
        return f"[{self.role}] {self.nama_pengirim}: {self.pesan[:40]}"
