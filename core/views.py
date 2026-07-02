from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import (authenticate, login, logout)
from django.contrib.auth.decorators import login_required
from .forms import (PesquisaClimaForm, CadastroForm, LoginForm)
from .services.weather_api import get_weather
from .models import EventoCalendario


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

    eventos = EventoCalendario.objects.order_by("data_inicio")

    context = {
        "weather": weather,
        "city_search": city,
        "eventos": eventos,
    }

    return render(request, "core/home.html", context)


def previsao(request):
    city = request.GET.get("city", "Rio de Janeiro")
    periodo = int(request.GET.get("periodo", 7))
    dia_selecionado = int(request.GET.get("dia", 0))
    inicio_intervalo = request.GET.get("inicio")
    fim_intervalo = request.GET.get("fim")

    if periodo not in [7, 15, 30]:
        periodo = 7

    try:
        weather = get_weather(city)
    except Exception:
        weather = None

    forecast_exibido = []
    dia_detalhe = None
    analise_intervalo = None

    if weather and weather.get("forecast"):
        forecast_completo = weather["forecast"]
        forecast_exibido = forecast_completo[:periodo]

        if dia_selecionado < len(forecast_exibido):
            dia_detalhe = forecast_exibido[dia_selecionado]

        if inicio_intervalo is not None and fim_intervalo is not None:
            try:
                ini = int(inicio_intervalo)
                fim = int(fim_intervalo)
                if ini > fim:
                    ini, fim = fim, ini
                intervalo = forecast_exibido[ini:fim + 1]
                if intervalo:
                    temps = [d["max_temp"] for d in intervalo if isinstance(d["max_temp"], (int, float))]
                    chuvas = [d["rain_chance"] for d in intervalo if isinstance(d["rain_chance"], (int, float))]
                    scores = [d["risk_score"] for d in intervalo if isinstance(d["risk_score"], (int, float))]
                    analise_intervalo = {
                        "inicio_label": intervalo[0]["day_label"],
                        "fim_label": intervalo[-1]["day_label"],
                        "temp_media": round(sum(temps) / len(temps)) if temps else "--",
                        "chuva_media": round(sum(chuvas) / len(chuvas)) if chuvas else "--",
                        "score_medio": round(sum(scores) / len(scores)) if scores else "--",
                        "vento_medio": weather.get("wind_speed", "--"),
                    }
                    score = analise_intervalo["score_medio"]
                    if isinstance(score, int) and score >= 80:
                        analise_intervalo["texto"] = "Período excelente para atividades ao ar livre."
                    elif isinstance(score, int) and score >= 60:
                        analise_intervalo["texto"] = "Condições favoráveis, mas fique de olho na chuva."
                    elif isinstance(score, int):
                        analise_intervalo["texto"] = "Período com risco climático elevado. Planeje com cuidado."
                    else:
                        analise_intervalo["texto"] = "Selecione um intervalo para ver a análise."
            except (ValueError, IndexError):
                analise_intervalo = None

    return render(request, 'core/previsao.html', {
        'weather': weather,
        'city': city,
        'periodo': periodo,
        'forecast_exibido': forecast_exibido,
        'dia_selecionado': dia_selecionado,
        'dia_detalhe': dia_detalhe,
        'analise_intervalo': analise_intervalo,
        'inicio_intervalo': inicio_intervalo,
        'fim_intervalo': fim_intervalo,
    })


@login_required
def calendario(request):
    eventos = EventoCalendario.objects.order_by("data_inicio")
    return render(request, "core/calendario.html", {"eventos": eventos})


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
    return render(request, 'pesquisa_clima.html', {'form': form, 'cidade': cidade})


def cadastro(request):
    erro = None
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            if User.objects.filter(username=username).exists():
                erro = 'Usuário já existe'
            else:
                User.objects.create_user(username=username, email=email, password=password)
                return redirect('login')
    else:
        form = CadastroForm()
    return render(request, 'core/cadastro.html', {'form': form, 'erro': erro})


def login_view(request):
    erro = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            usuario = authenticate(request, username=username, password=password)
            if usuario:
                login(request, usuario)
                return redirect('home')
            erro = 'Usuário ou senha inválidos'
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form, 'erro': erro})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def alertas(request):
    return render(request, 'core/alertas.html')


@login_required
def config(request):
    return render(request, 'core/config.html')