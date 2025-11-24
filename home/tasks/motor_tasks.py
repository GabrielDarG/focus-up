# home/tasks/motor_tasks.py

import logging
import random
import threading 
from datetime import datetime, time 
from django.utils import timezone
from django.db.models import F
from ..models import Tarefa, Usuario, UsuarioFoco
from ..ai_engine import FocusAIEngine 

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

DIAS_DA_SEMANA_MAP = {
    0: 'recorrente_seg', 1: 'recorrente_ter', 2: 'recorrente_qua',
    3: 'recorrente_qui', 4: 'recorrente_sex', 5: 'recorrente_sab',
    6: 'recorrente_dom',
}

DIAS_DA_SEMANA_STR = {
    0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira',
    3: 'Quinta-feira', 4: 'Sexta-feira', 5: 'Sábado',
    6: 'Domingo',
}

def processar_slots_diarios(usuario: Usuario):
    """
    O "motor" principal. 
    """
    usuario.refresh_from_db()

    logger.info(f"Processando 'motor' para: {usuario.email}")

    if not UsuarioFoco.objects.filter(user=usuario).exists():
        logger.info(f"Usuário {usuario.email} não tem focos. Abortando geração IA.")
        return
    
    slots_foram_resetados = usuario.verificar_e_resetar_slots_diarios()
    
    deve_processar = slots_foram_resetados
    
    if not slots_foram_resetados:
        if usuario.slots_tarefas_ia_usados == 0:
            logger.warning(f"Slots já resetados, mas IA está zerada (0/{Usuario.LIMITE_SLOTS_IA}). Forçando nova tentativa...")
            deve_processar = True
        else:
            logger.info(f"Slots para {usuario.email} já foram processados e já existem tarefas. Pulando.")
            deve_processar = False
    
    if deve_processar:
        logger.info(f"HORA DO SORTEIO E GERAÇÃO para {usuario.email}...")

        agora = timezone.localtime(timezone.now())
        HORA_CORTE = usuario.HORA_CORTE_RESET
        
        dia_alvo = None 
        if agora.time() >= HORA_CORTE:
            logger.info(f"Corte ({HORA_CORTE}) já passou. Gerando tarefas de AMANHÃ.")
            dia_alvo = agora.date() + timezone.timedelta(days=1)
        else:
            logger.info(f"Corte ({HORA_CORTE}) ainda não passou. Gerando tarefas de HOJE.")
            dia_alvo = agora.date()
            
        dia_da_semana_int = dia_alvo.weekday() 
        
        # Sorteio Manual
        if usuario.slots_tarefas_pessoais_usados == 0:
            processar_sorteio_manual(usuario, dia_da_semana_int)
        
        # Geração IA
        if usuario.slots_tarefas_ia_usados < Usuario.LIMITE_SLOTS_IA:
            logger.info(f"[Motor IA] Disparando thread de geração (Paralela) para {usuario.email}...")
            thread_ia = threading.Thread(
                target=processar_geracao_ia_paralela, 
                args=(usuario, dia_da_semana_int),
                daemon=True
            )
            thread_ia.start()
        else:
            logger.info("[Motor IA] Limite de IA já atingido. Não gerando.")

    # Reset de tarefas antigas
    inicio_dia_de_jogo_atual = usuario.get_inicio_dia_de_jogo_atual()
    tarefas_para_falhar = Tarefa.objects.filter(
        usuario=usuario,
        tipo_tarefa__in=['PESSOAL', 'IA_DIARIA'], 
        concluida=False, falhou=False, descartada=False,
        data_criacao__lt=inicio_dia_de_jogo_atual 
    )
    count_falhadas = tarefas_para_falhar.update(falhou=True, xp=0)
    if count_falhadas > 0:
        logger.info(f"RESET: {count_falhadas} tarefas antigas marcadas como 'Falhou' para {usuario.email}.")


def processar_sorteio_manual(usuario: Usuario, dia_da_semana_int: int):
    logger.info(f"[Motor Manual] Iniciando sorteio para {usuario.email}...")
    campo_dia = DIAS_DA_SEMANA_MAP.get(dia_da_semana_int)
    if not campo_dia:
        logger.error(f"[Motor Manual] Não foi possível encontrar o dia da semana para {dia_da_semana_int}")
        return
    templates_para_hoje = Tarefa.objects.filter(
        usuario=usuario, tipo_tarefa='TEMPLATE_PESSOAL', **{campo_dia: True}
    )
    templates_list = list(templates_para_hoje)
    logger.info(f"[Motor Manual] Encontrados {len(templates_list)} templates para {usuario.email} para o dia '{campo_dia}'.")

    limite_slots = usuario.get_limite_tarefas_pessoais()
    
    k = min(len(templates_list), limite_slots) 
    if k > 0:
        templates_sorteados = random.sample(templates_list, k=k)
        logger.info(f"[Motor Manual] Sorteando {k} tarefas para {usuario.email}...")
        
        novas_tarefas_criadas = []
        for template in templates_sorteados:
            ja_existe = Tarefa.objects.filter(
                usuario=usuario, 
                titulo=template.titulo, 
                tipo_tarefa='PESSOAL',
                data_criacao__date=timezone.now().date()
            ).exists()
            
            if not ja_existe:
                nova_tarefa_pessoal = Tarefa.objects.create(
                    usuario=usuario, tipo_tarefa='PESSOAL', titulo=template.titulo,
                    descricao=template.descricao, foco=template.foco, 
                    xp=template.xp_original or 10, xp_original=template.xp_original or 10,
                    concluida=False, falhou=False
                )
                novas_tarefas_criadas.append(nova_tarefa_pessoal)
        
        if novas_tarefas_criadas:
            usuario.slots_tarefas_pessoais_usados += len(novas_tarefas_criadas)
            usuario.save(update_fields=['slots_tarefas_pessoais_usados'])
            logger.info(f"[Motor Manual] {len(novas_tarefas_criadas)} tarefas PESSOAIS criadas para {usuario.email}.")
    else:
        logger.info(f"[Motor Manual] Nenhum template de tarefa pessoal para sortear para {usuario.email}.")


