# Em home/forms/perfil_forms.py
from django import forms
from ..models.usuario_foco import UsuarioFoco 

# --- CHOICES ---
FOCO_CHOICES = [
    ('', '---------'), 
    ('academia', 'Academia'),
    ('estudos', 'Estudos'),
    ('trabalho', 'Trabalho'),
    ('saude', 'Saúde'),
    ('casa', 'Casa'),
    ('lazer', 'Lazer'),
    ('outro', 'Outro (Especifique nos Detalhes)'),
]

# Academia
NIVEL_TREINO_CHOICES = [('', '---------'), ('iniciante', 'Iniciante'), ('intermediario', 'Intermediário'), ('avancado', 'Avançado')]
LOCAL_TREINO_CHOICES = [('', '---------'), ('casa', 'Em Casa'), ('academia', 'Na Academia')]
FREQ_TREINO_CHOICES = [('', '---------'), ('1', '1x'), ('2', '2x'), ('3', '3x'), ('4', '4x'), ('5', '5x'), ('6', '6x'), ('7', '7x')]

# Estudos (NOVO)
TIPO_ESTUDANTE_CHOICES = [('', '---------'), ('medio', 'Ensino Médio'), ('graduacao', 'Graduação'), ('pos', 'Pós-graduação'), ('concurso', 'Concurso Público'), ('autodidata', 'Autodidata'), ('outro', 'Outro')]
PERIODO_ESTUDO_CHOICES = [('', '---------'), ('manha', 'Manhã'), ('tarde', 'Tarde'), ('noite', 'Noite'), ('indiferente', 'Indiferente')]

# Trabalho (NOVO)
MODALIDADE_TRABALHO_CHOICES = [('', '---------'), ('presencial', 'Presencial'), ('hibrido', 'Híbrido'), ('remoto', 'Remoto')]

# Saúde (NOVO)
ACOMPANHAMENTO_CHOICES = [('', '---------'), ('regular', 'Regularmente'), ('ocasional', 'Ocasionalmente'), ('nao', 'Não faço')]

# Casa (NOVO)
TIPO_MORADIA_CHOICES = [('', '---------'), ('apartamento', 'Apartamento'), ('casa', 'Casa'), ('outro', 'Outro')]
MORA_SOZINHO_CHOICES = [('', '---------'), ('sim', 'Sim'), ('nao', 'Não')]

# Lazer (NOVO)
FREQ_LAZER_CHOICES = [('', '---------'), ('diario', 'Diariamente'), ('semanal', 'Algumas vezes/semana'), ('fds', 'Finais de semana'), ('raro', 'Raramente')]
TIPO_LAZER_CHOICES = [('', '---------'), ('casa', 'Em casa'), ('arlivre', 'Ao ar livre'), ('social', 'Social'), ('cultural', 'Cultural'), ('indiferente', 'Indiferente')]


