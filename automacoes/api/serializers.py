from rest_framework import serializers
import re
from .models import Solicitacoes, DefStatusSolicitacoes, DefDocumentos

class DefDocumentosSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefDocumentos
        fields = ['documento_id']

class SolicitacoesSerializer(serializers.ModelSerializer):
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
    documento_id = serializers.PrimaryKeyRelatedField(queryset=DefDocumentos.objects.all())

    class Meta:
        model = Solicitacoes
        fields = ['solicitacao_id', 'cnpj', 'ambiente', 'certificado', 'data_inicial', 'data_final', 'documento_id']
    
    def create(self, validated_data):
        try:
            status_solicitacao = DefStatusSolicitacoes.objects.get(pk=1)
        except DefStatusSolicitacoes.DoesNotExist:
            raise serializers.ValidationError("Status de solicitação não encontrado.")
        
        validated_data['status_solicitacao_id'] = status_solicitacao
        return Solicitacoes.objects.create(**validated_data)