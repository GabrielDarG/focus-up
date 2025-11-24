# home/views/usuario_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.contrib.auth import login

# --- NOVAS IMPORTAÇÕES ---
from django.utils import timezone
from datetime import datetime, timedelta, time
from django.http import JsonResponse
from django.db.models import Q, Count 

# --- IMPORTAÇÕES PARA GRÁFICOS (MATPLOTLIB) ---
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import numpy as np 
from collections import Counter
# ----------------------------------------------

try:
    from ..forms import UsuarioCadastroForm
    from ..forms import UsuarioEditarPerfilForm 
except ImportError:
    from ..forms.usuario_forms import UsuarioCadastroForm
    from ..forms.usuario_forms import UsuarioEditarPerfilForm
from ..forms.perfil_forms import UsuarioFocoForm

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from decimal import Decimal

from ..models.usuario_foco import UsuarioFoco
from ..models import Usuario
from ..models.loja import InventarioUsuario
from ..models.tarefa import Tarefa
from ..models.amigo import Amigo

# IMPORT DO FEEDBACK IA
from ..ai_feedback import gerar_feedback_focus_ai

import logging
logger = logging.getLogger(__name__)


# --- FUNÇÕES ORIGINAIS DO USUÁRIO ---

def index(request):
    if request.user.is_authenticated:
        return redirect('home:home')
    return render(request, 'home/index.html')

