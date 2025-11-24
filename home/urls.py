# home/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import usuario_views, tarefa_views, amigo_views, loja_views

app_name = 'home'

urlpatterns = [
    # --- URLs de Usuario ---
    path('', usuario_views.index, name='index'),
    path('home/', usuario_views.home, name='home'),
    path('login/', usuario_views.login_view, name='login'),
    path('logout/', usuario_views.logout_view, name='logout'),
    path('cadastro/', usuario_views.cadastro, name='cadastro'),

    # --- URLs de Perfil ---
    path('meu-perfil/', usuario_views.gerenciar_meu_perfil, name='meu_perfil'),
    path('meu-perfil/editar/', usuario_views.editar_perfil, name='editar_perfil'),
    
    # --- URLs de Estatisticas ---
    path('estatisticas/', usuario_views.estatisticas_view, name='estatisticas'),
    path('api/gerar-review-ia/', usuario_views.api_gerar_review_ia, name='api_gerar_review_ia'),

    # --- URLs Como Usar ---
    path('como-usar/', usuario_views.como_usar_view, name='como_usar'),

    path('termos/', usuario_views.termos, name='termos'),

    # --- URL de Resgate de Foco ---
    path('resgatar-foco/', usuario_views.resgatar_foco, name='resgatar_foco'),

    # --- URLs de Tarefas ---
    path('Tarefas/', tarefa_views.lista_Tarefas, name='lista_Tarefas'),
    path('Tarefas/adicionar/', tarefa_views.adicionar_Tarefas, name='adicionar_Tarefas'),
    path('tarefas/<int:tarefa_id>/concluir/', tarefa_views.concluir_tarefa, name='concluir_tarefa'),
    path('tarefas/salvar-recorrencia/', tarefa_views.salvar_recorrencia, name='salvar_recorrencia'),
    path('tarefas/<int:tarefa_id>/descartar/', tarefa_views.descartar_tarefa, name='descartar_tarefa'),
    path('tarefas/<int:tarefa_id>/concluir-atrasado/', tarefa_views.concluir_atrasado, name='concluir_atrasado'),
    path('tarefas/<int:tarefa_id>/editar/', tarefa_views.editar_tarefa_pessoal, name='editar_tarefa_pessoal'),
    
    # API para o "Polling"
    path('api/status-geracao-ia/', tarefa_views.api_status_geracao_ia, name='api_status_geracao_ia'),

    # --- URLs para sistema de amizade ---
    path('amigos/', amigo_views.listar_amigos, name='listar_amigos'),
    path('amigos/buscar/', amigo_views.buscar_usuarios, name='buscar_usuarios'),
    path('api/buscar-usuarios/', amigo_views.api_buscar_usuarios, name='api_buscar_usuarios'),
    path('amigos/enviar-pedido/<str:usuario_id>/', amigo_views.enviar_pedido_amizade, name='enviar_pedido_amizade'),
    path('amigos/aceitar-pedido/<int:pedido_id>/', amigo_views.aceitar_pedido_amizade, name='aceitar_pedido_amizade'),
    path('amigos/recusar-pedido/<int:pedido_id>/', amigo_views.recusar_remover_amizade, name='recusar_remover_amizade'),
    path('amigos/remover/<str:amigo_username>/', amigo_views.remover_amigo, name='remover_amigo'),
    path('amigos/perfil/<str:nome_usuario>/', amigo_views.ver_perfil_usuario, name='ver_perfil_usuario'),

    # --- URLs da Loja ---
    path('loja/', loja_views.loja_view, name='loja_view'),
    path('loja/comprar/<int:item_id>/', loja_views.comprar_item, name='comprar_item'),
    path('loja/ativar/<int:item_id>/', loja_views.ativar_item, name='ativar_item'),

    # --- URLs do Inventario ---
    path('inventario/', loja_views.inventario_view, name='inventario_view'),
]