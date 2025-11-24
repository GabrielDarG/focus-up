# home/models/notificacao.py

from django.db import models
from .usuario import Usuario

class Notificacao(models.Model):
    TIPO_CHOICES = [
        ('CONQUISTA', 'Nova Conquista'),
        ('AMIZADE', 'Pedido de Amizade'),
        ('Tarefa', 'Lembrete de Tarefa'),
        ('GRUPO', 'Aviso de Grupo'),
    ]

    id_notificacao = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, related_name='notificacoes', on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    mensagem = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)

    class Meta:
        ordering = ['-data_envio']
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'

    def __str__(self):
        return f'Notificação para {self.usuario.nome_usuario} - {self.tipo}'