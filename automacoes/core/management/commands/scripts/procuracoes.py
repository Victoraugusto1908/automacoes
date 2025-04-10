from biblioteca import *
from certificateSelector import *
from bookeepingXMLTeste import *

output_path = r"C:\Users\victor.gomes\Desktop\codigos\automacoes\procuracoes"

# Pegando o token do request
token = accessToken()

if token == False:
    print("Não será possível rodar o processo pois a requisição de autenticação foi negada.")
    logs.info("Não será possível rodar o processo pois a requisição de autenticação foi negada.")

else:
    driver = chrome_options_def(output_path)
    helper = SeleniumHelper(driver)

    CertificateSelector('33242075000138.pfx', 'Fisco2024')

    try:
        if login(driver):
            print("Login efetuado com sucesso.")

            situacao = "Ativas"
            if search_procuracoes(driver, situacao):
                print("Procurações pesquisadas com sucesso.")

                quant_pages = count_pages(driver)
                if quant_pages:
                    print("Elemento de tabela de páginas lido com sucesso.")

                    # iterando sobre as páginas lidas
                    for pag in range(1, quant_pages + 1):
                        for line in range(2, 22):
                            try:
                                env_list = readProcurations(driver, line, situacao)
                                if env_list:
                                    print(f"Procuração da empresa {env_list[1]} lida.")
                                    logs.info(f"Procuração da empresa {env_list[1]} lida.")
                                    
                                    # Escriturar resultados no XML
                                    output = arquive(env_list, output_path)
                                    bookeeping_xml(env_list, output)

                                    # Formatando os dados para o Post
                                    try:
                                        env_post = formatar(env_list)
                                        if env_post:
                                            response = PostEndPoint(env_post, token)

                                            status_code = response.status_code

                                            if status_code == 204:
                                                print("Requisição Post bem sucedida!")
                                                logs.info("Request finished.")
                                            elif status_code == 401:
                                                logs.info("Requisição com o token vencido.")
                                                # Pegando o token novamente
                                                token = accessToken()
                                                if token:
                                                    response = PostEndPoint(env_post, token)
                                                    logs.info("Requisição finished.")
                                                else:
                                                    logs.erro("Requisições finalizadas com erros.")
                                            else:
                                                print(f"Erro: {status_code} - {response.text}")
                                                logs.erro(f"Erro: {status_code} - {response.text}")

                                    except Exception as e:
                                        print(f"""Algo não saiu como o esperado para a requisição Post: {e} \n {response}""")
                                        logs.erro(f"Algo não saiu como o esperado para a requisição Post: {e}\n {response}")
                            
                            except Exception as e:
                                print(f"Houve algum erro na leitura da procuração: {e}")
                                logs.erro(f"""Houve um erro na leitura da procuração: {e}
                                            Tentando recarregar a página.""")
                                
                                # Capturando o erro
                                if helper.texto_elemento(By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[1]/div/div/div/div[2]') == 'ERR_CONNECTION_RESET':
                                    logs.info("Conexão com o ecac resetada.")
                                    driver.refresh()
                                    env_list = readProcurations(driver, line, situacao)
                                    if env_list:
                                        logs.info("Recarregando a página, conseguimos ler a procuração novamente.")
                                        print(f"Procuração da empresa {env_list[1]} lida.")
                                        
                                        # Escriturar resultados no XML
                                        output = arquive(env_list, output_path)
                                        bookeeping_xml(env_list, output)
                            
                        # Trocando de página para continuar lendo as procurações
                        if trocar_pag(driver, pag):
                            continue

                        else:
                            print("Não foi possível trocar de página.")
                            logs.erro("Não foi posível trocar de página.")

                else:
                    print("Houve algum erro ao ler o elemento da lista de páginas.")
                    logs.erro("Houve algum erro ao ler o elemento da lista de páginas.")

            else:
                print("Houve algum erro ao pesquisar as procurações.")
                logs.erro("Houve algum erro ao pesquisar as procurações.")

        else:
            print("Não foi possível realizar o Login no portal do e-cac.")
            logs.erro("Não foi possível realizar o login no portal do e-cac.")

    except Exception as e:
        print(f"Houve algum problema na leitura das procurações: '{e}'")
        logs.erro(f"Houve algum problema na leitura das procurações: '{e}'")
            
    driver.close()

    # Repetindo para as canceladas
    driver = chrome_options_def(driver)

    CertificateSelector()

    try:
        if login(driver):
            print("Login efetuado com sucesso.")

            situacao = "Canceladas"
            if search_procuracoes(driver, situacao):
                print("Procurações pesquisadas com sucesso.")

                quant_pages = count_pages(driver)
                if quant_pages:
                    print("Elemento de tabela de páginas lido com sucesso.")

                    # iterando sobre as páginas lidas
                    for pag in range(1, quant_pages + 1):
                        for line in range(2, 22):
                            try:
                                env_list = readProcurations(driver, line, situacao)
                                if env_list:
                                    print(f"Procuração da empresa {env_list[1]} lida.")
                                    logs.info(f"Procuração da empresa {env_list[1]} lida.")
                                    
                                    # Escriturar resultados no XML
                                    output = arquive(env_list, output_path)
                                    bookeeping_xml(env_list, output)

                                    # Formatando os dados para o Post
                                    try:
                                        env_post = formatar(env_list)
                                        if env_post:
                                            response = PostEndPoint(env_post, token)

                                            status_code = response.status_code

                                            if status_code == 204:
                                                print("Requisição Post bem sucedida!")
                                                logs.info("Request finished.")
                                            elif status_code == 401:
                                                logs.info("Requisição com o token vencido.")
                                                # Pegando o token novamente
                                                token = accessToken()
                                                if token:
                                                    response = PostEndPoint(env_post, token)
                                                    logs.info("Requisição finished.")
                                                else:
                                                    logs.erro("Requisições finalizadas com erros.")
                                            else:
                                                print(f"Erro: {status_code} - {response.text}")
                                                logs.erro(f"Erro: {status_code} - {response.text}")

                                    except Exception as e:
                                        print(f"""Algo não saiu como o esperado para a requisição Post: {e} \n {response}""")
                                        logs.erro(f"Algo não saiu como o esperado para a requisição Post: {e}\n {response}")
                            
                            except Exception as e:
                                print(f"Houve algum erro na leitura da procuração: {e}")
                                logs.info(f"""Houve um erro na leitura da procuração: {e}
                                            Tentando recarregar a página.""")
                                
                                # Capturando o erro
                                if helper.texto_elemento(By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[1]/div/div/div/div[2]') == 'ERR_CONNECTION_RESET':
                                    logs.info("Conexão com o ecac resetada.")
                                    driver.refresh()
                                    env_list = readProcurations(driver, line, situacao)
                                    if env_list:
                                        logs.info("Recarregando a página, conseguimos ler a procuração novamente.")
                                        print(f"Procuração da empresa {env_list[1]} lida.")
                                        
                                        # Escriturar resultados no XML
                                        output = arquive(env_list, output_path)
                                        bookeeping_xml(env_list, output)
                            
                        # Trocando de página para continuar lendo as procurações
                        if trocar_pag(driver, pag):
                            continue

                        else:
                            print("Não foi possível trocar de página.")
                            logs.erro("Não foi posível trocar de página.")

                else:
                    print("Houve algum erro ao ler o elemento da lista de páginas.")
                    logs.erro("Houve algum erro ao ler o elemento da lista de páginas.")

            else:
                print("Houve algum erro ao pesquisar as procurações.")
                logs.erro("Houve algum erro ao pesquisar as procurações.")

        else:
            print("Não foi possível realizar o Login no portal do e-cac.")
            logs.erro("Não foi possível realizar o login no portal do e-cac.")

    except Exception as e:
        print(f"Houve algum problema na leitura das procurações: '{e}'")
        logs.erro(f"Houve algum problema na leitura das procurações: '{e}'")
    

    leave_safely(driver)

    driver.close()

    # Limpando a pattern do certificado
    pathOfstringValue = 'SOFTWARE\Policies\Google\Chrome\AutoSelectCertificateForUrls'
    stringValueName = '1'
    clearCertificate(stringValueName, 'limpo', pathOfstringValue)
    logs.info(f"Pattern limpo com sucesso.")

    driver.quit()
