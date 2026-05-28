from django import forms

class PesquisaClimaForm(forms.Form):

    cidade = forms.CharField(
        label='Cidade',
        max_length=100
    )
