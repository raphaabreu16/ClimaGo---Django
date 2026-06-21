from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class PesquisaClimaForm(forms.Form):

    cidade = forms.CharField(

        label='Cidade',

        max_length=100

    )


class CadastroForm(UserCreationForm):

    email = forms.EmailField()

    class Meta:

        model = User

        fields = (

            'username',

            'email',

            'password1',

            'password2'

        )


class LoginForm(forms.Form):

    username = forms.CharField(

        label='Usuário',

        max_length=150

    )

    password = forms.CharField(

        label='Senha',

        widget=forms.PasswordInput

    ) 