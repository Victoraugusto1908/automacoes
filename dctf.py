from biblioteca import *
from certificateSelector import *
import sys

logs.info("Só para teste!")

cnpj = sys.argv[0]
ambiente = sys.argv[1]
certificado = sys.argv[2]
data_inicial = sys.argv[3]
data_final = sys.argv[4]

dropbox_path = f"apiauditorteste.grupofiscoplan.com.br"
path = "app/download"

ACCESS_TOKEN = os.getenv('DROPBOX_ACCES_TOKEN')

if ACCESS_TOKEN is None:
    raise ValueError("O token de acesso do Dropbox não está configurado.")

if certificado:
    CertificateSelector("/app/codigos/Fiscoplan - Fisco2011.pfx", 'Fisco2011')
    perfilProcurador = True
else: # Pra quando for certificado da própria empresa
    path_certificado = "/app/ceritificados"
    for certificate in os.listdir(path_certificado):
        try:
            certificado_cnpj, certificado_senha = certificate.split("-")
            if certificado_cnpj == cnpj:
                arquivo_caminho = os.path.join(path_certificado, cnpj + "-" + certificado_senha + ".pfx")
                CertificateSelector(arquivo_caminho, certificado_senha)
                perflProcurador = False
                break
        except ValueError:
            continue

# iniciando uma instância no driver
driver = chrome_options_def(path)
helper = SeleniumHelper(driver)

if login(driver):
    print("Login realizado com sucesso!")

    # Fazendo o login no perfil do procurador
    if perfilProcurador == True:
        try:
            perfil_procurador(driver, cnpj)
            validation = True
        except Exception as e:
            logs.erro(f"[DCTF] Houve um erro ao realizar o login no perfil do cliente: {e}")
            validation = False
    if perfilProcurador == False:
        logs.info("[DCTF] Usando certificado da própria empresa.")
    
    if validation == True:
        try:
            driver.get('https://cav.receita.fazenda.gov.br/Servicos/ATSPO/DCTF/Consulta/Abrir.asp')
            helper.clicar_elemento(By.XPATH, '/html/body/div/div[2]/div/form/table/tbody/tr/th/input')
            
            # Contando quantas linhas tenho na tabela
            count_lines = quantLines(driver)
            if count_lines:
                print(f"Achamos {count_lines} na tabela.")
                logs.info(f"Achamos {count_lines} na tabela.")

                # Iterando sobre o resultado
                for tr in range(2, count_lines + 1):
                    if download_dctf(driver, tr):
                        # Testando para ver se o download já acabou
                        while any(f.endswith('.crdownload') for f in os.listdir(path)):
                            logs.info("Download ainda em andamento")
                            sleep(1)
                        data = get_date(driver, tr)
                        if data:
                            if rename_file_dctf(path, data):
                                print("Download realizado com sucesso.")
                                logs.info("[DCTF]Download realizado com sucesso.")

                                try:
                                    upload_arquivo(ACCESS_TOKEN, path, dropbox_path)
                                    logs.info("[DCTF] Arquivo enviado para o dropbox com sucesso!")

                                except Exception as e:
                                    logs.erro(f"[DCTF] Houve um erro ao transmitir o arquivo para o dropbox: {e}")
                            else:
                                print("Não consegui renomear o arquivo")
                                logs.info("Não consegui renomear o arquivo")
                        else:
                            logs.erro("[DCTF] Houve um erro ao pegar a data.")
                    else:
                        logs.erro("[DCTF] Houve algum erro no download dos arquivos.")
            else:
                logs.erro("[DCTF] Não foi possível localizar a quantidade de linhas que temos na tabela.")
        except ConnectionError:
            logs.erro("[DCTF] Sem conexão com a internet.")
        except FileNotFoundError:
            logs.erro("[DCTF] Esse endereço não existe.")
        except Exception as e:
            logs.erro(f"Erro ao executar o script DCTF: {e}")
else:
    logs.erro("[DCTF] Houve um erro ao realizar o login no e-cac.")

# Limpando a pattern do certificado
# pathOfstringValue = 'SOFTWARE\Policies\Google\Chrome\AutoSelectCertificateForUrls'
# stringValueName = '1'
# clearCertificate(stringValueName, 'limpo', pathOfstringValue)
# logs.info(f"Pattern limpo com sucesso.")

if leave_safely(driver):
    driver.close()
    driver.quit()
else:
    print("Sai com segurança do e-cac.")
    logs.info("Script encerrado com sucesso.")