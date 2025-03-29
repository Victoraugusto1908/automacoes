import os
import json
import time
import shutil
import subprocess
import logging

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

#Classe do log
class logs:
    log = "/app/log/INFO.log"
    logging.basicConfig(filename= log, format = "%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO, encoding='UTF-8')
    """Def para quando for uma informação"""
    @staticmethod
    def info(str):
        logging.info(str)

    """Def para quando for um erro"""
    @staticmethod
    def erro(str):
        logging.error(str)

def chamados(dados, caminho, arquivo):
    processados = "/app/txts/processados"
    # processados = r"C:\Users\victor.gomes\Desktop\codigos\automacoes\automacoes\txts\processado"
    erros = "/app/txts/erros"
    # erros = r"C:\Users\victor.gomes\Desktop\codigos\automacoes\automacoes\txts\erros"

    cnpj = dados['cnpj']
    ambiente = dados['ambiente']
    certificado = "1" if dados['certificado'] else "0"
    data_inicial = dados['data_inicial']
    data_final = dados['data_final']
    documento = int(dados['documento'])
    
    #Executando download DCTF
    if documento == 0:
        comando = ["python", 
                   "codigos/dctf.py", 
                   cnpj, ambiente, certificado, data_inicial, data_final]
        try:
            resultado = subprocess.run(comando, capture_output=True, text=True, check=True)
            logs.info(f"Script executado com sucesso! Saída: {resultado.stdout}")
            sucesso = os.path.join(processados, arquivo)
            shutil.move(caminho, sucesso)
        except subprocess.CalledProcessError as e:
            logs.erro(f"Erro na execução do script. Código de erro: {e.returncode} - {e.stderr}")
            erro = os.path.join(erros, arquivo)
            shutil.move(caminho, erro)
        except FileNotFoundError:
            logs.erro("Python não encontrado. Verifique se está instalado e no PATH.")
            erro = os.path.join(erros, arquivo)
            shutil.move(caminho, erro)
        except Exception as e:
            logs.erro(f"Erro inesperado: {e} - Esses são os dados do json: {dados}")
            erro = os.path.join(erros, arquivo)
            shutil.move(caminho, erro)

def ler_json(caminho):
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        return dados
    except json.JSONDecodeError as e:
        logs.erro(f"Erro ao ler o JSON ({caminho}): {e}")

def monitorar():
    path = "/app/txts/pendentes"
    # path = r"C:\Users\victor.gomes\Desktop\codigos\automacoes\automacoes\txts\pendentes"
    destino = "/app/txts/processando"
    # destino = r"C:\Users\victor.gomes\Desktop\codigos\automacoes\automacoes\txts\processando"

    while True:
        for arquivo in os.listdir(path):
            if arquivo.endswith(".json"):
                caminho = os.path.join(path, arquivo)
                novo_caminho = os.path.join(destino, arquivo)

                try:
                    shutil.move(caminho, novo_caminho)
                    logs.info(f"Movido para 'processando': {novo_caminho}")
                    dados = ler_json(novo_caminho)

                    if dados:
                        chamados(dados, novo_caminho, arquivo)
                    else:
                        logs.erro(f"JSON inválido: {novo_caminho}")
                        shutil.move(novo_caminho, os.path.join("/app/txts/erros", arquivo))

                except Exception as e:
                    logs.erro(f"Erro ao movero arquivo {arquivo}: {e}")
        time.sleep(10)

if __name__ == "__main__":
    monitorar()
