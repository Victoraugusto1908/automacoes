# api/urls.py
from django.urls import path
from .views import ConsultaAPIView  
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Minha API",
        default_version='v1',
        description="Documentação da API",
    ),
    public=True,
)

urlpatterns = [
    # Suas URLs da API
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-docs'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc-docs'),
    path('consulta/', ConsultaAPIView.as_view(), name='consulta'),  # Exemplo de rota
    path('schema/', SpectacularAPIView.as_view(), name='schema'),  # Geração do schema
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
