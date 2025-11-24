# home/ai_feedback.py

from .models import Usuario, Tarefa
from .ai_engine import FocusAIEngine

def gerar_feedback_focus_ai(usuario: Usuario):
    """
    Coleta dados e chama o FocusAIEngine para gerar um review real.
    """
    
    # Coleta os Dados do Banco
    nome = usuario.nome.split()[0] if usuario.nome else usuario.nome_usuario
    
    # Estatísticas brutas
    concluidas = usuario.tarefas_concluidas_prazo_count + usuario.tarefas_concluidas_atrasadas_count
    descartadas = usuario.tarefas_descartadas_count
    streak = usuario.dias_foco
    nivel = usuario.nivel
    xp = usuario.xp_atual
    
    # Monta o dicionário para a IA ler
    dados_para_ia = {
        "nome_usuario": nome,
        "nivel": nivel,
        "xp_atual": xp,
        "dias_foco_streak": streak,
        "total_tarefas_concluidas": concluidas,
        "total_tarefas_descartadas": descartadas,
        "taxa_sucesso": f"{(concluidas / (concluidas + descartadas) * 100):.1f}%" if (concluidas + descartadas) > 0 else "0%"
    }
    
    # Chama a IA Real (Ollama)
    engine = FocusAIEngine()
    review = engine.gerar_review_estatistico(dados_para_ia)
    
    return review