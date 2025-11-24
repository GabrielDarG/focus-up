document.addEventListener('DOMContentLoaded', function() {
    console.log("adicionar_Tarefas.js Carregado! (v5 - Edição In-line)");

    const container = document.querySelector('.container-add-tarefa');
    const listaRecorrencia = document.getElementById('lista-recorrencia');
    
    const ajaxUrlSalvarRecorrencia = container ? container.dataset.ajaxUrlSalvarRecorrencia : null;
    const csrftoken = container ? container.dataset.csrfToken : null;
    const urlCriarTarefa = container ? container.dataset.urlCriar : null;

    const formTarefa = document.getElementById('form-tarefa');
    const formTitulo = document.getElementById('form-tarefa-titulo');
    const formSubmitBtn = document.getElementById('form-tarefa-submit-btn');
    const formCancelBtn = document.getElementById('form-tarefa-cancel-btn');
    
    const fieldTitulo = document.getElementById('id_titulo');
    const fieldFoco = document.getElementById('id_foco');
    const fieldDescricao = document.getElementById('id_descricao');

    
    // --- Lógica de Edição ---
    
    if (listaRecorrencia) {
        listaRecorrencia.addEventListener('click', function(event) {
            
            const botaoEditar = event.target.closest('[data-action="editar-tarefa"]');
            const botaoToggle = event.target.closest('[data-action="toggle-recorrencia"]');

            if (botaoEditar) {
                event.preventDefault(); 
                console.log("Botão Editar clicado.");
                const urlGet = botaoEditar.href; 
                iniciarEdicao(urlGet);
            }
            
            if (botaoToggle) {
                event.preventDefault();
                toggleDropdown(botaoToggle);
            }
        });
    }

    async function iniciarEdicao(url) {
        console.log(`Buscando dados em: ${url}`);
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            
            if (!response.ok) throw new Error(`Erro ${response.status} ao buscar dados.`);
            
            const data = await response.json();
            console.log("Dados recebidos:", data);

            fieldTitulo.value = data.titulo;
            fieldDescricao.value = data.descricao;
            fieldFoco.value = data.foco_id || ""; 

            modoEdicao(url); 

        } catch (error) {
            console.error("Erro ao buscar dados da tarefa:", error);
            alert("Não foi possível carregar os dados da tarefa. Tente recarregar a página.");
        }
    }

    function modoEdicao(urlPost) {
        formTarefa.action = urlPost;
        
        formTitulo.textContent = "Editando Tarefa";
        formSubmitBtn.textContent = "Salvar Alterações";
        
        formCancelBtn.style.display = "block";
        
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function modoCriacao() {
        formTarefa.reset(); 
        
        formTarefa.action = urlCriarTarefa;
        
        formTitulo.textContent = "Criar Nova Tarefa Pessoal";
        formSubmitBtn.textContent = "Criar Tarefa na Lista";
        
        formCancelBtn.style.display = "none";
    }

    if (formCancelBtn) {
        formCancelBtn.addEventListener('click', function(event) {
            event.preventDefault();
            modoCriacao();
        });
    }


    // --- Lógica de Recorrência ---

    if (!listaRecorrencia) {
        console.log("Lista de recorrência não encontrada (normal se não houver tarefas).");
    }
    if (!ajaxUrlSalvarRecorrencia || !csrftoken) {
        console.error("ERRO CRÍTICO: URL de salvar recorrência ou CSRF Token não encontrados no .container-add-tarefa");
    }

    function toggleDropdown(botaoToggle) {
        const dropdown = botaoToggle.closest('.dropdown-recorrencia');
        
        document.querySelectorAll('.dropdown-recorrencia.is-open').forEach(openDropdown => {
            if (openDropdown !== dropdown) {
                openDropdown.classList.remove('is-open');
            }
        });

        dropdown.classList.toggle('is-open');
    }

    document.addEventListener('click', function(event) {
        if (!event.target.closest('.dropdown-recorrencia')) {
            document.querySelectorAll('.dropdown-recorrencia.is-open').forEach(openDropdown => {
                openDropdown.classList.remove('is-open');
            });
        }
    });

    if (listaRecorrencia) {
        listaRecorrencia.addEventListener('change', function(event) {
            const checkbox = event.target.closest('.recorrencia-dropdown-menu input[type="checkbox"]');
            if (checkbox) {
                const dropdownMenu = checkbox.closest('.recorrencia-dropdown-menu');
                const botao = dropdownMenu.previousElementSibling;
                const itemLi = checkbox.closest('li.item-recorrencia');
                const tarefaId = itemLi.dataset.tarefaId;
                const dia = checkbox.name; 
                const status = checkbox.checked; 

                atualizarTextoBotao(botao, dropdownMenu);
                
                salvarRecorrencia(tarefaId, dia, status, botao);
            }
        });
    }

    function atualizarTextoBotao(botao, dropdownMenu) {
        const inputsMarcados = dropdownMenu.querySelectorAll('input:checked');
        let diasSelecionados = [];
        inputsMarcados.forEach(input => {
            diasSelecionados.push(input.dataset.dia); 
        });

        if (diasSelecionados.length === 0) {
            botao.textContent = 'Definir recorrência';
            botao.classList.add('botao-recorrencia-vazio'); 
        } else if (diasSelecionados.length === 7) {
            botao.textContent = 'Todos os dias';
            botao.classList.remove('botao-recorrencia-vazio');
        } else {
            botao.textContent = diasSelecionados.join(', ');
            botao.classList.remove('botao-recorrencia-vazio');
        }
    }

    async function salvarRecorrencia(tarefaId, dia, status, botao) {
        console.log(`Salvando... Tarefa ${tarefaId}, Dia: ${dia}, Status: ${status}`);
        
        botao.style.opacity = '0.5';
        botao.disabled = true; 

        try {
            const response = await fetch(ajaxUrlSalvarRecorrencia, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    tarefa_id: tarefaId,
                    dia: dia,
                    status: status
                })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || "Erro de rede");
            }

            const data = await response.json();
            
            if (data.success) {
                console.log("Recorrência salva com sucesso.");
                botao.textContent = data.novo_texto;
                
                if (data.novo_texto !== "Definir recorrência") {
                    botao.classList.remove('botao-recorrencia-vazio');
                } else {
                    botao.classList.add('botao-recorrencia-vazio');
                }

            } else {
                throw new Error(data.error || "O servidor recusou a mudança.");
            }

        } catch (error) {
            console.error("Erro ao salvar recorrência:", error);
            alert(`Erro ao salvar: ${error.message}. A página será recarregada.`);
            location.reload(); 
        } finally {
            botao.style.opacity = '1';
            botao.disabled = false;
        }
    }
});