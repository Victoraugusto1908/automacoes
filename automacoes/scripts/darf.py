from biblioteca import *
from certificateSelector import *

path = r"C:\Users\victor.gomes\Desktop\codigos\automacoes\darf"
cnpj = '09352161000119'
varAttempt = True

CertificateSelector(r"33242075000138.pfx", 'Fisco2024')

# iniciando uma instância no driver
driver = chrome_options_def(path)
helper = SeleniumHelper(driver)

if login(driver):
    print("Login realizado com sucesso!")

    # Fazendo o login no perfil do procurador
    if perfil_procurador(driver, cnpj):
        try:
            # Indo para o endereço da aplicação
            driver.get("https://cav.receita.fazenda.gov.br/Servicos/ATFLA/PagtoWeb.app/Default.aspx")

            # Iterando sobre os meses
            months_list = lista_meses()
            for mes in months_list:
                if search_darf(driver, mes[0], mes[1]):
                    try:
                        # Verificando o erro de não existir nenhuma arrecadação para o período pesquisado
                        sleep(2)
                        alert = driver.switch_to.alert
                        alert_text = alert.text
                        print("Texto do alerta:", alert_text)
                        alert.accept()

                        # Testando o alerta
                        if alert_text == "Nenhuma arrecadação localizada.":
                            print("Nenhum arrecadação localizada para o período pesquisado. Realizando a busca para outro período.")
                            logs.info("Nenhum arrecadação localizada para o período pesquisado. Realizando a busca para outro período.")

                    except UnexpectedAlertPresentException:
                        print("Abriu um alerta inexperado. Agora da pra tratar.")
                        logs.erro("Abriu um alerta inexperado não tratado. Verificar para corrigir o erro.")
                    
                    except NoAlertPresentException:
                        if varAttempt == True:
                            varAttempt = attempt(driver, varAttempt, path)
                            search_darf(driver, mes[0], mes[1])

                        quantidade_linhas = CountLines(driver)
                        if quantidade_linhas:
                            ListaDosCodigos = codigosList(driver, quantidade_linhas)
                            if ListaDosCodigos:
                                for code in ListaDosCodigos:
                                    logs.info(f"Baixando os comprovantes do código {code}")
                                    if download_pdf(driver, code, quantidade_linhas):
                                        print("Download realizado com sucesso.")
                                        logs.info("Download realizado com sucesso.")
                                        # Verificando se o download acabou
                                        while any(arquivo.endswith(".crdownload") for arquivo in os.listdir(path)):
                                            print("Aguardando o término do download....")
                                            sleep(1)
                                        rename_file_darf(code, mes[0], path)
                                    else:
                                        logs.erro("Houve um erro ao realizar o download do arquivo.")
                                # Voltando para pesquisar outro mês
                                helper.clicar_elemento(By.ID, 'BtnRetornar')

                            else:
                                logs.erro("Houve um erro ao obter a lista com os codigos disponíveis para aquela pesquisa de DARF.")
                        else:
                            logs.erro("Houve um erro ao calcular o número de linhas do resultado da pesquisa DARF.")
                    except Exception as e:
                        logs.erro(f"Houve algum erro inesperado ao procurar os DARFs. ({e})")
                else:
                    logs.erro("Houve um erro ao pesquisar as procurações.")
        except ConnectionError:
            logs.erro("Sem conexão com a internet script DARF.")
        except FileNotFoundError:
            logs.erro("Esse endereço não existe para pesquisa DARF.")
        except Exception as e:
            logs.erro(f"Houve alguma falha ao executar o script de pesquisa DARF: {e}")
    else:
        logs.erro("Houve um erro ao logar no perfil do procurador na pesquisa DARF.")
else:
    logs.erro("Houve um erro ao realizar o login no e-cac.")

# Limpando a pattern do certificado
pathOfstringValue = 'SOFTWARE\Policies\Google\Chrome\AutoSelectCertificateForUrls'
stringValueName = '1'
clearCertificate(stringValueName, 'limpo', pathOfstringValue)
logs.info(f"Pattern limpo com sucesso.")

if leave_safely(driver) == 'Logout realizado com sucesso':
    print("Logout realziado com sucesso.")
else:
    print("Houve algum erro ao realizar o logout.")

driver.close()
driver.quit()