from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('previsao/', views.previsao, name='previsao'),
    path('calendario/', views.calendario, name='calendario'),
    path('eventos/', views.eventos, name='eventos'),
    path('eventos/<int:evento_id>/apagar/', views.apagar_evento, name='apagar_evento'),
    path('pesquisa-clima/', views.pesquisar_clima, name='pesquisa_clima'),
    path('alertas/', views.alertas, name='alertas'),
    path('config/', views.config, name='config'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('alertas/', views.alertas, name='alertas'),
    path('config/', views.config, name='config'),
]
