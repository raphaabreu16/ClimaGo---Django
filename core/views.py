from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import PesquisaClimaForm, CadastroForm

def home(request):
    return render(request, 'core/home.html')


def previsao(request):
    return render(request, 'core/previsao.html')


def calendario(request):
    return render(request, 'core/calendario.html')


def eventos(request):
    return render(request, 'core/eventos.html')

def pesquisar_clima(request):

    cidade = None

    if request.method == 'POST':
        form = PesquisaClimaForm(request.POST)

        if form.is_valid():
            cidade = form.cleaned_data['cidade']

    else:
        form = PesquisaClimaForm()

    return render(
        request,
        'pesquisa_clima.html',
        {
            'form': form,
            'cidade': cidade
        }
    )
def cadastro(request):

    erro = None

    if request.method == 'POST':

        form = CadastroForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if User.objects.filter(username=username).exists():

                erro = 'Usuário já existe'

            else:

                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                return redirect('login')

    else:

        form = CadastroForm()

    return render(
        request,
        'cadastro.html',
        {
            'form': form,
            'erro': erro
        }
    ) 