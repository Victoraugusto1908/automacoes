# api/urls.py
from django.urls import path
from . import views  # Supondo que você tenha views na pasta api

urlpatterns = [
    # Suas URLs da API
    path('hello/', views.hello_view, name='hello'),  # Exemplo de rota
]
