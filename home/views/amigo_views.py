from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from ..models.usuario import Usuario
from ..models.amigo import Amigo, PedidoAmizade
from ..models.tarefa import Tarefa # <-- IMPORTANTE
from django.contrib.auth import get_user_model
from django.utils import timezone # <-- IMPORTANTE
from datetime import timedelta # <-- IMPORTANTE
from django.http import JsonResponse
from django.db.models import F

# (Seu logger, se você usar)
import logging
logger = logging.getLogger(__name__)

@login_required
def buscar_usuarios(request):
    """
    Apenas carrega a página HTML base para "Encontrar Amigos".
    O JavaScript (AJAX) cuidará de fazer a busca e exibir os resultados.
    """
    return render(request, 'home/amigos/buscar_usuarios.html')


@login_required
def api_buscar_usuarios(request):
    """
    (API) Responde ao JavaScript com uma lista de usuários (em JSON) 
    baseada na busca 'q'.
    """
    query = request.GET.get('q', '') 
    resultados_lista = []

    if query and len(query) >= 2: # Só busca com 2+ caracteres
        resultados_qs = Usuario.objects.filter(
            Q(nome_usuario__icontains=query) | Q(nome__icontains=query)
        ).exclude(pk=request.user.pk)[:10] # Limita a 10 resultados

        for usuario in resultados_qs:
            resultados_lista.append({
                'id': usuario.pk,
                'nome': usuario.nome,
                'nome_usuario': usuario.nome_usuario
            })
    
    return JsonResponse({'resultados': resultados_lista})


@login_required
def enviar_pedido_amizade(request, usuario_id):
    """
    Cria um PedidoAmizade (status 'pendente') 
    para um usuário. Requer um método POST.
    """
    if request.method == 'POST':
        para_usuario = get_object_or_404(Usuario, pk=usuario_id)
        de_usuario = request.user

        if para_usuario == de_usuario:
            messages.error(request, 'Você não pode adicionar a si mesmo.')
        elif Amigo.objects.filter(usuario=de_usuario, amigo=para_usuario).exists():
            messages.warning(request, f'Você já é amigo de {para_usuario.nome_usuario}.')
        else:
            # get_or_create para evitar duplicados
            pedido, created = PedidoAmizade.objects.get_or_create(
                de_usuario=de_usuario, 
                para_usuario=para_usuario,
                defaults={'status': 'pendente'} # Só define status se for novo
            )
            
            if created:
                messages.success(request, f'Pedido de amizade enviado para {para_usuario.nome_usuario}.')
            else:
                # Se já existe, verifica se estava recusado e reenvia
                if pedido.status == 'recusado':
                    pedido.status = 'pendente'
                    pedido.save()
                    messages.success(request, f'Pedido de amizade reenviado para {para_usuario.nome_usuario}.')
                else:
                    messages.info(request, f'Você já enviou um pedido para {para_usuario.nome_usuario}.')

        return redirect('home:buscar_usuarios')
    
    else:
        messages.error(request, 'Método não permitido.')
        return redirect('home:buscar_usuarios')


@login_required
def aceitar_pedido_amizade(request, pedido_id):
    """
    Muda o status de um pedido para 'aceito' e cria a 
    relação de amizade bidirecional (Amigo).
    """
    pedido = get_object_or_404(PedidoAmizade, pk=pedido_id, para_usuario=request.user)

    if pedido.status == 'pendente':
        pedido.status = 'aceito'
        pedido.save()
        Amigo.objects.create(usuario=pedido.de_usuario, amigo=pedido.para_usuario)
        Amigo.objects.create(usuario=pedido.para_usuario, amigo=pedido.de_usuario)
        messages.success(request, f'Você agora é amigo de {pedido.de_usuario.nome_usuario}!')
    
    return redirect('home:listar_amigos') # Redireciona para a pág. de abas


