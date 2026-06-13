from django import forms

class PesquisaClimaForm(forms.Form):

    cidade = forms.CharField(
        label="Cidade",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Ex: Rio de Janeiro",
            "class": "form-control",
            "autocomplete": "off"
        })
    )

    estado = forms.CharField(
        label="Estado (opcional)",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Ex: RJ",
            "class": "form-control"
        })
    )

    pais = forms.CharField(
        label="País",
        max_length=100,
        required=False,
        initial="Brasil",
        widget=forms.TextInput(attrs={
            "placeholder": "Ex: Brasil",
            "class": "form-control"
        })
    )
