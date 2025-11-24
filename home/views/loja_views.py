# home/views/loja_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
import datetime
from ..models.loja import ItemLoja, Compra, InventarioUsuario
from ..models.usuario import Usuario

def get_preco_slot_extra(usuario):
    inv_slot = InventarioUsuario.objects.filter(usuario=usuario, item__tipo_efeito='SLOT_EXTRA').first()
    qtd_atual = inv_slot.quantidade if inv_slot else 0
    if qtd_atual == 0: return 500
    if qtd_atual == 1: return 1000
    if qtd_atual == 2: return 2000
    return None 

def garantir_moldura_padrao(usuario):
    try:
        moldura_padrao = ItemLoja.objects.filter(tipo_efeito='MOLDURA', classe_css='moldura-padrao').first()
        if moldura_padrao:
            if not InventarioUsuario.objects.filter(usuario=usuario, item=moldura_padrao).exists():
                InventarioUsuario.objects.create(
                    usuario=usuario, item=moldura_padrao, quantidade=1, esta_ativo=True
                )
    except Exception:
        pass

@login_required
def loja_view(request):
    garantir_moldura_padrao(request.user)
    todos_itens = ItemLoja.objects.exclude(classe_css='moldura-padrao')
    
    inventario_map = {
        inv.item_id: inv 
        for inv in InventarioUsuario.objects.filter(usuario=request.user)
    }

    lista_upgrades = []
    lista_customizacao = []
    lista_cores = []

    for item in todos_itens:
        # Inicializa o atributo para evitar erro na ordenação depois
        item.esgotado_maximo = False 
        
        if item.tipo_efeito == 'SLOT_EXTRA':
            novo_preco = get_preco_slot_extra(request.user)
            if novo_preco is None:
                item.esgotado_maximo = True
            else:
                item.preco = novo_preco 
        
        item.no_inventario = inventario_map.get(item.id)
        
        if item.tipo_efeito in ['XP_BOOST', 'SLOT_EXTRA', 'CONGELADOR']:
            lista_upgrades.append(item)
        elif item.tipo_efeito in ['MOLDURA', 'AVATAR']:
            lista_customizacao.append(item)
        elif item.tipo_efeito == 'COR_BORDA':
            lista_cores.append(item)

    def criterio_ordem(x):
        tem_item = x.no_inventario is not None
        # Agora x.esgotado_maximo sempre existe (é False por padrão), então não dá erro
        if x.tipo_efeito == 'SLOT_EXTRA' and not getattr(x, 'esgotado_maximo', False):
            tem_item = False
        return (tem_item, x.preco)

    lista_upgrades.sort(key=criterio_ordem)
    lista_customizacao.sort(key=criterio_ordem)
    lista_cores.sort(key=criterio_ordem)

    context = {
        'secao_upgrades': lista_upgrades,
        'secao_customizacao': lista_customizacao,
        'secao_cores': lista_cores,
        'moedas_usuario': request.user.moedas,
        'agora': timezone.now()
    }
    return render(request, 'home/loja/loja.html', context)

@login_required
def comprar_item(request, item_id):
    if request.method != 'POST':
        return redirect('home:loja_view')

    item = get_object_or_404(ItemLoja, pk=item_id)
    usuario = request.user
    
    preco_final = item.preco
    if item.tipo_efeito == 'SLOT_EXTRA':
        preco_dinamico = get_preco_slot_extra(usuario)
        if preco_dinamico is None:
            messages.error(request, "Máximo atingido!")
            return redirect('home:loja_view')
        preco_final = preco_dinamico

    if usuario.moedas < preco_final:
        messages.error(request, f"Faltam {preco_final - usuario.moedas} moedas.")
        return redirect('home:loja_view')

    bloquear_compra = False
    tipos_unicos = ['SLOT_EXTRA', 'MOLDURA', 'AVATAR', 'COR_BORDA']
    if item.tipo_efeito in tipos_unicos:
         if InventarioUsuario.objects.filter(usuario=usuario, item=item).exists():
             bloquear_compra = True
    
    if item.tipo_efeito == 'XP_BOOST':
        if InventarioUsuario.objects.filter(usuario=usuario, item=item, quantidade__gt=0).exists():
             bloquear_compra = True

    if not item.eh_consumivel and item.tipo_efeito not in tipos_unicos and item.tipo_efeito != 'XP_BOOST':
         if InventarioUsuario.objects.filter(usuario=usuario, item=item).exists():
             bloquear_compra = True

    if bloquear_compra:
        messages.warning(request, "Você já possui este item!")
        return redirect('home:loja_view')

    try:
        with transaction.atomic():
            usuario.adicionar_moedas(-preco_final) 
            item_inv, created = InventarioUsuario.objects.get_or_create(
                usuario=usuario,
                item=item,
                defaults={'quantidade': 0}
            )
            item_inv.quantidade += 1
            item_inv.save()
            Compra.objects.create(usuario=usuario, item=item, preco_pago=preco_final)

        messages.success(request, f"Compra realizada! '{item.nome}' adicionado.")

    except Exception as e:
        messages.error(request, "Erro na compra.")
        
    return redirect('home:loja_view')

