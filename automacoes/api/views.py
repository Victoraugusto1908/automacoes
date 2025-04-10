# views.py
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SolicitacoesSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import JSONParser

class SolicitacoesAPIView(APIView):
    @swagger_auto_schema(
        request_body=SolicitacoesSerializer
    )

    def post(self, request, *ags, **kwargs):
        if not request.content_type == "application/json":
            return Response({"error": "Content-Type deve ser application/json"}, status=400)
        serializer = SolicitacoesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"mensagem": "Dados recebidos com sucesso!", 
                 "dados": serializer.data}, 
                 status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


