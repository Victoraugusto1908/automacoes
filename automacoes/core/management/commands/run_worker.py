import importlib
import time
from django.core.management.base import BaseCommand
from django.db import transaction
from automacoes.api.models import Solicitacoes

class Command(BaseCommand):

    def processar_tarefa(self, tarefa):
        tarefa.status_solicitacao_id = 2 # Atualiza o status da tarefa para "em processamento"
        tarefa.save()

        try:
            modulo_script = fr"C:\Users\victor.gomes\Documents\projeto_automacoes\automacoes\scripts\{tarefa.document_id}.py"
            modulo = importlib.import_module(modulo_script)
            
            resultado = modulo.main(tarefa.cnpj, tarefa.ambiente, tarefa.certificado, tarefa.data_inicial, tarefa.data_final)

            tarefa.status_id = 4 # Atualiza o status da tarefa para "concluida"
            tarefa.save()

            self.stdout.write(self.style.SUCCESS(f"Tarefa {tarefa.solicitacao_id} processado com sucesso!"))

        except Exception as e:
            tarefa.status_id = 3 # Atualiza o status da tarefa para "erro"
            tarefa.save()
            
            self.stdout.write(self.style.ERROR(f'Erro ao processar tarefa {tarefa.solicitacao_id}: {str(e)}'))

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Worker iniciado. Press Ctrl+C para sair.'))
        while True:
            try:
                transaction.atomic()
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

            