@login_required
def recusar_remover_amizade(request, pedido_id): 
    """
    Recusa um pedido pendente (deleta o PedidoAmizade).
    Não mexe no modelo Amigo, pois a amizade não existia.
    """
    # Só pode recusar pedidos enviados PARA você
    pedido = get_object_or_404(PedidoAmizade, pk=pedido_id, para_usuario=request.user)
    
    if pedido.status == 'pendente':
        nome_removido = pedido.de_usuario.nome_usuario
        pedido.delete()
        messages.info(request, f'Pedido de {nome_removido} recusado.') 
    else:
        messages.error(request, 'Não foi possível recusar este pedido.')
         
    return redirect('home:listar_amigos') # Redireciona para a pág. de abas


@login_required
def listar_amigos(request):
    """
    Busca DUAS listas (Amigos e Pedidos Pendentes) e envia 
    ambas para o template 'amigos.html' (página de abas).
    """
    # 1. Lista de Amigos
    amizades = request.user.amigos.select_related('amigo')
    lista_de_amigos = [amizade.amigo for amizade in amizades]
    
    # 2. Lista de Pedidos Pendentes
    pedidos_pendentes = PedidoAmizade.objects.filter(para_usuario=request.user, status='pendente')

    contexto = {
        'amigos': lista_de_amigos,
        'pedidos': pedidos_pendentes
    }
    return render(request, 'home/amigos/amigos.html', contexto)


@login_required
def remover_amigo(request, amigo_username):
    """
    Remove uma amizade existente (deleta dos dois lados 
    no modelo Amigo) e deleta o PedidoAmizade.
    """
    if request.method == 'POST':
        try:
            amigo = Usuario.objects.get(nome_usuario=amigo_username)

            if amigo == request.user:
                 messages.error(request, 'Você não pode remover a si mesmo.')
                 return redirect('home:listar_amigos')

            # Deleta a relação de amizade
            Amigo.objects.filter(usuario=request.user, amigo=amigo).delete()
            Amigo.objects.filter(usuario=amigo, amigo=request.user).delete()

            # Encontra e deleta o PedidoAmizade que originou a amizade
            pedido_amizade = PedidoAmizade.objects.filter(
                (Q(de_usuario=request.user) & Q(para_usuario=amigo)) |
                (Q(de_usuario=amigo) & Q(para_usuario=request.user))
            ).first()

            if pedido_amizade:
                pedido_amizade.delete() 

            messages.success(request, f'Você não é mais amigo de {amigo.nome_usuario}.')
        
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro: {e}')
        
        return redirect('home:listar_amigos')
    else:
        messages.warning(request, 'Ação não permitida.')
        return redirect('home:listar_amigos')

@login_required
def ver_perfil_usuario(request, nome_usuario):
    """
    Mostra um "perfil público" de um usuário, 
    com suas estatísticas e barra de XP.
    """
    try:
        usuario_alvo = Usuario.objects.get(nome_usuario=nome_usuario)
        
        # 1. Calcular Estatísticas
        
        # Tarefas Totais (do seu models.py)
        tarefas_totais = (
            usuario_alvo.tarefas_concluidas_prazo_count + 
            usuario_alvo.tarefas_concluidas_atrasadas_count
        )
        
        # Tarefas na Semana
        hoje = timezone.now()
        uma_semana_atras = hoje - timedelta(days=7)
        
        # --- AQUI ESTÁ A CORREÇÃO ---
        # Trocamos status='concluida' por concluida=True,
        # que é o nome do campo no seu modelo Tarefa.
        tarefas_semana = Tarefa.objects.filter(
            usuario=usuario_alvo,
            concluida=True, # <-- CORRIGIDO
            data_conclusao__gte=uma_semana_atras
        ).count()
        
        # Frequência (dos dias_foco)
        frequencia = usuario_alvo.dias_foco

        # 2. Preparar contexto para o template
        contexto = {
            'perfil': usuario_alvo,
            'tarefas_totais': tarefas_totais,
            'tarefas_semana': tarefas_semana,
            'frequencia': frequencia
        }
        
        return render(request, 'home/amigos/perfil_usuario.html', contexto)

    except Usuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado.')
        return redirect('home:listar_amigos')
    except Exception as e:
        # Pega outros erros (ex: se data_conclusao não existir)
        logger.error(f"Erro ao ver perfil de {nome_usuario}: {e}")
        messages.error(request, 'Não foi possível carregar o perfil.')
        return redirect('home:listar_amigos')