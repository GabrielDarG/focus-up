import requests
import json
from dataclasses import dataclass
from typing import List, Optional, Literal, Dict, Any
from .models.usuario_foco import UsuarioFoco 
import logging
import time

logger = logging.getLogger(__name__)

XP_POR_DIFICULDADE = {
    "facil": 10,
    "medio": 25,
    "dificil": 50,
    "hiperdificil": 100
}
DIFICULDADES_VALIDAS = ["facil", "medio", "dificil"] 

@dataclass
class TarefaSugerida:
    titulo: str
    descricao_motivacional: str
    dificuldade: Literal["facil", "medio", "dificil", "hiperdificil"]
    xp_calculado: int 
    foco: Optional[UsuarioFoco] = None

class FocusAIEngine:
    def __init__(self, model="llama3", timeout=180, max_retries=2):
        self.api_url = "http://localhost:11434/api/generate"
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logger
        self.logger.info(f"[FocusAIEngine] Motor de IA: modelo={self.model}, timeout={self.timeout}s, retries={self.max_retries}.")

    def _chamar_ollama(self, prompt: str) -> Optional[Dict[str, Any]]:
        payload = {"model": self.model, "prompt": prompt, "format": "json", "stream": False}
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    wait_time = 1.5 ** attempt
                    self.logger.warning(f"[FocusAIEngine] Tentativa {attempt + 1}/{self.max_retries + 1}...")
                    time.sleep(wait_time)
                self.logger.debug(f"[FocusAIEngine] Chamando Ollama (tentativa {attempt + 1})...")
                response = requests.post(self.api_url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                response_data = response.json()
                if 'response' in response_data:
                    try:
                        json_interno = json.loads(response_data['response'])
                        self.logger.debug(f"[FocusAIEngine] Ollama retornou JSON válido.")
                        return json_interno
                    except json.JSONDecodeError as json_err:
                        self.logger.error(f"[FocusAIEngine] Tentativa {attempt + 1}: Erro JSON: {json_err}")
                        self.logger.error(f"[FocusAIEngine] Resposta (string): {response_data['response']}")
                        last_exception = json_err
                else:
                    self.logger.error(f"[FocusAIEngine] Tentativa {attempt + 1}: Chave 'response' não encontrada.")
                    last_exception = ValueError("Chave 'response' não encontrada")
            except Exception as e:
                self.logger.error(f"[FocusAIEngine] Tentativa {attempt + 1}: Erro Inesperado: {e}")
                last_exception = e
        self.logger.error(f"[FocusAIEngine] Todas as {self.max_retries + 1} tentativas falharam.")
        if last_exception: self.logger.error(f"[FocusAIEngine] Último erro: {type(last_exception).__name__}: {last_exception}")
        return None


    def gerar_sugestao_tarefa_diaria(self, perfil_usuario: dict) -> Optional[TarefaSugerida]:
        instrucao_tipo = "Sugira UMA (1) MISSÃO DIÁRIA."
        num_sugestoes = 1
        prompt_geracao = f"""
        Você é o "FocusBuddy", um Mestre de Jogo (Game Master) criativo e encorajador. Sua missão é criar {num_sugestoes} "Missão Diária" (tarefa) para o jogador.

        **REGRA DE OURO: AÇÕES CONCRETAS E DETALHADAS!**
        * **NÃO** sugira tarefas vagas (Ex: "Estude", "Seja saudável", "Limpe a casa").
        * **SUGIRA AÇÕES** claras, com começo, meio e fim (Ex: "Escreva o rascunho do email X", "Complete a Lição Y", "Faça 3 séries de agachamento").
        * **NÃO** mencione o dia da semana (ex: "Hoje é terça-feira"), a menos que seja 100% essencial para a tarefa descrita no perfil.

        **PERFIL DO USUÁRIO (Sua fonte de ideias):**
        {json.dumps(perfil_usuario, ensure_ascii=False, indent=2)}

        **INSTRUÇÕES DE GERAÇÃO:**
        1.  Baseie-se 100% no Perfil do Usuário. Use o `foco_nome` e os `dados_especificos`.
        2.  **"titulo"**: Crie um nome de "Missão" curto e gamificado (Ex: "O Código do Mestre", "Fortalecendo o Core", "Hidratação Nível 1").
        3.  **"descricao_motivacional"**: Dê a ação concreta e detalhada. **A DESCRIÇÃO NÃO PODE SER VAGA.**
        4.  **"dificuldade"**: Classifique a ação como "facil" (< 15min), "medio" (15-40min), ou "dificil" (> 40min).

        **Retorne APENAS um objeto JSON com a chave "sugestoes"**, contendo uma lista com {num_sugestoes} missão(ões).
        Cada missão DEVE ter as chaves **"titulo"** (em português), **"descricao_motivacional"** (em português) e **"dificuldade"**.
        """
        try:
            self.logger.info(f"[FocusAIEngine] Gerando sugestão diária para foco '{perfil_usuario.get('foco_nome', 'N/A')}'...")
            resposta_json = self._chamar_ollama(prompt_geracao)
            if not resposta_json or "sugestoes" not in resposta_json or not isinstance(resposta_json["sugestoes"], list) or not resposta_json["sugestoes"]:
                self.logger.warning("[FocusAIEngine] IA não retornou sugestões válidas.")
                return None
            tarefa_data = resposta_json["sugestoes"][0]
            titulo = (tarefa_data.get("titulo") or tarefa_data.get("title") or tarefa_data.get("Título") or tarefa_data.get("Titulo"))
            desc = (tarefa_data.get("descricao_motivacional") or tarefa_data.get("description_motivacional") or tarefa_data.get("descrição_motivacional") or tarefa_data.get("descricao") or "")
            diff = tarefa_data.get("dificuldade", "facil").lower() 
            if not titulo or not isinstance(titulo, str) or desc is None or not isinstance(desc, str):
                self.logger.error(f"[FocusAIEngine] IA retornou dados incompletos: {tarefa_data}")
                return None
            if diff not in DIFICULDADES_VALIDAS:
                self.logger.warning(f"[FocusAIEngine] Dificuldade inválida '{diff}', usando 'facil'.")
                diff = "facil" 
            xp_calculado = XP_POR_DIFICULDADE.get(diff, 10) 
            sugestao = TarefaSugerida(titulo=titulo, descricao_motivacional=desc, dificuldade=diff, xp_calculado=xp_calculado, foco=None)
            self.logger.info(f"[FocusAIEngine] Sugestão gerada: '{sugestao.titulo}'")
            return sugestao
        except Exception as e:
            self.logger.exception(f"[FocusAIEngine] Erro na geração:")
            return None
    
    
    def gerar_pacote_tarefas_diarias(self, perfis_foco: List[UsuarioFoco], dia_da_semana: str, num_tarefas: int) -> List[TarefaSugerida]:
        perfis_dict_list = []
        foco_map = {} 
        for perfil in perfis_foco:
            perfis_dict_list.append({"foco_nome": perfil.foco_nome, "dados_especificos": perfil.dados_especificos, "detalhes": perfil.detalhes})
            foco_map[perfil.foco_nome.lower()] = perfil
        if not perfis_dict_list: return []
        
        prompt_geracao = f"""
        Você é o "FocusBuddy", um Mestre de Jogo (Game Master). Sua missão é criar {num_tarefas} "Missões Diárias" (tarefas) para o jogador.

        **PERFIS DE FOCO DO JOGADOR:**
        {json.dumps(perfis_dict_list, ensure_ascii=False, indent=2)}

        **INSTRUÇÕES DE GERAÇÃO:**
        1.  **Gere EXATAMENTE {num_tarefas} missões.**
        2.  **VARIE OS FOCOS!** Baseie cada tarefa em um dos perfis acima.
        3.  **SEJA CRIATIVO!** Sugira ações concretas e detalhadas.
        4.  **"foco_nome"**: Para CADA tarefa, inclua a chave "foco_nome" (Ex: "Academia", "Estudos"). Use o nome exato do perfil.
        5.  **"titulo"**: Crie um nome de "Missão" curto e gamificado.
        6.  **"descricao_motivacional"**: Ação concreta e detalhada.
        7.  **"dificuldade"**: "facil", "medio", ou "dificil".
        8.  **NÃO** mencione o dia da semana.

        **Retorne APENAS um objeto JSON com a chave "sugestoes"**, contendo uma lista com {num_tarefas} missões.
        Cada missão DEVE ter as chaves **"foco_nome"**, **"titulo"**, **"descricao_motivacional"**, e **"dificuldade"**.
        """
        try:
            self.logger.info(f"[FocusAIEngine] Gerando PACOTE de {num_tarefas} tarefas de IA...")
            resposta_json = self._chamar_ollama(prompt_geracao)
            if not resposta_json or "sugestoes" not in resposta_json or not isinstance(resposta_json["sugestoes"], list):
                return []
            tarefas_geradas = []
            for i, tarefa_data in enumerate(resposta_json["sugestoes"]):
                if i >= num_tarefas: break
                titulo = (tarefa_data.get("titulo") or tarefa_data.get("title"))
                desc = (tarefa_data.get("descricao_motivacional") or tarefa_data.get("descricao") or "")
                diff = tarefa_data.get("dificuldade", "facil").lower()
                foco_nome = tarefa_data.get("foco_nome")
                foco_obj = foco_map.get(foco_nome.lower()) if foco_nome else None
                
                if not all([titulo, foco_obj]) or desc is None: continue
                if diff not in DIFICULDADES_VALIDAS: diff = "facil"
                xp_calculado = XP_POR_DIFICULDADE.get(diff, 10)
                sugestao = TarefaSugerida(titulo=titulo, descricao_motivacional=desc, dificuldade=diff, xp_calculado=xp_calculado, foco=foco_obj)
                tarefas_geradas.append(sugestao)
            self.logger.info(f"[FocusAIEngine] Pacote de {len(tarefas_geradas)}/{num_tarefas} tarefas de IA gerado.")
            return tarefas_geradas
        except Exception as e:
            self.logger.exception(f"[FocusAIEngine] Erro na geração do PACOTE de IA:")
            return []


    def gerar_review_estatistico(self, dados_estatisticos: dict) -> dict:
        prompt = f"""
        Você é o "Focus AI", uma inteligência artificial analítica e motivadora de um app de produtividade gamificada.
        Sua função é analisar os dados do usuário e dar um feedback curto e uma dica prática.

        **DADOS DO USUÁRIO:**
        {json.dumps(dados_estatisticos, ensure_ascii=False, indent=2)}

        **INSTRUÇÕES:**
        1. **Analise os números:** Veja se a pessoa está indo bem (muitas tarefas concluídas, streak alto) ou mal (muitas descartadas, streak baixo).
        2. **Seja Gamificado:** Use termos como "Jogado", "Mestre", "XP", "Nível".
        3. **Tom de Voz:** Motivador, analítico, curto e direto.
        4. **Formato:** Retorne um JSON com TRÊS chaves:
           - "texto": Uma frase de impacto (máx 30 palavras) resumindo a análise.
           - "humor": Escolha entre "excelente", "bom" ou "critico".
           - "dica": Uma sugestão de AÇÃO curta (máx 15 palavras) para o usuário melhorar ou manter o ritmo. (Ex: "Tente focar nas manhãs", "Divida tarefas grandes").

        **Retorne APENAS o JSON.**
        """
        
        try:
            self.logger.info("[FocusAIEngine] Gerando Review Estatístico via IA...")
            resposta = self._chamar_ollama(prompt)
            
            if resposta and 'texto' in resposta and 'humor' in resposta:
                return resposta
            else:
                return {
                    "texto": "Meus sensores estão recalibrando, mas vejo que você continua na luta. Mantenha o foco!",
                    "humor": "bom",
                    "dica": "Revise seus focos e tente tarefas mais simples hoje."
                }
        except Exception as e:
            self.logger.exception("Erro ao gerar review estatístico:")
            return {
                "texto": "Erro de conexão com o núcleo de IA. Mas seus dados estão seguros!",
                "humor": "critico",
                "dica": "Verifique sua conexão e tente novamente."
            }