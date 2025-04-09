from django.db import models
import uuid

class Solicitacoes(models.Model):
    solicitacao_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cnpj = models.CharField(max_length=14, unique=True)
    ambiente = models.CharField(max_length=200)
    certificado = models.BooleanField(default=False)
    data_inicial = models.DateField()
    data_final = models.DateField()
    documento_id = models.ForeignKey('DefDocumentos', on_delete=models.CASCADE)
    status_solicitacao_id = models.ForeignKey('DefStatusSolicitacoes', on_delete=models.CASCADE)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_alteracao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Solicitação: {self.solicitacao_id}, {self.cnpj}, {self.ambiente}, {self.certificado}, {self.data_inicial}, {self.data_final}, {self.documento_id}, {self.status_solicitacao_id}"
    
class DefStatusSolicitacoes(models.Model):
    status_solicitacao_id = models.AutoField(primary_key=True) # PK númerica
    descricao = models.CharField(max_length=200)

    def __str__(self):
        return f"DefStatusSolicitacoes: {self.status_solicitacao_id}, {self.descricao}"

class DefDocumentos(models.Model):
    documento_id = models.AutoField(primary_key=True)
    descricao = models.CharField(max_length=200)

    def __str__(self):
        return f"DefDocumentos: {self.documento_id}, {self.descricao}"