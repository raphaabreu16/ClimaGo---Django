from django.utils import timezone
from datetime import timedelta

from core.models import (
    Usuario, Localizacao, EventoCalendario,
    PrevisaoClimatica, Alerta, ConfiguracaoAlerta
)

def run():

    u1 = Usuario.objects.create(
        nome="Joao Vianna",
        email="joaovianna@gmail.com",
        fuso_horario="America/Rio_de_Janeiro"
    )

    u2 = Usuario.objects.create(
        nome="Victor Hugo",
        email="vh@gmail.com",
        fuso_horario="America/Rio_de_Janeiro"
    )

    l1 = Localizacao.objects.create(
        usuario=u1,
        cidade="Rio de Janeiro",
        estado="RJ",
        pais="Brasil",
        latitude=-22.9068,
        longitude=-43.1729,
        apelido_local="Casa"
    )


    EventoCalendario.objects.create(
        usuario=u1,
        titulo="Treino",
        data_inicio=timezone.now() + timedelta(hours=3),
        data_fim=timezone.now() + timedelta(hours=4),
        tipo_evento="saude",
        prioridade="media",
        local_evento="Academia",
        localizacao=l1
    )

    print("Banco populado com sucesso!")
