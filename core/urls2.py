```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path(
        'pesquisa-clima/',
        views.pesquisar_clima,
        name='pesquisa_clima'
    ),
]
```
