from biblioteca import *
from certificateSelector import *

path = r"C:\Users\victor.gomes\Desktop\codigos\automacoes\dctfweb"
cnpj = '15103354000139'
attempt = True

CertificateSelector("33242075000138.pfx", 'Fisco2024')

# iniciando uma instância no driver
driver = chrome_options_def(path)

if login(driver):
    print("Login realizado com sucesso!")

    # Fazendo o login no perfil do procurador
    if perfil_procurador(driver, cnpj):
        try:
            driver.get('https://cav.receita.fazenda.gov.br/ecac/Aplicacao.aspx?id=10015&origem=menu')
            sleep(2)

            driver.get('https://dctfweb.cav.receita.fazenda.gov.br/AplicacoesWeb/DCTFWeb/Paginas/Captcha.aspx') # Link da aplicação
            sleep(2)

            # Tentando passar pelo Captcha
            if captcha(driver):
                print("Conseguimos passar pelo Captcha!")

                ApurLista = ApurList()
                if ApurLista:
                    for ano in ApurLista:
                        if search_dctfweb(driver, ano, attempt):
                            print("Declarações pesquisadas com sucesso.")
                            attempt = False

                            verify = verify_search(driver)
                            if verify == "Nenhuma declaração encontrada":
                                print(verify)

                            elif verify == "Ativa":
                                # Iterando sobre os resultados
                                for i in range(2, 14):
                                    download = download_DCTFWeb(driver, i)
                                    if download:
                                        print("Download realizado com sucesso.")
                                    else:
                                        print("Download do arquivo não realizado.")

                            else: 
                                print(f"Não conseguimos verificar o retorno da pesquisa: {verify}")
                                logs.erro(f"Não conseguimos verificar o retorno da pesquisa: {verify}")
                        else:
                            print("Não consegui pesquisar as declarações.")
                            logs.erro("Não consegui pesquisar as declarações.")
                else:
                    print("Houve uma falha ao tentar elaborar a lista dos períodos de apuração.")
                    logs.erro("Houve uma falha ao tentar elaborar a lista dos períodos de apuração.")
            else:
                print("Houve uma falha ao passar pelo Captcha.")
                logs.erro("Houve uma falha ao passar pelo Captcha.")

        except ConnectionError:
            print("Sem conexão com a internet.")
            logging.info("Sem conexão com a internet.")
        except FileNotFoundError:
            print("Esse endereço não existe.")
            logging.info("Esse endereço não existe.")
        except Exception as e:
            print(f"Erro do tipo nível 1: {e}")
            logs.erro(f"Erro do tipo nível 1: {e}")
    else:
        print("Houve um erro ao realizar o login no perfil do cliente.")
        logs.erro("Houve um erro ao realizar o login no perfil do cliente.")

else:
    print("Houve um erro ao realizar o login no e-cac.")
    logs.erro("Houve um erro ao realizar o login no e-cac.")

# Limpando a pattern do certificado
pathOfstringValue = 'SOFTWARE\Policies\Google\Chrome\AutoSelectCertificateForUrls'
stringValueName = '1'
clearCertificate(stringValueName, 'limpo', pathOfstringValue)
logs.info(f"Pattern limpo com sucesso.")

sleep(2)
if leave_safely(driver):
    driver.close()
    driver.quit()
else:
    print("Sai com segurança do e-cac.")
    