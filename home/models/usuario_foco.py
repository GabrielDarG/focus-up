# Em home/models/usuario_foco.py
from django.db import models
from .usuario import Usuario

class UsuarioFoco(models.Model): 
    """
    Armazena os perfis detalhados de cada usuário 
    para cada foco (academia, estudos, etc.) que a IA usará.
    """
    
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="focos_usuario") 
    foco_nome = models.CharField(max_length=50, verbose_name="Nome do Foco") 
    

    dados_especificos = models.JSONField(default=dict, blank=True, verbose_name="Dados Específicos do Foco")

    detalhes = models.TextField(blank=True, verbose_name="Observações Adicionais (para a IA)") 

    class Meta:
        unique_together = ('user', 'foco_nome')
        verbose_name = "Foco do Usuário" 
        verbose_name_plural = "Focos do Usuário" 

    def __str__(self):
        return f"Foco '{self.foco_nome}' de {self.user.nome_usuario}"