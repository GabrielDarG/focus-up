document.addEventListener('DOMContentLoaded', function () {
    console.log("meuperfil.js CARREGADO!");

    const perfisDataElement = document.getElementById('perfis-data');
    if (!perfisDataElement) return;
    const perfisDados = JSON.parse(perfisDataElement.textContent);

    const seletorPerfil = document.getElementById('seletor-perfil');
    const containerDinamico = document.getElementById('container-dinamico-perfil');
    const areaExibicao = document.getElementById('exibicao-perfil');
    const secaoFormulario = document.getElementById('secao-formulario');
    const form = document.getElementById('perfil-foco-form');
    const formFocoSelect = form ? form.querySelector('#id_foco_nome_select') : null;
    const formDetalhes = document.getElementById('id_detalhes_textarea');
    const botaoCancelar = document.getElementById('botao-cancelar-js');

    const camposAcademia = document.getElementById('campos-academia');
    const camposEstudos = document.getElementById('campos-estudos');
    const camposTrabalho = document.getElementById('campos-trabalho');
    const camposSaude = document.getElementById('campos-saude');
    const camposCasa = document.getElementById('campos-casa');
    const camposLazer = document.getElementById('campos-lazer');
    const todasAsDivsCampos = [ camposAcademia, camposEstudos, camposTrabalho, camposSaude, camposCasa, camposLazer ];

    // Academia
    const formAltura = document.getElementById('id_extra_altura');
    const formPeso = document.getElementById('id_extra_peso');
    const formNivelTreino = document.getElementById('id_extra_nivel_treino');
    const formLocalTreino = document.getElementById('id_extra_local_treino');
    const formFreqTreino = document.getElementById('id_extra_freq_treino');
    const formObjetivoAcademia = document.getElementById('id_extra_objetivo_academia');
    // Estudos
    const formTipoEstudante = document.getElementById('id_extra_tipo_estudante');
    const formAreaEstudo = document.getElementById('id_extra_area_estudo');
    const formPeriodoEstudo = document.getElementById('id_extra_periodo_preferido_estudo');
    // Trabalho
    const formAreaTrabalho = document.getElementById('id_extra_area_trabalho');
    const formModalidadeTrabalho = document.getElementById('id_extra_modalidade_trabalho');
    const formCargoAtual = document.getElementById('id_extra_cargo_atual');
    // Saúde
    const formObjetivoSaude = document.getElementById('id_extra_objetivo_saude');
    const formAcompanhamento = document.getElementById('id_extra_acompanhamento_medico');
    const formRestricao = document.getElementById('id_extra_restricao_alimentar');
    // Casa
    const formTipoMoradia = document.getElementById('id_extra_tipo_moradia');
    const formTarefaCasa = document.getElementById('id_extra_tarefa_principal_casa');
    const formMoraSozinho = document.getElementById('id_extra_mora_sozinho');
    // Lazer
    const formHobby = document.getElementById('id_extra_hobby_principal');
    const formFreqLazer = document.getElementById('id_extra_freq_lazer');
    const formTipoLazer = document.getElementById('id_extra_tipo_lazer_preferido');

    const mapFocoParaDivId = {
        'academia': 'campos-academia',
        'estudos': 'campos-estudos',
        'trabalho': 'campos-trabalho',
        'saude': 'campos-saude',
        'casa': 'campos-casa',
        'lazer': 'campos-lazer',
    };

    let inicializacaoOk = true;
    if (!seletorPerfil || !containerDinamico || !areaExibicao || !secaoFormulario || !form || !formFocoSelect || !formDetalhes || !botaoCancelar) {
        inicializacaoOk = false;
    }
    
    if (!inicializacaoOk) return;

    let perfilSelecionadoAtual = null;

    const placeholdersExemplo = {
        'academia': 'Ex: Quero focar em hipertrofia, treino 5x/semana na academia do prédio...',
        'estudos': 'Ex: Preciso estudar para a prova de cálculo, 2h por dia, prefiro à noite...',
        'trabalho': 'Ex: Projeto importante para entregar até sexta, organizar tarefas diárias...',
        'saude': 'Ex: Beber 2L de água por dia, lembrar vitaminas, caminhadas 3x/semana...',
        'casa': 'Ex: Limpeza semanal (seg/qua/sex), compras no sábado, consertar torneira...',
        'lazer': 'Ex: Ler 1 capítulo por dia, filme no fds, sair com amigos sexta...',
        'outro': 'Descreva seu objetivo específico, dificuldades, preferências...',
        '': 'Descreva seus objetivos, dificuldades, preferências...'
    };

    function toggleCamposEspeciaisFormulario(nomePerfil) {
        const focoKey = nomePerfil ? nomePerfil.toLowerCase() : '';
        const idDivParaMostrar = mapFocoParaDivId[focoKey];
        
        todasAsDivsCampos.forEach(div => {
            if (div) {
                if (div.id === idDivParaMostrar) {
                    div.style.display = 'block';
                } else {
                    div.style.display = 'none';
                }
            }
        });
    }

    function atualizarPlaceholderDetalhes(nomePerfil) {
        const placeholderKey = nomePerfil ? nomePerfil.toLowerCase() : '';
        const textoPlaceholder = placeholdersExemplo[placeholderKey] || placeholdersExemplo[''];
        if (formDetalhes) {
            formDetalhes.placeholder = textoPlaceholder;
        }
    }

    function atualizarExibicao(nomePerfil) {
        perfilSelecionadoAtual = nomePerfil;
        const perfil = perfisDados[nomePerfil];
        if (form) form.classList.remove('editando');

        if (!nomePerfil) {
            areaExibicao.innerHTML = `<p class="perfil-vazio-js">Selecione um perfil acima.</p>`;
            mostrarArea('exibicao');
            return;
        }

        let htmlInterno = '';
        let botaoPersonalizarHtml = `<button data-nome-perfil="${nomePerfil}" class="botao-personalizar">Personalizar Perfil</button>`;

        let nomeExibicao = nomePerfil;
        const optionSelecionada = Array.from(seletorPerfil.options).find(opt => opt.value === nomePerfil);
        if (optionSelecionada) { nomeExibicao = optionSelecionada.text; }

        if (perfil) {
            let detalhesHtml = '';
            if (perfil.dados_especificos && Object.keys(perfil.dados_especificos).length > 0) {
                const MapeamentoNomes = {
                    'altura': 'Altura', 'peso': 'Peso', 'nivel_treino': 'Nível', 'local_treino': 'Local', 'freq_treino': 'Frequência', 'objetivo_academia': 'Objetivo Fitness',
                    'tipo_estudante': 'Tipo de Estudante', 'area_estudo': 'Área de Estudo', 'periodo_preferido_estudo': 'Período Preferido',
                    'area_trabalho': 'Área', 'modalidade_trabalho': 'Modalidade', 'cargo_atual': 'Cargo',
                    'objetivo_saude': 'Objetivo de Saúde', 'acompanhamento_medico': 'Acompanhamento Médico', 'restricao_alimentar': 'Restrições',
                    'tipo_moradia': 'Moradia', 'tarefa_principal_casa': 'Tarefa Principal', 'mora_sozinho': 'Mora Sozinho(a)',
                    'hobby_principal': 'Hobby', 'freq_lazer': 'Frequência de Lazer', 'tipo_lazer_preferido': 'Tipo de Lazer'
                };
                
                detalhesHtml = `<h4>Detalhes Específicos</h4>${
                    Object.entries(perfil.dados_especificos)
                          .map(([chave, valor]) => `<p><strong>${MapeamentoNomes[chave] || chave}:</strong> ${valor}</p>`)
                          .join('')
                }`;
            }
            htmlInterno = `<h4>${nomeExibicao}</h4><p><strong>Observações:</strong> ${perfil.detalhes || '(Sem observações)'}</p>${detalhesHtml}${botaoPersonalizarHtml.replace('Personalizar', 'Editar')}`;
        } else {
            htmlInterno = `<h4>${nomeExibicao}</h4><p class="perfil-vazio-js" style="text-align: left; padding: 0;">Você ainda não definiu detalhes para este perfil de foco.</p>${botaoPersonalizarHtml}`;
        }
        areaExibicao.innerHTML = htmlInterno;
        mostrarArea('exibicao');
    }

    function preencherFormulario(nomePerfil) {
        const perfil = perfisDados[nomePerfil];
        
        if (!formFocoSelect) return;

        const nomePerfilValue = nomePerfil.toLowerCase();
        formFocoSelect.value = nomePerfilValue;

        formDetalhes.value = '';
        [ formAltura, formPeso, formNivelTreino, formLocalTreino, formFreqTreino, formObjetivoAcademia,
          formTipoEstudante, formAreaEstudo, formPeriodoEstudo,
          formAreaTrabalho, formModalidadeTrabalho, formCargoAtual,
          formObjetivoSaude, formAcompanhamento, formRestricao,
          formTipoMoradia, formTarefaCasa, formMoraSozinho,
          formHobby, formFreqLazer, formTipoLazer
        ].forEach(campo => { if (campo) campo.value = ''; });

        if (perfil) {
            formDetalhes.value = perfil.detalhes || '';
            if (perfil.dados_especificos) {
                const dados = perfil.dados_especificos;
                
                try { if (formAltura) formAltura.value = dados['altura'] ?? ''; } catch(e) {}
                try { if (formPeso) formPeso.value = dados['peso'] ?? ''; } catch(e) {}
                try { if (formNivelTreino) formNivelTreino.value = dados['nivel_treino'] ?? ''; } catch(e) {}
                try { if (formLocalTreino) formLocalTreino.value = dados['local_treino'] ?? ''; } catch(e) {}
                try { if (formFreqTreino) formFreqTreino.value = dados['freq_treino'] ?? ''; } catch(e) {}
                try { if (formObjetivoAcademia) formObjetivoAcademia.value = dados['objetivo_academia'] ?? ''; } catch(e) {}
                
                try { if (formTipoEstudante) formTipoEstudante.value = dados['tipo_estudante'] ?? ''; } catch(e) {}
                try { if (formAreaEstudo) formAreaEstudo.value = dados['area_estudo'] ?? ''; } catch(e) {}
                try { if (formPeriodoEstudo) formPeriodoEstudo.value = dados['periodo_preferido_estudo'] ?? ''; } catch(e) {}
                
                try { if (formAreaTrabalho) formAreaTrabalho.value = dados['area_trabalho'] ?? ''; } catch(e) {}
                try { if (formModalidadeTrabalho) formModalidadeTrabalho.value = dados['modalidade_trabalho'] ?? ''; } catch(e) {}
                try { if (formCargoAtual) formCargoAtual.value = dados['cargo_atual'] ?? ''; } catch(e) {}
                
                try { if (formObjetivoSaude) formObjetivoSaude.value = dados['objetivo_saude'] ?? ''; } catch(e) {}
                try { if (formAcompanhamento) formAcompanhamento.value = dados['acompanhamento_medico'] ?? ''; } catch(e) {}
                try { if (formRestricao) formRestricao.value = dados['restricao_alimentar'] ?? ''; } catch(e) {}
                
                try { if (formTipoMoradia) formTipoMoradia.value = dados['tipo_moradia'] ?? ''; } catch(e) {}
                try { if (formTarefaCasa) formTarefaCasa.value = dados['tarefa_principal_casa'] ?? ''; } catch(e) {}
                try { if (formMoraSozinho) formMoraSozinho.value = dados['mora_sozinho'] ?? ''; } catch(e) {}
                
                try { if (formHobby) formHobby.value = dados['hobby_principal'] ?? ''; } catch(e) {}
                try { if (formFreqLazer) formFreqLazer.value = dados['freq_lazer'] ?? ''; } catch(e) {}
                try { if (formTipoLazer) formTipoLazer.value = dados['tipo_lazer_preferido'] ?? ''; } catch(e) {}
            }
        }

        atualizarPlaceholderDetalhes(nomePerfil);
        toggleCamposEspeciaisFormulario(nomePerfil);
    }

    function mostrarArea(area) {
        if (!areaExibicao || !secaoFormulario) return;
        if (area === 'formulario') {
            areaExibicao.style.display = 'none';
            secaoFormulario.style.display = 'block';
            if (form) form.classList.add('editando');
        } else {
            areaExibicao.style.display = 'block';
            secaoFormulario.style.display = 'none';
            if (form) form.classList.remove('editando');
        }
    }

    if (seletorPerfil) {
        seletorPerfil.addEventListener('change', function () {
            atualizarExibicao(this.value);
            mostrarArea('exibicao');
        });
    }

    if (containerDinamico) {
        containerDinamico.addEventListener('click', function(event) {
            if (areaExibicao.contains(event.target) && event.target.classList.contains('botao-personalizar')) {
                const nomePerfil = event.target.getAttribute('data-nome-perfil');
                if (nomePerfil) {
                    preencherFormulario(nomePerfil);
                    mostrarArea('formulario');
                }
            }
        });
    }

    if (botaoCancelar) {
        botaoCancelar.addEventListener('click', function() {
            atualizarExibicao(perfilSelecionadoAtual);
        });
    }

    if (formFocoSelect) {
        formFocoSelect.addEventListener('change', function() {
            atualizarPlaceholderDetalhes(this.value);
            toggleCamposEspeciaisFormulario(this.value);
        });
    }

    mostrarArea('exibicao');
    if (formFocoSelect) {
        atualizarPlaceholderDetalhes(formFocoSelect.value);
        toggleCamposEspeciaisFormulario(formFocoSelect.value);
    }
});