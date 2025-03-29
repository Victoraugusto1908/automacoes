# api/urls.py
from django.urls import path
from . import views  # Supondo que você tenha views na pasta api
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Suas URLs da API
    path('hello/', views.HelloView.as_view(), name='hello'),  # Exemplo de rota
    path('schema/', SpectacularAPIView.as_view(), name='schema'),  # Geração do schema
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
