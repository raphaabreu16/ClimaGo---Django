from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import (authenticate,login,logout)
from .forms import PesquisaClimaForm, CadastroForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .services.weather_api import get_weather


def home(request):
    city = request.GET.get("city", "Rio de Janeiro")

    try:
        weather = get_weather(city)
    except Exception:
        weather = {
            "city": city,
            "temperature": "--",
            "humidity": "--",
            "wind_speed": "--",
            "weather_code": None,
            "forecast": [],
        }

    context = {
        "weather": weather,
        "city_search": city,
    }

    return render(request, "core/home.html", context)


def previsao(request):
    return render(request, 'core/previsao.html')

@login_required
def calendario(request):
    return render(request, 'core/calendario.html')

@login_required
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
def login_view(request):

    erro = None

    if request.method == 'POST':

        form = LoginForm(
            request.POST
        )

        if form.is_valid():

            username = (
                form.cleaned_data[
                    'username'
                ]
            )

            password = (
                form.cleaned_data[
                    'password'
                ]
            )

            usuario = authenticate(
                request,
                username=username,
                password=password
            )

            if usuario:

                login(
                    request,
                    usuario
                )

                return redirect(
                    'home'
                )

            erro = (
                'Usuário ou senha inválidos'
            )

    else:

        form = LoginForm()

    return render(
        request,
        'login.html',
        {
            'form': form,
            'erro': erro
        }
    )
def logout_view(request):

    logout(request)

    return redirect(
        'home'
    )
LOGIN_URL='login'

LOGIN_REDIRECT_URL='home'

def alertas(request):
    return render(request, 'core/alertas.html')

def config(request):
    return render(request, 'core/config.html')

