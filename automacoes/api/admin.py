from django.contrib import admin
from .models import DefDocumentos, DefStatusSolicitacoes, Solicitacoes

# Register your models here.
admin.site.register(DefDocumentos)
admin.site.register(DefStatusSolicitacoes)
admin.site.register(Solicitacoes)