# home/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models.usuario import Usuario
from .models.tarefa import Tarefa
from .models.usuario_foco import UsuarioFoco
from .models.amigo import PedidoAmizade 
from .models.conquista import Conquista, UsuarioConquista
from .models.loja import ItemLoja, Compra, InventarioUsuario
from .models.grupo import Grupo, GrupoUsuario, GrupoTarefa
from .models.notificacao import Notificacao

class CustomUsuarioAdmin(UserAdmin):
    model = Usuario
    
    list_display = ('email', 'nome_usuario', 'nome', 'nivel', 'xp_atual', 'moedas', 'is_staff', 'is_active')
    search_fields = ('email', 'nome_usuario', 'nome')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'nivel')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome', 'nome_usuario', 'data_nascimento', 'sexo')}),
        ('Gamificação (Nível/XP/Ouro)', {'fields': ('nivel', 'xp_atual', 'xp_proximo_nivel', 'moedas')}),
        ('Gamificação (Stats)', {'fields': ('ofensiva', 'avatar', 'dias_foco', 'ultimo_resgate_foco')}),
        
        ('Gamificação (Logs)', {'fields': ('slots_tarefas_pessoais_usados', 'slots_tarefas_ia_usados', 'data_reset_slots', 'tarefas_concluidas_prazo_count', 'tarefas_concluidas_atrasadas_count', 'tarefas_descartadas_count')}),
        
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome_usuario', 'nome', 'password', 'password2'),
        }),
    )

@admin.register(Tarefa) 
class TarefaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'tipo_tarefa', 'data_criacao', 'concluida', 'falhou', 'descartada')
    list_filter = ('tipo_tarefa', 'falhou', 'concluida', 'descartada', 'data_criacao')
    search_fields = ('titulo', 'usuario__nome_usuario', 'usuario__email')
    readonly_fields = ('data_criacao', 'data_acao_final')
    
    fieldsets = (
        ('Informações Principais', {
            'fields': ('usuario', 'titulo', 'descricao', 'tipo_tarefa', 'foco') 
        }),
        ('Datas (Automático)', {
            'fields': ('data_criacao', 'data_acao_final'),
            'classes': ('collapse',)
        }),
        ('Status da Tarefa', {
            'fields': ('concluida', 'falhou', 'descartada')
        }),
        ('Gamificação (XP)', {
            'fields': ('xp', 'xp_original')
        }),
        ('Recorrência (para Templates)', {
            'fields': (
                ('recorrente_dom', 'recorrente_seg', 'recorrente_ter'), 
                ('recorrente_qua', 'recorrente_qui', 'recorrente_sex', 'recorrente_sab')
            ),
            'classes': ('collapse',)
        }),
    )

admin.site.register(Usuario, CustomUsuarioAdmin)
admin.site.register(Conquista)
admin.site.register(UsuarioConquista)
admin.site.register(ItemLoja)
admin.site.register(Compra)
admin.site.register(InventarioUsuario) 
admin.site.register(PedidoAmizade)
admin.site.register(Grupo)
admin.site.register(GrupoUsuario)
admin.site.register(GrupoTarefa)
admin.site.register(Notificacao)
admin.site.register(UsuarioFoco)