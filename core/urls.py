from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('previsao/', views.previsao, name='previsao'),
    path('calendario/', views.calendario, name='calendario'),
    path('eventos/', views.eventos, name='eventos'),
    path('pesquisa-clima/', views.pesquisar_clima, name='pesquisa_clima'),
    path('cadastro/', views.cadastro, name='cadastro'),
]