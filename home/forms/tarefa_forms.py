# home/forms/Tarefa_forms.py
from django import forms
from django.db.models import Case, When, Value
from ..models import Tarefa
from ..models import UsuarioFoco 

class FocoModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.foco_nome.capitalize()

class TarefaForm(forms.ModelForm):
    
    foco = FocoModelChoiceField(
        queryset=UsuarioFoco.objects.none(), 
        required=False, 
        label="Área de Foco (Opcional)",
        widget=forms.Select(attrs={})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        
        if user:
            # --- MUDANÇA: Lógica de Ordenação Customizada ---
            
            # 1. Cria a "flag": 1 para 'Outro', 0 para os demais.
            # Usei __iexact para ignorar se está salvo como 'Outro' ou 'outro'.
            order_case = Case(
                When(foco_nome__iexact='Outro', then=Value(1)),
                default=Value(0)
            )
            
            # 2. Filtra pelo usuário
            queryset = UsuarioFoco.objects.filter(user=user)
            
            # 3. Ordena pela "flag" (0s primeiro) e DEPOIS alfabeticamente
            self.fields['foco'].queryset = queryset.order_by(order_case, 'foco_nome')
            
        else:
            self.fields['foco'].queryset = UsuarioFoco.objects.none()
            
        self.fields['foco'].empty_label = "Nenhuma área (tarefa geral)"
    

    class Meta:
        model = Tarefa
        fields = ['titulo', 'foco', 'descricao']
        
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Ex: Fazer almoço'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Adicione uma descrição (opcional)'}),
        }
        
        labels = {
            'titulo': 'Título da Tarefa',
        }