@login_required
def ativar_item(request, item_id):
    if request.method != 'POST':
        return redirect('home:loja_view')
        
    item_inv = get_object_or_404(InventarioUsuario, item_id=item_id, usuario=request.user)
    
    # --- MOLDURA ---
    if item_inv.item.tipo_efeito == 'MOLDURA':
        InventarioUsuario.objects.filter(
            usuario=request.user, 
            item__tipo_efeito='MOLDURA'
        ).update(esta_ativo=False)
        
        item_inv.refresh_from_db()
        item_inv.esta_ativo = True
        item_inv.save()
        
        messages.success(request, f"Moldura '{item_inv.item.nome}' equipada!")
        return redirect('home:inventario_view')

    # --- COR DA BORDA (COM TOGGLE) ---
    elif item_inv.item.tipo_efeito == 'COR_BORDA':
        
        # MUDANÇA AQUI: Se já estiver ativo, desativa (remove)
        if item_inv.esta_ativo:
            item_inv.esta_ativo = False
            item_inv.save()
            messages.info(request, f"Cor '{item_inv.item.nome}' removida. Voltando ao padrão.")
            
        else:
            # Se não estiver ativo, desativa as outras e ativa essa
            InventarioUsuario.objects.filter(
                usuario=request.user, 
                item__tipo_efeito='COR_BORDA'
            ).update(esta_ativo=False)
            
            item_inv.refresh_from_db()
            item_inv.esta_ativo = True
            item_inv.save()
            messages.success(request, f"Cor '{item_inv.item.nome}' ativada!")
            
        return redirect('home:inventario_view')
        
    # --- AVATAR ---
    elif item_inv.item.tipo_efeito == 'AVATAR':
        InventarioUsuario.objects.filter(
            usuario=request.user, 
            item__tipo_efeito='AVATAR'
        ).update(esta_ativo=False)
        
        item_inv.refresh_from_db()
        item_inv.esta_ativo = True
        item_inv.save()
        
        messages.success(request, f"Avatar '{item_inv.item.nome}' equipado!")
        return redirect('home:inventario_view')
    
    if item_inv.quantidade <= 0:
        messages.error(request, "Você não possui este item.")
        return redirect('home:loja_view')
        
    if item_inv.item.tipo_efeito == 'XP_BOOST':
        agora = timezone.now()
        if item_inv.esta_ativo and item_inv.data_expiracao_efeito and item_inv.data_expiracao_efeito > agora:
             messages.warning(request, "Você já está com um Boost de XP ativo!")
             return redirect('home:loja_view')
        item_inv.quantidade -= 1 
        item_inv.esta_ativo = True
        item_inv.data_expiracao_efeito = agora + datetime.timedelta(hours=24)
        item_inv.save()
        messages.success(request, f"⚡ BOOST ATIVADO!")
        
    elif item_inv.item.tipo_efeito == 'CONGELADOR':
        messages.info(request, "❄️ Este item é Passivo! Ele ativa sozinho.")
        
    else:
        messages.info(request, "Este item não pode ser ativado manualmente.")

    return redirect('home:inventario_view')

@login_required
def inventario_view(request):
    garantir_moldura_padrao(request.user)

    molduras_ativas = InventarioUsuario.objects.filter(
        usuario=request.user, item__tipo_efeito='MOLDURA', esta_ativo=True
    )
    if molduras_ativas.count() > 1:
        molduras_ativas.update(esta_ativo=False)
        padrao = InventarioUsuario.objects.filter(usuario=request.user, item__classe_css='moldura-padrao').first()
        if padrao: 
            padrao.esta_ativo = True
            padrao.save()

    cores_ativas = InventarioUsuario.objects.filter(
        usuario=request.user, item__tipo_efeito='COR_BORDA', esta_ativo=True
    )
    if cores_ativas.count() > 1:
        cores_ativas.update(esta_ativo=False)

    meus_itens = InventarioUsuario.objects.filter(
        usuario=request.user
    ).filter(
        Q(quantidade__gt=0) | Q(esta_ativo=True)
    ).order_by('-item__preco') 
    
    context = {'meus_itens': meus_itens}
    return render(request, 'home/loja/inventario.html', context)