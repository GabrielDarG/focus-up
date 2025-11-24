
from django.db import models
from .usuario import Usuario

class ItemLoja(models.Model):
    """
    Representa um produto que pode ser comprado na loja.
    """
    
    TIPO_EFEITO_CHOICES = [
        ('CONGELADOR', 'Congelador de Ofensiva'),
        ('XP_BOOST', 'Dobro de XP (24h)'),
        ('SLOT_EXTRA', 'Slot de Tarefa Extra'),
        ('MOLDURA', 'Moldura (Formato)'),     
        ('COR_BORDA', 'Cor da Borda'),       
        ('AVATAR', 'Novo Avatar'),
    ]

    nome = models.CharField(max_length=100, verbose_name="Nome do Item")
    descricao = models.TextField(verbose_name="Descrição", default="")
    preco = models.IntegerField(default=100, verbose_name="Preço (Moedas)")
    
    tipo_efeito = models.CharField(
        max_length=20, 
        choices=TIPO_EFEITO_CHOICES,
        default='CONGELADOR'
    )
    
    valor_efeito = models.IntegerField(default=1, verbose_name="Valor do Efeito")

    icone_bootstrap = models.CharField(
        max_length=50, 
        default="bi-box-seam", 
        help_text="Classe do ícone Bootstrap (ex: bi-snow2)"
    )
    

    classe_css = models.CharField(
        max_length=50, 
        blank=True, null=True, 
        verbose_name="Classe CSS (Para Molduras/Cores)",
        help_text="Ex: moldura-quadrada, borda-vermelha, borda-azul"
    )
    
    eh_consumivel = models.BooleanField(default=True, verbose_name="É Consumível?")

    def __str__(self):
        return f"{self.nome} - {self.preco} moedas"

    class Meta:
        verbose_name = "Item da Loja"
        verbose_name_plural = "Itens da Loja"


class InventarioUsuario(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="inventario")
    item = models.ForeignKey(ItemLoja, on_delete=models.CASCADE)
    
    quantidade = models.IntegerField(default=1, verbose_name="Quantidade Possuída")
    data_aquisicao = models.DateTimeField(auto_now_add=True)
    
    esta_ativo = models.BooleanField(default=False, verbose_name="Item em Uso?")
    data_expiracao_efeito = models.DateTimeField(null=True, blank=True, verbose_name="Data de Expiração")

    def __str__(self):
        return f"{self.usuario.email} possui {self.quantidade}x {self.item.nome}"

    class Meta:
        unique_together = ('usuario', 'item') 
        verbose_name = "Item no Inventário"
        verbose_name_plural = "Inventário dos Usuários"


class Compra(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    item = models.ForeignKey(ItemLoja, on_delete=models.SET_NULL, null=True)
    preco_pago = models.IntegerField(default=0) 
    data_compra = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        nome_item = self.item.nome if self.item else "Item Removido"
        return f"Compra: {nome_item} por {self.usuario.email}"