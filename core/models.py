from django.db import models
from django.contrib.auth.models import User


class Perfil(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    fuso_horario = models.CharField(
        max_length=100,
        default='America/Sao_Paulo'
    )

    def __str__(self):
        return self.user.username


class Localizacao(models.Model):
    usuario = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        related_name='localizacoes'
    )
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=100, blank=True, null=True)
    pais = models.CharField(max_length=100, default='Brasil')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    apelido_local = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        if self.apelido_local:
            return self.apelido_local
        return f'{self.cidade} - {self.estado}'


class EventoCalendario(models.Model):
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
    ]

    TIPO_EVENTO_CHOICES = [
        ('trabalho', 'Trabalho'),
        ('estudo', 'Estudo'),
        ('lazer', 'Lazer'),
        ('saude', 'Saúde'),
        ('outro', 'Outro'),
    ]

    usuario = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        related_name='eventos'
    )
    localizacao = models.ForeignKey(
        Localizacao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos'
    )
    titulo = models.CharField(max_length=150)
    descricao = models.TextField(blank=True, null=True)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    local_evento = models.CharField(max_length=200, blank=True, null=True)
    tipo_evento = models.CharField(
        max_length=30,
        choices=TIPO_EVENTO_CHOICES,
        default='outro'
    )
    prioridade = models.CharField(
        max_length=20,
        choices=PRIORIDADE_CHOICES,
        default='media'
    )

    def __str__(self):
        return self.titulo


class PrevisaoClimatica(models.Model):
    localizacao = models.ForeignKey(
        Localizacao,
        on_delete=models.CASCADE,
        related_name='previsoes'
    )
    data_hora = models.DateTimeField()
    temperatura = models.DecimalField(max_digits=5, decimal_places=2)
    temperatura_min = models.DecimalField(max_digits=5, decimal_places=2)
    temperatura_max = models.DecimalField(max_digits=5, decimal_places=2)
    umidade = models.IntegerField()
    velocidade_vento = models.DecimalField(max_digits=5, decimal_places=2)
    condicao_climatica = models.CharField(max_length=100)
    probabilidade_chuva = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f'{self.condicao_climatica} - {self.data_hora}'


class Alerta(models.Model):
    STATUS_LEITURA_CHOICES = [
        ('nao_lido', 'Não lido'),
        ('lido', 'Lido'),
    ]

    TIPO_ALERTA_CHOICES = [
        ('chuva', 'Chuva'),
        ('tempestade', 'Tempestade'),
        ('vento_forte', 'Vento forte'),
        ('calor_extremo', 'Calor extremo'),
        ('frio_extremo', 'Frio extremo'),
        ('outro', 'Outro'),
    ]

    evento = models.ForeignKey(
        EventoCalendario,
        on_delete=models.CASCADE,
        related_name='alertas'
    )
    previsao = models.ForeignKey(
        PrevisaoClimatica,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertas'
    )
    tipo_alerta = models.CharField(
        max_length=30,
        choices=TIPO_ALERTA_CHOICES
    )
    mensagem = models.TextField()
    data_hora_envio = models.DateTimeField()
    status_leitura = models.CharField(
        max_length=20,
        choices=STATUS_LEITURA_CHOICES,
        default='nao_lido'
    )
    antecedencia = models.IntegerField(
        help_text='Antecedência em minutos'
    )

    def __str__(self):
        return f'{self.tipo_alerta} - {self.evento.titulo}'


class ConfiguracaoAlerta(models.Model):
    usuario = models.OneToOneField(
        Perfil,
        on_delete=models.CASCADE,
        related_name='configuracao_alerta'
    )
    chuva = models.BooleanField(default=True)
    tempestade = models.BooleanField(default=True)
    vento_forte = models.BooleanField(default=True)
    calor_extremo = models.BooleanField(default=True)
    frio_extremo = models.BooleanField(default=True)
    antecedencia_padrao = models.IntegerField(
        default=60,
        help_text='Antecedência padrão em minutos'
    )
    notificacao_push_ativa = models.BooleanField(default=True)

    def __str__(self):
        return f'Configuração de {self.user.username}'