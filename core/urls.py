from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('previsao/', views.previsao, name='previsao'),
    path('calendario/', views.calendario, name='calendario'),
]