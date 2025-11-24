from django.db import models
from .usuario import Usuario

class Amigo(models.Model):
    usuario = models.ForeignKey(Usuario, related_name='amigos', on_delete=models.CASCADE)
    amigo = models.ForeignKey(Usuario, related_name='amigo_de', on_delete=models.CASCADE)
    data_amizade = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'amigo')
        verbose_name = 'Amizade'
        verbose_name_plural = 'Amizades'

    def __str__(self):
        return f'{self.usuario.nome_usuario} é amigo de {self.amigo.nome_usuario}'

class PedidoAmizade(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('aceito', 'Aceito'),
        ('recusado', 'Recusado'),
    )
    
    de_usuario = models.ForeignKey(Usuario, related_name='pedidos_enviados', on_delete=models.CASCADE)
    para_usuario = models.ForeignKey(Usuario, related_name='pedidos_recebidos', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('de_usuario', 'para_usuario')
        verbose_name = 'Pedido de Amizade'
        verbose_name_plural = 'Pedidos de Amizade'

    def __str__(self):
        return f'Pedido de {self.de_usuario.nome_usuario} para {self.para_usuario.nome_usuario}'