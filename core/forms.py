from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import EventoCalendario


class PesquisaClimaForm(forms.Form):
    cidade = forms.CharField(label='Cidade', max_length=100)


class CadastroForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginForm(forms.Form):
    username = forms.CharField(label='Usuário', max_length=150)
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)


class EventoForm(forms.Form):
    titulo = forms.CharField(
        label='Nome do evento',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Ex: Trilha na serra'})
    )
    data_inicio = forms.DateTimeField(
        label='Data e hora de início',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )
    data_fim = forms.DateTimeField(
        label='Data e hora de fim',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )
    local_evento = forms.CharField(
        label='Localização',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Buscar cidade ou endereço...'})
    )
    tipo_evento = forms.ChoiceField(
        label='Tipo',
        choices=EventoCalendario.TIPO_EVENTO_CHOICES
    )
    descricao = forms.CharField(
        label='Descrição',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Detalhes do evento...'})
    )