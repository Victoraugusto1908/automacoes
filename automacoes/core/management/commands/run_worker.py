import time
from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import Solicitacoes, DefStatusSolicitacoes
import subprocess
import os

class Command(BaseCommand):

    def processar_tarefa(self, tarefa):
        status_em_processamento = DefStatusSolicitacoes.objects.get(status_solicitacao_id=2)
        status_processado_com_sucesso = DefStatusSolicitacoes.objects.get(status_solicitacao_id=4)
        status_processado_com_erros = DefStatusSolicitacoes.objects.get(status_solicitacao_id=3)

        with transaction.atomic():
            tarefa.status_solicitacao_id = status_em_processamento # Atualiza o status da tarefa para "em processamento"
            tarefa.save()

            try:
                # Executa o script correpondente do documento_id
                script_path = fr"C:\Users\victor.gomes\Documents\projeto_automacoes\automacoes\core\management\commands\scripts\{tarefa.documento_id.documento_id}.py"

                command = [
                    r"C:\Users\victor.gomes\Documents\projeto_automacoes\app\Scripts\python.exe",
                    script_path,
                    tarefa.cnpj, tarefa.ambiente, str(tarefa.certificado), str(tarefa.data_inicial), str(tarefa.data_final)
                ]

                resultado = subprocess.run(command, capture_output=True, text=True)
                with transaction.atomic():
                    tarefa.refresh_from_db()
                    tarefa.status_id = status_processado_com_sucesso # Atualiza o status da tarefa para "concluida"
                    tarefa.save()

                self.stdout.write(self.style.SUCCESS(f"Tarefa {tarefa.solicitacao_id} processado com sucesso!"))

            except subprocess.CalledProcessError as e:
                with transaction.atomic():
                    tarefa.refresh_from_db()
                    tarefa.status_id = status_processado_com_erros # Atualiza o status da tarefa para "erro"
                    tarefa.save()
                
                self.stdout.write(self.style.ERROR(f'Erro na execução do Script {script_path} {tarefa.solicitacao_id}: {str(e)}'))
            
            except FileNotFoundError:
                with transaction.atomic():
                    tarefa.refresh_from_db()
                    tarefa.status_id = status_processado_com_erros
                    tarefa.save()
                
                self.stdout.write(self.style.ERROR(f'Arquivo não encontrado: {script_path}'))

            except Exception as e:
                with transaction.atomic():
                    tarefa.refresh_from_db()
                    tarefa.status_id = status_processado_com_erros
                    tarefa.save()
                
                self.stdout.write(self.style.ERROR(f"Erro inesperado: {str(e)}"))

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

            



