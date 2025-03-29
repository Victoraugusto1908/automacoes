# views.py
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class HelloView(APIView):
    @extend_schema(
        responses={200: 'Mensagem de sucesso'}
    )
    def get(self, request):
        # Acessa o parâmetro 'name' diretamente da query string
        name = request.query_params.get('name', 'Munfo')  # Default 'Munfo' caso 'name' não seja passado
        return Response({'message': f'Olá, {name}'}, status=status.HTTP_200_OK)


