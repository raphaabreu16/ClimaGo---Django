from django.contrib import admin
from .models import (
    Perfil,
    Localizacao,
    EventoCalendario,
    PrevisaoClimatica,
    Alerta,
    ConfiguracaoAlerta,
)


admin.site.register(Perfil)
admin.site.register(Localizacao)
admin.site.register(EventoCalendario)
admin.site.register(PrevisaoClimatica)
admin.site.register(Alerta)
admin.site.register(ConfiguracaoAlerta)