def gerar_e_salvar_tarefa_ia_worker(usuario: Usuario, foco_obj: UsuarioFoco, dia_str: str, thread_index: int):
    try:
        usuario_check = Usuario.objects.get(pk=usuario.pk)
        if usuario_check.slots_tarefas_ia_usados >= Usuario.LIMITE_SLOTS_IA:
            logger.warning(f"[Motor IA Worker {thread_index}] Limite atingido durante execução concorrente. Abortando.")
            return

        logger.info(f"[Motor IA Worker {thread_index}] Iniciado. Gerando para Foco: {foco_obj.foco_nome}...")
        engine = FocusAIEngine()
        perfil_dict = {
            "foco_nome": foco_obj.foco_nome,
            "dados_especificos": foco_obj.dados_especificos,
            "detalhes": foco_obj.detalhes,
            "dia_da_semana": dia_str
        }
        sugestao = engine.gerar_sugestao_tarefa_diaria(perfil_dict)
        if sugestao:
            if Usuario.objects.filter(pk=usuario.pk, slots_tarefas_ia_usados__lt=Usuario.LIMITE_SLOTS_IA).exists():
                Tarefa.objects.create(
                    usuario=usuario,
                    tipo_tarefa='IA_DIARIA', 
                    titulo=sugestao.titulo,
                    descricao=sugestao.descricao_motivacional,
                    foco=foco_obj,
                    xp=sugestao.xp_calculado,
                    xp_original=sugestao.xp_calculado,
                    concluida=False,
                    falhou=False
                )
                usuario_db = Usuario.objects.get(pk=usuario.pk)
                usuario_db.slots_tarefas_ia_usados = F('slots_tarefas_ia_usados') + 1
                usuario_db.save(update_fields=['slots_tarefas_ia_usados'])
                logger.info(f"[Motor IA Worker {thread_index}] SUCESSO. Tarefa '{sugestao.titulo}' criada.")
            else:
                logger.warning(f"[Motor IA Worker {thread_index}] Limite atingido no último segundo. Tarefa descartada.")
        else:
            logger.warning(f"[Motor IA Worker {thread_index}] IA falhou em gerar sugestão para o foco {foco_obj.foco_nome}.")
    except Exception as e:
        logger.exception(f"[Motor IA Worker {thread_index}] FALHA CRÍTICA na thread. {e}")

def processar_geracao_ia_paralela(usuario: Usuario, dia_da_semana_int: int):
    logger.info(f"[Motor IA Paralelo] Thread principal iniciada. Gerando para {usuario.email}...")
    
    usuario_atualizado = Usuario.objects.get(pk=usuario.pk)
    
    perfis_foco = list(UsuarioFoco.objects.filter(user=usuario_atualizado))
    dia_str = DIAS_DA_SEMANA_STR.get(dia_da_semana_int, "hoje")
    
    if not perfis_foco:
        logger.warning(f"[Motor IA Paralelo] Usuário {usuario.email} não tem Perfis de Foco. Thread terminando.")
        return
        
    num_ja_geradas = usuario_atualizado.slots_tarefas_ia_usados
    num_para_gerar = Usuario.LIMITE_SLOTS_IA - num_ja_geradas
    
    if num_para_gerar <= 0:
         logger.info(f"[Motor IA Paralelo] Tarefas já foram completadas por outra thread ou processo.")
         return

    focos_para_gerar = []
    
    temp_perfis = perfis_foco.copy()
    while len(focos_para_gerar) < num_para_gerar:
        if not temp_perfis: 
            temp_perfis = perfis_foco.copy()
        
        foco_sorteado = random.choice(temp_perfis)
        focos_para_gerar.append(foco_sorteado)
        try:
            temp_perfis.remove(foco_sorteado)
        except ValueError:
            pass 

    logger.info(f"[Motor IA Paralelo] Disparando {len(focos_para_gerar)} threads 'worker'...")
    for i, foco_obj in enumerate(focos_para_gerar):
        t = threading.Thread(
            target=gerar_e_salvar_tarefa_ia_worker,
            args=(usuario, foco_obj, dia_str, i + 1),
            daemon=True
        )
        t.start() 

    logger.info(f"[Motor IA Paralelo] Todas as {len(focos_para_gerar)} threads disparadas. Thread principal terminando.")