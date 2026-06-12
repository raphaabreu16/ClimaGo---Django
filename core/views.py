from django.shortcuts import render


def home(request):
    return render(request, 'core/home.html')


def previsao(request):
    return render(request, 'core/previsao.html')


def calendario(request):
    return render(request, 'core/calendario.html')


def eventos(request):
    return render(request, 'core/eventos.html')