
from django.db import models
from .usuario import Usuario

class Conquista(models.Model):
    id_conquista = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(null=True, blank=True)
    criterio = models.CharField(max_length=150)
    usuarios = models.ManyToManyField(Usuario, through='UsuarioConquista', related_name='conquistas')

    xp_points = models.IntegerField(default=0, help_text="XP ganho ao obter essa conquista")

    def __str__(self):
        return self.nome

class UsuarioConquista(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    conquista = models.ForeignKey(Conquista, on_delete=models.CASCADE)
    data_conquista = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'conquista')

    def __str__(self):
        return f'{self.usuario.nome_usuario} - {self.conquista.nome}'