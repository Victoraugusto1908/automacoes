import time
from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import Solicitacoes, DefStatusSolicitacoes
from pathlib import Path
import sys

# Adiciona o diretório pai ao PYTHONPATH
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.resolve()
sys.path.append(str(PROJECT_ROOT))

from scripts import copia_declaracao

class Command(BaseCommand):
    SCRIPT_MAP = {
        '1': copia_declaracao,
    }

    def processar_tarefa(self, tarefa, SCRIPT_MAP):
        status_em_processamento = DefStatusSolicitacoes.objects.get(status_solicitacao_id=2)
        status_processado_com_sucesso = DefStatusSolicitacoes.objects.get(status_solicitacao_id=4)
        status_processado_com_erros = DefStatusSolicitacoes.objects.get(status_solicitacao_id=3)

        with transaction.atomic():
            tarefa.status_solicitacao_id = status_em_processamento # Atualiza o status da tarefa para "em processamento"
            tarefa.save()

            try:
                documento_id = str(tarefa.documento_id.documento_id)
                # self.stdout.write(self.style.SUCCESS(f"{documento_formatado}"))
                modulo = SCRIPT_MAP.get(documento_id)

                resultado = modulo.main(tarefa.cnpj, tarefa.ambiente, tarefa.certificado, tarefa.data_inicial, tarefa.data_final)
                with transaction.atomic():
                    tarefa.refresh_from_db()
                    tarefa.status_id = status_processado_com_sucesso # Atualiza o status da tarefa para "concluida"
                    tarefa.save()

                self.stdout.write(self.style.SUCCESS(f"Tarefa {tarefa.solicitacao_id} processado com sucesso!"))

            except Exception as e:
                with transaction.atomic():
                    tarefa.refresh_from_db()
                    tarefa.status_id = status_processado_com_erros # Atualiza o status da tarefa para "erro"
                    tarefa.save()
                
                self.stdout.write(self.style.ERROR(f'Erro ao processar tarefa {tarefa.solicitacao_id}: {str(e)}'))

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Worker iniciado. Press Ctrl+C para sair.'))
        while True:
            try:
                with transaction.atomic():
                    tarefa = Solicitacoes.objects.select_for_update(skip_locked=True).filter(status_solicitacao_id=1).first()

                    if tarefa:
                        self.processar_tarefa(tarefa)

                    else:
                        self.stdout.write(self.style.SUCCESS('Nenhuma tarefa encontrada. Aguardando...'))
                        time.sleep(5)
            
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS('Worker encerrado.'))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro: {str(e)}"))
                time.sleep(10)  # Espera 10 segundos antes de tentar novamente

            



