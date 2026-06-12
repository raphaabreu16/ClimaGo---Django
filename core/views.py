from django.shortcuts import render


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
    