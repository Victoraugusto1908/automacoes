from rest_framework import serializers

# Exemplo de um serializer para um modelo simples
class HelloSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False, default='Mundo')
