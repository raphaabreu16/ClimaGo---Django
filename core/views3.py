from django.shortcuts import render
from .forms import PesquisaClimaForm

def home(request):
    return render(request, 'home.html')

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