class UsuarioFocoForm(forms.ModelForm):
    
    foco_nome = forms.ChoiceField(
        choices=FOCO_CHOICES,
        label="Qual é o Foco?",
        widget=forms.Select(attrs={'id': 'id_foco_nome_select'}) 
    )

    
    # Academia
    altura = forms.DecimalField(label="Altura (metros)", required=False, max_digits=3, decimal_places=2, widget=forms.NumberInput(attrs={'step': '0.01', 'min': '1.00', 'max': '2.50', 'placeholder': 'Ex: 1.76'}))
    peso = forms.DecimalField(label="Peso Atual (kg)", required=False, max_digits=5, decimal_places=1, widget=forms.NumberInput(attrs={'step': '0.5', 'min': '30', 'max': '200'}))
    nivel_treino = forms.ChoiceField(choices=NIVEL_TREINO_CHOICES, label="Seu Nível", required=False)
    local_treino = forms.ChoiceField(choices=LOCAL_TREINO_CHOICES, label="Onde você treina?", required=False)
    freq_treino = forms.ChoiceField(choices=FREQ_TREINO_CHOICES, label="Frequência Semanal", required=False)
    objetivo_academia = forms.CharField(label="Principal Objetivo Fitness", required=False, widget=forms.TextInput(attrs={'placeholder': 'Ex: Ganhar massa, perder peso'}))
    
    # Estudos (NOVOS)
    tipo_estudante = forms.ChoiceField(choices=TIPO_ESTUDANTE_CHOICES, label="Tipo de Estudante", required=False)
    area_estudo = forms.CharField(label="Área de Estudo", required=False, widget=forms.TextInput(attrs={'placeholder': 'Ex: Engenharia, Direito, Programação'}))
    periodo_preferido_estudo = forms.ChoiceField(choices=PERIODO_ESTUDO_CHOICES, label="Período Preferido", required=False)
    
    # Trabalho (NOVOS)
    area_trabalho = forms.CharField(label="Sua Área", required=False, widget=forms.TextInput(attrs={'placeholder': 'Ex: TI, Marketing, Vendas'}))
    modalidade_trabalho = forms.ChoiceField(choices=MODALIDADE_TRABALHO_CHOICES, label="Modalidade", required=False)
    cargo_atual = forms.CharField(label="Cargo Atual", required=False, widget=forms.TextInput(attrs={'placeholder': 'Ex: Desenvolvedor Jr, Gerente'}))

    # Saúde (NOVOS)
    objetivo_saude = forms.CharField(label="Principal Objetivo de Saúde", required=False, widget=forms.TextInput(attrs={'placeholder': 'Ex: Beber mais água, Comer melhor'}))
    acompanhamento_medico = forms.ChoiceField(choices=ACOMPANHAMENTO_CHOICES, label="Acompanhamento Médico", required=False)
    restricao_alimentar = forms.CharField(label="Restrições Alimentares?", required=False, widget=forms.TextInput(attrs={'placeholder': 'Ex: Glúten, Lactose, Nenhuma'}))
    
    # Casa (NOVOS)
    tipo_moradia = forms.ChoiceField(choices=TIPO_MORADIA_CHOICES, label="Tipo de Moradia", required=False)
    tarefa_principal_casa = forms.CharField(label="Tarefa Doméstica Principal", required=False, widget=forms.TextInput(attrs={'placeholder': 'Ex: Limpeza geral, Organização'}))
    mora_sozinho = forms.ChoiceField(choices=MORA_SOZINHO_CHOICES, label="Mora Sozinho(a)?", required=False)
    
    # Lazer (NOVOS)
    hobby_principal = forms.CharField(label="Hobby Principal", required=False, widget=forms.TextInput(attrs={'placeholder': 'Ex: Leitura, Jogos, Esportes'}))
    freq_lazer = forms.ChoiceField(choices=FREQ_LAZER_CHOICES, label="Frequência", required=False)
    tipo_lazer_preferido = forms.ChoiceField(choices=TIPO_LAZER_CHOICES, label="Tipo Preferido", required=False)


    class Meta:
        model = UsuarioFoco 
        fields = ['foco_nome', 'detalhes'] 
        labels = { 'detalhes': 'Observações Adicionais (para a IA)' }
        widgets = {
            'detalhes': forms.Textarea(
                attrs={'rows': 4, 
                       'placeholder': 'Descreva seus objetivos, dificuldades, preferências...', 
                       'id': 'id_detalhes_textarea'} 
            ),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance') 
        initial_data = {}
        if instance and instance.dados_especificos:
            initial_data = instance.dados_especificos.copy()
        kwargs['initial'] = initial_data 
        super().__init__(*args, **kwargs)

        # Mapeamento de Focos para seus campos específicos
        self.campos_especificos_map = {
            'academia': ['altura', 'peso', 'nivel_treino', 'local_treino', 'freq_treino', 'objetivo_academia'],
            'estudos': ['tipo_estudante', 'area_estudo', 'periodo_preferido_estudo'],
            'trabalho': ['area_trabalho', 'modalidade_trabalho', 'cargo_atual'],
            'saude': ['objetivo_saude', 'acompanhamento_medico', 'restricao_alimentar'],
            'casa': ['tipo_moradia', 'tarefa_principal_casa', 'mora_sozinho'],
            'lazer': ['hobby_principal', 'freq_lazer', 'tipo_lazer_preferido'],
          
        }

        # Adiciona IDs aos widgets dos campos específicos
        for foco, campos in self.campos_especificos_map.items():
            for nome_campo in campos:
                if nome_campo in self.fields:
                    self.fields[nome_campo].widget.attrs['id'] = f'id_extra_{nome_campo}' 
                    

   
    def clean(self):
        cleaned_data = super().clean()
        foco_selecionado = cleaned_data.get('foco_nome')

        campos_a_limpar = {}
        for foco, campos in self.campos_especificos_map.items():
            if foco != foco_selecionado:
                for nome_campo in campos:
                    # Remove o valor se o foco não for o correspondente
                    if nome_campo in cleaned_data:
                         cleaned_data.pop(nome_campo, None) 
        
        return cleaned_data

    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        dados_especificos_atuais = {}
        foco_selecionado = self.cleaned_data.get('foco_nome')

        if foco_selecionado and foco_selecionado in self.campos_especificos_map:
            campos_deste_foco = self.campos_especificos_map[foco_selecionado]
            for nome_campo in campos_deste_foco:
                if nome_campo in self.cleaned_data and self.cleaned_data[nome_campo]:
                     # Armazena no dicionário com uma chave consistente (pode ser o próprio nome do campo)
                     dados_especificos_atuais[nome_campo] = self.cleaned_data[nome_campo]

        instance.dados_especificos = dados_especificos_atuais
        
        if commit:
            instance.save()
        return instance