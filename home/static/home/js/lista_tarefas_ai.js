document.addEventListener('DOMContentLoaded', function() {
    console.log("lista_tarefas_ai.js Carregado! (v103 - Moedas Universal Class)");

    const container = document.querySelector('.container-tarefas');
    const listaTarefasUL = document.getElementById('lista-tarefas-ul');
    let itemListaVazia = document.getElementById('lista-tarefas-vazia');

    const ajaxUrlGerarManual = container.dataset.ajaxUrlGerar;
    const ajaxUrlSalvarManual = container.dataset.ajaxUrlSalvar;
    const ajaxUrlStatusIA = container.dataset.ajaxUrlStatusGeracaoIa;
    const csrftoken = container.dataset.csrfToken;

    const slotsIaUsados = parseInt(container.dataset.slotsIaUsados, 10);
    const slotsIaLimite = parseInt(container.dataset.slotsIaLimite, 10);
    
    const iaLoadingContainer = document.getElementById('ia-loading-container');
    const iaLoadingSpinner = document.getElementById('ia-loading-spinner'); 
    const iaLoadingFeedback = document.getElementById('ia-loading-feedback');
    let pollingInterval = null; 

    const seletorFocoManual = document.getElementById('seletor-foco-ia-lista');
    const botaoGerarManual = document.getElementById('botao-gerar-ia-lista');
    const areaSugestaoManual = document.getElementById('area-sugestao-lista');
    const feedbackManual = document.getElementById('feedback-ia-lista');
    const botaoAceitarManual = document.getElementById('botao-aceitar-lista');
    const botaoDispensarManual = document.getElementById('botao-dispensar-lista');
    let sugestaoManualAtual = null; 
    
    if (iaLoadingContainer && slotsIaUsados < slotsIaLimite) {
        console.log("Slots de IA não estão cheios. Iniciando Polling...");
        iniciarPollingGeracaoIA();
    } else if (iaLoadingContainer) {
        iaLoadingContainer.style.display = 'none';
    }

    function atualizarMoedasVisualmente(novoValor) {
        const elementosMoedas = document.querySelectorAll('.qtd-moedas-display');

        if (elementosMoedas.length > 0) {
            elementosMoedas.forEach(el => {
                el.style.color = '#00ff00'; 
                el.style.transition = 'color 0.3s ease';
                
                el.innerText = novoValor;
                
                setTimeout(() => {
                    el.style.color = ''; 
                }, 1000);
            });
            console.log(`Atualizado ${elementosMoedas.length} locais com moedas:`, novoValor);
        } else {
            console.warn("Nenhum elemento com a classe 'qtd-moedas-display' encontrado.");
        }
    }

    function iniciarPollingGeracaoIA() {
        verificarStatusGeracaoIA();
        pollingInterval = setInterval(verificarStatusGeracaoIA, 5000); 
    }

    async function verificarStatusGeracaoIA() {
        try {
            const response = await fetch(ajaxUrlStatusIA, {
                method: 'GET',
                headers: { 'X-CSRFToken': csrftoken, 'X-Requested-With': 'XMLHttpRequest' }
            });
            
            if (!response.ok) {
                throw new Error(`Erro ${response.status} ao verificar status.`);
            }

            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || "Resposta de status inválida");
            }

            iaLoadingFeedback.textContent = `[${data.tarefas_criadas}/${data.tarefas_limite}] Missões geradas...`;

            if (data.status === 'completo') {
                console.log("Geração de IA concluída! Recarregando a página...");
                iaLoadingFeedback.textContent = "Sucesso! Carregando missões...";
                iaLoadingContainer.classList.add('completo');
                
                clearInterval(pollingInterval); 
                
                setTimeout(() => {
                    location.reload();
                }, 1000);
            }

        } catch (error) {
            console.error(`Erro no Polling: ${error.message}`);
            iaLoadingFeedback.textContent = "Erro ao verificar geração. Tentando novamente...";
            iaLoadingContainer.classList.add('erro');
        }
    }

    if (seletorFocoManual) {
        seletorFocoManual.addEventListener('change', function() {
            botaoGerarManual.disabled = !this.value;
            mostrarAreaSugestaoManual(false); 
            feedbackManual.textContent = ''; 
            feedbackManual.className = 'feedback-ia-lista'; 
            sugestaoManualAtual = null;
        });
    }

    function mostrarAreaSugestaoManual(mostrar = true) {
        if (!areaSugestaoManual || !botaoAceitarManual || !botaoDispensarManual) return;
        areaSugestaoManual.style.display = mostrar ? 'block' : 'none';
        const mostrarBotaoAceitar = mostrar && sugestaoManualAtual;
        botaoAceitarManual.style.display = mostrarBotaoAceitar ? 'inline-block' : 'none';
        botaoDispensarManual.style.display = mostrar ? 'inline-block' : 'none';
    }

    if (botaoGerarManual) {
        botaoGerarManual.addEventListener('click', async function() {
            const focoSelecionado = seletorFocoManual.value; 
            if (!focoSelecionado) return;
            
            botaoGerarManual.disabled = true; 
            botaoGerarManual.textContent = 'Gerando...';
            areaSugestaoManual.innerHTML = '<p>Consultando a IA...</p>'; 
            areaSugestaoManual.classList.add('loading');
            feedbackManual.textContent = ''; 
            feedbackManual.className = 'feedback-ia-lista'; 
            sugestaoManualAtual = null;
            mostrarAreaSugestaoManual(true);
            
            try {
                const response = await fetch(ajaxUrlGerarManual, { 
                    method: 'POST', 
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken, 'X-Requested-With': 'XMLHttpRequest' }, 
                    body: JSON.stringify({ foco_nome: focoSelecionado, action: 'gerar_sugestao' }) 
                });
                if (!response.ok) {
                    const err = await response.json();
                    throw new Error(err.error || "IA falhou em gerar sugestão");
                }
                const data = await response.json();
                
                sugestaoManualAtual = data; 
                areaSugestaoManual.classList.remove('loading');
                areaSugestaoManual.innerHTML = `
                    <p><strong>${data.titulo}</strong> <span class="xp-sugestao">(${data.xp} XP)</span></p>
                    <p class="task-description-full">${data.descricao}</p>
                `;
                
                feedbackManual.textContent = 'Sugestão pronta!'; 
                feedbackManual.classList.add('sucesso');
                mostrarAreaSugestaoManual(true);
            } catch (error) {
                console.error("Erro Gerar Manual:", error); 
                areaSugestaoManual.innerHTML = '<p style="color:var(--cor-erro);">Falha.</p>'; 
                feedbackManual.textContent = `Erro: ${error.message}. Tente.`; 
                feedbackManual.classList.add('erro');
                sugestaoManualAtual = null; 
                mostrarAreaSugestaoManual(true);
            } finally {
                botaoGerarManual.disabled = !seletorFocoManual.value; 
                botaoGerarManual.textContent = 'Sugerir Tarefa';
            }
        });
    }

    if (botaoAceitarManual) {
        botaoAceitarManual.addEventListener('click', async function() {
            if (!sugestaoManualAtual) return;
            
            botaoAceitarManual.disabled = true; 
            botaoAceitarManual.textContent = 'Adicionando...';
            botaoDispensarManual.disabled = true;
            feedbackManual.textContent = 'Salvando...'; 
            feedbackManual.className = 'feedback-ia-lista';
            
            const sugestaoParaSalvar = { ...sugestaoManualAtual };

            try {
                const response = await fetch(ajaxUrlSalvarManual, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken, 'X-Requested-With': 'XMLHttpRequest' },
                    body: JSON.stringify({
                        titulo: sugestaoParaSalvar.titulo,
                        descricao: sugestaoParaSalvar.descricao,
                        xp: sugestaoParaSalvar.xp,
                        foco_nome: sugestaoParaSalvar.foco_nome,
                        action: 'salvar_sugestao',
                        is_auto_generated: false 
                    })
                });
                if (!response.ok) {
                    const err = await response.json();
                    throw new Error(err.error || "Falha ao salvar sugestão");
                }
                const data = await response.json();

                feedbackManual.textContent = `Tarefa adicionada! (+${data.xp_adicionado} XP) Atualizando...`;
                feedbackManual.classList.add('sucesso');
                sugestaoManualAtual = null; 
                
                setTimeout(() => {
                    location.reload(); 
                }, 750); 

            } catch (error) {
                console.error("Erro Salvar Manual:", error); 
                feedbackManual.textContent = `Erro: ${error.message}`; 
                feedbackManual.classList.add('erro');
                sugestaoManualAtual = sugestaoParaSalvar; 
                
                botaoAceitarManual.disabled = false; 
                botaoAceitarManual.textContent = 'Adicionar esta Tarefa';
                botaoDispensarManual.disabled = false;
                
                mostrarAreaSugestaoManual(true);
            }
        });
    }

    if (botaoDispensarManual) {
        botaoDispensarManual.addEventListener('click', function() {
            sugestaoManualAtual = null; 
            mostrarAreaSugestaoManual(false); 
            areaSugestaoManual.innerHTML = ''; 
            feedbackManual.textContent = ''; 
            feedbackManual.className = 'feedback-ia-lista';
            if (botaoGerarManual) botaoGerarManual.disabled = !seletorFocoManual.value;
        });
    }

    async function handleAcaoTarefaClick(event) {
        const botaoClicado = event.target.closest('button.botao-tarefa');
        if (!botaoClicado) { return; }
        event.preventDefault(); 
        const form = botaoClicado.closest('form');
        const url = form.action; 
        const tarefaLi = form.closest('li.item-tarefa');
        const tarefaId = tarefaLi ? tarefaLi.id.split('-')[1] : null;
        if (!url || !tarefaLi || !tarefaId) { 
            console.error("Erro na Ação: URL/ID da tarefa não encontrado."); 
            return; 
        }
        console.log(`Ação AJAX para Tarefa ID: ${tarefaId} (URL: ${url})`);
        botaoClicado.disabled = true; 
        botaoClicado.textContent = '...';
        tarefaLi.querySelectorAll('.botao-tarefa').forEach(b => b.disabled = true);
        try {
            const response = await fetch(url, { 
                method: 'POST', 
                headers: { 
                    'X-CSRFToken': csrftoken, 
                    'X-Requested-With': 'XMLHttpRequest' 
                } 
            });
            if (!response.ok) { 
                let msg = `E${response.status}`; 
                try{ const err=await response.json(); msg=err.error||msg; } catch(e){} 
                throw new Error(msg); 
            }
            const data = await response.json();
            if (data.success) {
                if (data.concluida || data.descartada) {
                    removerItemDaLista(tarefaLi, `Tarefa ${tarefaId} concluída/descartada.`);
                    
                    if (data.concluida && typeof atualizarBarraDeXP === 'function') {
                        atualizarBarraDeXP(data); 
                    }

                    if (data.concluida && data.moedas_total !== undefined) {
                        atualizarMoedasVisualmente(data.moedas_total);
                    }
                }
                else if (!data.concluida) { 
                    console.log(`Tarefa ${tarefaId} desmarcada.`);
                    location.reload(); 
                }
            } else { 
                throw new Error(data.error || "Erro retornado."); 
            }
        } catch (error) {
            console.error("Erro AJAX na Ação:", error);
            tarefaLi.querySelectorAll('.botao-tarefa').forEach(b => b.disabled = false);
            if (botaoClicado.classList.contains('botao-concluir')) botaoClicado.textContent = 'Concluir';
            if (botaoClicado.classList.contains('botao-concluir-atrasada')) botaoClicado.textContent = 'Concluir (sem XP)';
            if (botaoClicado.classList.contains('botao-descartar')) botaoClicado.textContent = 'Descartar';
            alert(`Erro: ${error.message}`);
        }
    }
    
    if (listaTarefasUL) {
        listaTarefasUL.addEventListener('click', handleAcaoTarefaClick);
    }
    
    function removerItemDaLista(tarefaLi, mensagemLog) {
        console.log(mensagemLog);
        tarefaLi.style.opacity = '0';
        tarefaLi.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease';
        tarefaLi.style.transform = 'translateX(50px)';
        setTimeout(() => {
            tarefaLi.remove();
            if (listaTarefasUL.querySelectorAll('li.item-tarefa').length === 0) {
                listaTarefasUL.innerHTML = `
                    <li class="item-tarefa-vazia" id="lista-tarefas-vazia">
                        <p>Você não tem tarefas para hoje.</p>
                        <p>Crie tarefas recorrentes ou aguarde suas Quests Diárias!</p>
                    </li>
                `;
            }
        }, 500); 
    }
});