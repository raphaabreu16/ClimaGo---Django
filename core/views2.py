from django.shortcuts import render
from .forms import PesquisaClimaForm

def home(request):

    form = PesquisaClimaForm()

    return render(request, 'home.html', {
        'form': form
    })
