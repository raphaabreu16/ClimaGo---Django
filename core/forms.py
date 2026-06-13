from django import forms
from django.contrib.auth.models import User

class PesquisaClimaForm(forms.Form):

    cidade = forms.CharField(
        label='Cidade',
        max_length=100
    )
    
class CadastroForm(forms.Form):

    username = forms.CharField(
        label='Usuário',
        max_length=150
    )

    email = forms.EmailField()

    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput()
    )