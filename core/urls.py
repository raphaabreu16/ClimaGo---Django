from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('previsao/', views.previsao, name='previsao'),
    path('calendario/', views.calendario, name='calendario'),
    path('eventos/', views.eventos, name='eventos'),
    path('pesquisa-clima/', views.pesquisar_clima, name='pesquisa_clima'),
<<<<<<< HEAD
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
=======
    path('alertas/', views.alertas, name='alertas'),
    path('config/', views.config, name='config'),
>>>>>>> 0deb9d4abfffe2852ccbd9232eaa264978aa8506
]