@login_required
def home(request):
    user = request.user
    
    qtd_congelador_antes = 0
    item_congelador = InventarioUsuario.objects.filter(usuario=user, item__tipo_efeito='CONGELADOR').first()
    if item_congelador:
        qtd_congelador_antes = item_congelador.quantidade

    user.verificar_manutencao_ofensiva()
    
    if item_congelador:
        item_congelador.refresh_from_db()
        if item_congelador.quantidade < qtd_congelador_antes:
            messages.info(request, f"Ufa! Congelador de Ofensiva utilizado com sucesso. Sua sequência de {user.dias_foco} dias foi salva!", extra_tags='popup-congelador')

    now = timezone.now()
    HORA_CORTE = time(22, 0, 0)

    if now.time() < HORA_CORTE:
        inicio_dia_foco_atual = now.replace(hour=22, minute=0, second=0, microsecond=0) - timedelta(days=1)
    else:
        inicio_dia_foco_atual = now.replace(hour=22, minute=0, second=0, microsecond=0)

    inicio_dia_foco_anterior = inicio_dia_foco_atual - timedelta(days=1)

    ultimo_resgate = user.ultimo_resgate_foco
    pode_resgatar = True

    if ultimo_resgate is not None:
        if ultimo_resgate >= inicio_dia_foco_atual:
            pode_resgatar = False

    context = {
        'pode_resgatar': pode_resgatar,
        'nivel_usuario': user.nivel,
        'xp_usuario': user.xp_atual,
        'xp_necessario': user.xp_proximo_nivel,
    }
    return render(request, 'home/home.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                nome_display = getattr(user, 'nome_usuario', user.email)
                messages.success(request, f'Bem-vindo de volta, {nome_display}!')
                return redirect('home:home')
            else:
                messages.error(request, 'Nome de usuário ou senha inválidos.')
        else:
            first_error = next(iter(form.errors.values()), ["Nome de usuário ou senha inválidos."])[0]
            messages.error(request, first_error)
    else:
        form = AuthenticationForm()
    return render(request, 'home/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('home:index')


def cadastro(request):
    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        form = UsuarioCadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            backend_path = settings.AUTHENTICATION_BACKENDS[0]
            login(request, user, backend=backend_path)
            messages.success(request, 'Cadastro realizado com sucesso! Bem-vindo(a)!')
            return redirect('home:home')
        else:
            first_error = next(iter(form.errors.values()))[0] if form.errors else "Erro no cadastro."
            messages.error(request, f"Erro no cadastro: {first_error}")
    else:
        form = UsuarioCadastroForm()
    return render(request, 'home/cadastro.html', {'form': form})


def termos(request):
    return render(request, 'home/termosdeuso.html')

@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = UsuarioEditarPerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home:editar_perfil') 
        else:
            messages.error(request, 'Erro ao atualizar o perfil. Verifique os campos.')
    else:
        form = UsuarioEditarPerfilForm(instance=request.user)

    context = {
        'form': form
    }
    return render(request, 'home/editar_perfil.html', context)

@login_required
def gerenciar_meu_perfil(request):
    perfis_atuais = UsuarioFoco.objects.filter(user=request.user).order_by('foco_nome')
    perfis_atuais_dict = {}
    for perfil in perfis_atuais:
        dados_js = perfil.dados_especificos if isinstance(perfil.dados_especificos, dict) else {}
        for key, value in dados_js.items():
            if isinstance(value, Decimal):
                dados_js[key] = str(value) 
        perfis_atuais_dict[perfil.foco_nome] = {
            'foco_nome': perfil.foco_nome,
            'dados_especificos': dados_js,
            'detalhes': perfil.detalhes
        }

    if request.method == 'POST':
        foco_nome_post = request.POST.get('foco_nome')
        if not foco_nome_post:
            messages.error(request, "O campo 'Qual é o Foco?' é obrigatório.")
            form = UsuarioFocoForm()
            context = { 'perfis_atuais': perfis_atuais, 'form': form, 'perfis_atuais_dict': perfis_atuais_dict }
            return render(request, 'home/perfil usuario/meu_perfil.html', context)

        instance_existente = UsuarioFoco.objects.filter(user=request.user, foco_nome=foco_nome_post).first()
        form = UsuarioFocoForm(request.POST, instance=instance_existente)

        if form.is_valid():
            try:
                foco_selecionado = form.cleaned_data['foco_nome']
                dados_especificos_para_salvar = {}

                if hasattr(form, 'campos_especificos_map'):
                    campos_deste_foco = form.campos_especificos_map.get(foco_selecionado, [])
                    for campo in campos_deste_foco:
                        valor = form.cleaned_data.get(campo)
                        if valor is not None and valor != '':
                            if isinstance(valor, Decimal):
                                dados_especificos_para_salvar[campo] = str(valor)
                            else:
                                dados_especificos_para_salvar[campo] = valor

                perfil, criado = UsuarioFoco.objects.update_or_create(
                    user=request.user,
                    foco_nome=foco_selecionado,
                    defaults={
                        'dados_especificos': dados_especificos_para_salvar,
                        'detalhes': form.cleaned_data['detalhes']
                    }
                )

                if criado:
                    messages.success(request, f"Novo foco '{foco_selecionado}' salvo com sucesso!")
                else:
                    messages.success(request, f"Foco '{foco_selecionado}' atualizado com sucesso!")

                return redirect('home:meu_perfil')

            except Exception as e:
                logger.exception(f"Erro ao salvar UsuarioFocoForm manually:")
                messages.error(request, f"Ocorreu um erro inesperado ao salvar: {e}")

        else: 
            logger.warning(f"UsuarioFocoForm inválido: {form.errors.as_json()}")
            messages.error(request, "Erro ao salvar. Verifique os campos.")

    else:
        form = UsuarioFocoForm()

    context = {
        'perfis_atuais': perfis_atuais,
        'form': form, 
        'perfis_atuais_dict': perfis_atuais_dict
    }
    return render(request, 'home/perfil usuario/meu_perfil.html', context)


@login_required
def resgatar_foco(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método inválido.'}, status=405)

    user = request.user
    now = timezone.now()

    HORA_CORTE = time(22, 0, 0)
    if now.time() < HORA_CORTE:
        inicio_dia_foco_atual = now.replace(hour=22, minute=0, second=0, microsecond=0) - timedelta(days=1)
    else:
        inicio_dia_foco_atual = now.replace(hour=22, minute=0, second=0, microsecond=0)

    ultimo_resgate = user.ultimo_resgate_foco

    if ultimo_resgate is not None and ultimo_resgate >= inicio_dia_foco_atual:
        return JsonResponse({'success': False, 'message': 'Você já resgatou seu foco hoje.'}, status=400)

    inicio_dia_foco_anterior = inicio_dia_foco_atual - timedelta(days=1)
    if ultimo_resgate is not None and ultimo_resgate < inicio_dia_foco_anterior:
        user.dias_foco = 0 

    user.adicionar_moedas(100) 
    user.adicionar_xp(20)
    user.dias_foco += 1
    user.ultimo_resgate_foco = now

    user.save(update_fields=[
        'dias_foco', 'xp_atual', 'ultimo_resgate_foco', 'nivel', 'xp_proximo_nivel', 'moedas'
    ])

    return JsonResponse({
        'success': True,
        'dias_foco': user.dias_foco,
        'xp_atual': user.xp_atual,
        'nivel': user.nivel,
        'xp_proximo_nivel': user.xp_proximo_nivel,
        'moedas': user.moedas, 
    })


# --- GERAÇÃO DOS GRÁFICOS ---

def gerar_grafico_focos(usuario):
    dados = Tarefa.objects.filter(usuario=usuario, concluida=True).exclude(foco__isnull=True).values('foco__foco_nome').annotate(total=Count('id_Tarefa')).order_by('-total')
    if not dados: return None
    nomes = [d['foco__foco_nome'] for d in dados]
    valores = [d['total'] for d in dados]
    nomes = [nome.capitalize() for nome in nomes]
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor('#2a2f42')
    ax.set_facecolor('#2a2f42')
    barras = ax.bar(nomes, valores, color='#5a48f5', width=0.6, zorder=3)
    ax.set_title('Tarefas Concluídas por Foco', color='#f8f9fa', fontsize=14, pad=15, fontweight='bold')
    ax.set_ylabel('Quantidade', color='#a9b1d6')
    ax.tick_params(axis='x', colors='#a9b1d6', rotation=0)
    ax.tick_params(axis='y', colors='#a9b1d6')
    ax.grid(axis='y', linestyle='--', alpha=0.2, zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#343b58')
    ax.spines['left'].set_color('#343b58')
    for barra in barras:
        height = barra.get_height()
        ax.annotate(f'{height}', xy=(barra.get_x() + barra.get_width() / 2, height), xytext=(0, 5), textcoords="offset points", ha='center', va='bottom', color='#ffc93e', fontweight='bold')
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', transparent=False)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close(fig)
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    return graphic

def gerar_grafico_semana_rosca(usuario):
    tarefas_datas = Tarefa.objects.filter(usuario=usuario, concluida=True).values_list('data_conclusao', flat=True)
    if not tarefas_datas: return None
    dias_nomes = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    dias_contagem = [0] * 7
    for data in tarefas_datas:
        if data: dias_contagem[timezone.localtime(data).weekday()] += 1
    if sum(dias_contagem) == 0: return None
    labels = []
    sizes = []
    paleta_cores = ['#5a48f5', '#ffc93e', '#00d2d3', '#7bed9f', '#ff6b6b', '#7b2cbf', '#34495e']
    colors = []
    for i in range(7):
        if dias_contagem[i] > 0:
            labels.append(dias_nomes[i])
            sizes.append(dias_contagem[i])
            colors.append(paleta_cores[i % len(paleta_cores)])
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(7, 5))
    fig.patch.set_facecolor('#2a2f42')
    ax.set_facecolor('#2a2f42')
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, pctdistance=0.85, textprops=dict(color="#f8f9fa"), wedgeprops=dict(width=0.4, edgecolor='#2a2f42'))
    plt.setp(texts, size=10, weight="bold")
    plt.setp(autotexts, size=9, weight="bold", color="#2a2f42") 
    ax.set_title('Distribuição Semanal', color='#f8f9fa', fontsize=14, pad=15, fontweight='bold')
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', transparent=True)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close(fig)
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    return graphic

def como_usar_view(request):
    return render(request, 'home/como_usar.html')

def gerar_grafico_radar_turnos(usuario):
    tarefas_datas = Tarefa.objects.filter(usuario=usuario, concluida=True).values_list('data_conclusao', flat=True)
    if not tarefas_datas: return None
    categorias = ['Madrugada', 'Manhã', 'Tarde', 'Noite']
    contagem = [0, 0, 0, 0]
    for data in tarefas_datas:
        if data:
            hora = timezone.localtime(data).hour
            if 0 <= hora < 6: contagem[0] += 1
            elif 6 <= hora < 12: contagem[1] += 1
            elif 12 <= hora < 18: contagem[2] += 1
            else: contagem[3] += 1
    if sum(contagem) == 0: return None
    N = len(categorias)
    angulos = [n / float(N) * 2 * np.pi for n in range(N)]
    angulos += angulos[:1] 
    contagem += contagem[:1] 
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor('#2a2f42')
    ax.set_facecolor('#2a2f42')
    ax.plot(angulos, contagem, color='#00d2d3', linewidth=2, linestyle='solid')
    ax.fill(angulos, contagem, color='#00d2d3', alpha=0.25)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias, color='#f8f9fa', size=11, weight='bold')
    ax.yaxis.grid(True, color='#343b58', linestyle='--')
    ax.xaxis.grid(True, color='#343b58')
    ax.set_yticklabels([])
    ax.set_title("Turnos de Produtividade", color='#f8f9fa', size=14, weight='bold', pad=20)
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', transparent=True)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close(fig)
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    return graphic


# --- API PARA GERAR REVIEW (AJAX) ATUALIZADA ---
@login_required
def api_gerar_review_ia(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método inválido'}, status=405)
    
    try:
        # Chama a função que usa o motor de IA
        feedback_ia = gerar_feedback_focus_ai(request.user)
        
        return JsonResponse({
            'success': True,
            'texto': feedback_ia.get('texto', ''),
            'humor': feedback_ia.get('humor', 'bom'),
            'dica': feedback_ia.get('dica', '') # Inclui a Dica no JSON
        })
    except Exception as e:
        logger.exception("Erro ao gerar review na API")
        return JsonResponse({'success': False, 'error': 'Erro interno na IA.'}, status=500)


# --- VIEW DE ESTATÍSTICAS (PRINCIPAL) ---
@login_required
def estatisticas_view(request):
    usuario = request.user
    
    total_concluidas = usuario.tarefas_concluidas_prazo_count + usuario.tarefas_concluidas_atrasadas_count
    
    foco_principal_query = Tarefa.objects.filter(usuario=usuario, concluida=True).exclude(foco__isnull=True).values('foco__foco_nome').annotate(total=Count('id_Tarefa')).order_by('-total').first()
    foco_principal_nome = "Nenhum"
    if foco_principal_query:
        foco_principal_nome = foco_principal_query['foco__foco_nome'].capitalize()

    concluidas_atraso = usuario.tarefas_concluidas_atrasadas_count
    streak = usuario.dias_foco
    descartadas = usuario.tarefas_descartadas_count

    grafico_focos = gerar_grafico_focos(usuario)
    grafico_rosca = gerar_grafico_semana_rosca(usuario)
    grafico_radar = gerar_grafico_radar_turnos(usuario)

    amigos_ids = []
    try:
        amigos_1 = Amigo.objects.filter(usuario=usuario).values_list('amigo_id', flat=True)
        amigos_2 = Amigo.objects.filter(amigo=usuario).values_list('usuario_id', flat=True)
        amigos_ids = list(set(list(amigos_1) + list(amigos_2)))
        top_amigos = Usuario.objects.filter(pk__in=amigos_ids).order_by('-xp_atual')[:3]
    except Exception as e:
        logger.error(f"Erro ranking: {e}")
        top_amigos = []

    context = {
        'total_concluidas': total_concluidas,
        'foco_principal': foco_principal_nome,
        'concluidas_atraso': concluidas_atraso,
        'streak': streak,
        'descartadas': descartadas,
        'top_amigos': top_amigos,
        'grafico_focos': grafico_focos,
        'grafico_rosca': grafico_rosca, 
        'grafico_radar': grafico_radar, 
    }
    
    return render(request, 'home/tarefas/estatisticas.html', context)