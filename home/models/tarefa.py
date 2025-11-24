# home/models/tarefa.py

from django.db import models
from .usuario import Usuario 
from .usuario_foco import UsuarioFoco 
from django.utils import timezone 

class Tarefa(models.Model):
    FREQUENCIA_CHOICES = [
        ('DIARIA', 'Diária'),
        ('SEMANAL', 'Semanal'),
        ('MENSAL', 'Mensal')
    ]

    TIPO_CHOICES = [
        ('PESSOAL', 'Pessoal'),   
        ('DIARIA', 'Diária (Antigo?)'),
        ('SEMANAL', 'Semanal (Antigo?)'),
        ('TEMPLATE_PESSOAL', 'Template Pessoal'),
        ('IA_DIARIA', 'IA Diária')
    ]
    
    id_Tarefa = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='Tarefas')
    
    foco = models.ForeignKey(
        UsuarioFoco, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,               
        verbose_name="Área de Foco"
    )

    tipo_tarefa = models.CharField(
        max_length=20, 
        choices=TIPO_CHOICES, 
        default='PESSOAL', 
        verbose_name="Tipo da Tarefa"
    )
    
    titulo = models.CharField(max_length=100, verbose_name="Nome do Hábito") 
    
    descricao = models.TextField(null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    frequencia = models.CharField(max_length=10, choices=FREQUENCIA_CHOICES, default='DIARIA', null=True, blank=True)
    
    hora_lembrete = models.TimeField(verbose_name="Horário do Lembrete", null=True, blank=True) 
    ultimo_lembrete_enviado = models.DateTimeField(blank=True, null=True)

    concluida = models.BooleanField(default=False)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    
    xp_original = models.IntegerField(null=True, blank=True, verbose_name="XP Original (se falhou)")
    xp = models.IntegerField(default=10, verbose_name="XP da Tarefa")

    falhou = models.BooleanField(default=False, verbose_name="Tarefa Falhou (reset 22h)")

    descartada = models.BooleanField(default=False, verbose_name="Tarefa Descartada")
    data_acao_final = models.DateTimeField(null=True, blank=True, verbose_name="Data de Conclusão ou Descarte")

    # Campos de Recorrência
    recorrente_dom = models.BooleanField(default=False, verbose_name="Dom")
    recorrente_seg = models.BooleanField(default=False, verbose_name="Seg")
    recorrente_ter = models.BooleanField(default=False, verbose_name="Ter")
    recorrente_qua = models.BooleanField(default=False, verbose_name="Qua")
    recorrente_qui = models.BooleanField(default=False, verbose_name="Qui")
    recorrente_sex = models.BooleanField(default=False, verbose_name="Sex")
    recorrente_sab = models.BooleanField(default=False, verbose_name="Sáb")

    def __str__(self):
        nome_display = getattr(self.usuario, 'nome_usuario', self.usuario.email)
        return f'[{self.get_tipo_tarefa_display()}] {self.titulo} ({nome_display})' 

    def save(self, *args, **kwargs):
        if self.xp_original is None and self.xp > 0:
            self.xp_original = self.xp
        
        if self.falhou and self.xp > 0:
            if self.xp_original is None:
                self.xp_original = self.xp
            self.xp = 0
            
        agora = timezone.now()
        
        if (self.concluida or self.descartada) and self.data_acao_final is None:
            self.data_acao_final = agora
            
        elif not self.concluida and not self.descartada:
            self.data_acao_final = None
            
        super().save(*args, **kwargs)

    def get_dias_recorrencia_display(self):
        dias_map = {
            'recorrente_seg': 'Seg', 'recorrente_ter': 'Ter', 'recorrente_qua': 'Qua',
            'recorrente_qui': 'Qui', 'recorrente_sex': 'Sex', 'recorrente_sab': 'Sáb',
            'recorrente_dom': 'Dom',
        }
        dias_selecionados = [dias_map[field] for field in dias_map if getattr(self, field)]
        if len(dias_selecionados) == 7: return "Todos os dias"
        if len(dias_selecionados) == 0: return None 
        return ", ".join(dias_selecionados)