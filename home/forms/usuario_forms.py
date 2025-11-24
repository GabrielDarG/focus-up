from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from ..models.usuario import Usuario

class UsuarioCadastroForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('email', 'nome', 'nome_usuario', 'sexo', 'data_nascimento')

        widgets = {
            'email': forms.EmailInput(
                attrs={'placeholder': 'exemplo@email.com'}
            ),
            'nome': forms.TextInput(
                attrs={'placeholder': 'Digite seu nome completo'}
            ),
            'nome_usuario': forms.TextInput(
                attrs={'placeholder': 'Nome no FocusUP'}
            ),
            'data_nascimento': forms.DateInput(
                attrs={'type': 'date'} 
            ),
            'sexo': forms.Select(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_choices = list(self.fields['sexo'].choices)
        if current_choices and current_choices[0][0] != '':
             self.fields['sexo'].choices = [('', '---------')] + current_choices
        elif not current_choices:
             self.fields['sexo'].choices = [('', '---------')]


    def clean_nome_usuario(self):
        nome_usuario = self.cleaned_data.get("nome_usuario")
        if Usuario.objects.filter(nome_usuario__iexact=nome_usuario).exists():
            raise ValidationError("Esse nome de usuário já está em uso.")
        return nome_usuario

# -------------------------------------------------------------------
# ------------------ FORMULÁRIO DE EDIÇÃO DE PERFIL  -------------------
# -------------------------------------------------------------------

class UsuarioEditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['avatar', 'nome', 'nome_usuario', 'sexo', 'data_nascimento']
        
        widgets = {
            'nome': forms.TextInput(
                attrs={'placeholder': 'Digite seu nome completo'}
            ),
            'nome_usuario': forms.TextInput(
                attrs={'placeholder': 'Nome no FocusUP'}
            ),
            'data_nascimento': forms.DateInput(
                attrs={'type': 'date'} 
            ),
            'sexo': forms.Select(),

           
            'avatar': forms.FileInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        current_choices = list(self.fields['sexo'].choices)
        if current_choices and current_choices[0][0] != '':
                self.fields['sexo'].choices = [('', '---------')] + current_choices
        elif not current_choices:
                self.fields['sexo'].choices = [('', '---------')]
       

    def clean_nome_usuario(self):
        """ Validação para nome de usuário duplicado. """
        nome_usuario = self.cleaned_data.get('nome_usuario')
        if nome_usuario != self.instance.nome_usuario:       
            if Usuario.objects.filter(nome_usuario__iexact=nome_usuario).exists():
                raise ValidationError("Esse nome de usuário já está em uso por outra conta.")
        return nome_usuario
