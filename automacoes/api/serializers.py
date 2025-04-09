from rest_framework import serializers
import re
from .models import Solicitacoes

class SolicitacoesSerializer(serializers.Serializer):
    cnpj = serializers.CharField(
        max_length=14, min_length=14,
        validators=[
            lambda value: re.match(r'^\d{14}$', value) or serializers.ValidationError("CNPJ deve conter exatamente 14 dígitos númericos.")
        ]
    )
    ambiente = serializers.CharField(max_length=200)
    certificado = serializers.BooleanField()
    data_inicial = serializers.DateField()
    data_final = serializers.DateField()
    documento = serializers.IntegerField()

    class Meta:
        model = Solicitacoes
        fields = ['cnpj', 'ambiente', 'certificado', 'data_inicial', 'data_final', 'documento']