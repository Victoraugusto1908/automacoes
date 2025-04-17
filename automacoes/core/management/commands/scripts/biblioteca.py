import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException, NoAlertPresentException, NoSuchAttributeException
from selenium.common.exceptions import TimeoutException
import uuid
import os
from bs4 import BeautifulSoup
import requests
from time import sleep
import logging
from datetime import datetime
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
from dateutil.relativedelta import relativedelta
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from calendar import monthrange
import re
import dropbox
from pyautogui import hotkey

# Criando uma instância do webdriver
def chrome_options_def(path):
    chrome_options = uc.ChromeOptions()

    # JSON para configurar o destino como "Salvar como PDF"
    app_state = {
        "recentDestinations": [{"id": "Save as PDF", "origin": "local", "account": ""}],
        "selectedDestinationId": "Save as PDF",
        "version": 2,
        "isHeaderFooterEnabled": False
    }

    prefs = {
        "printing.print_preview_sticky_settings.appState": json.dumps(app_state),
        "download.default_directory": str(path),
        "profile.default_content_settings.popups": 0,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    }

    chrome_options.add_experimental_option("prefs", prefs)

    # Argumentos para disfarçar a automação
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--kiosk-printing')
    chrome_options.add_argument('--disable-print-preview')
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    chrome_options.add_argument(r"--user-data-dir=C:\Users\victor.gomes\AppData\Local\Google\Chrome\User Data")
    chrome_options.add_argument("--profile-directory=Profile 2")

    # Cria o driver SEM fixar version_main (ele detecta automaticamente)
    driver = uc.Chrome(options=chrome_options)

    # Remove o indicador de automação
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.navigator.chrome = {
                runtime: {}
            };
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3],
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['pt-BR', 'pt'],
            });
        """
    })

    logging.info(f"Iniciando o programa...")

    return driver

# Classe para o wait
class SeleniumHelper:
    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)  # Tempo de espera único para toda a classe

    def esperar_elemento_clicavel(self, by, valor):
        """Aguarda até que o elemento seja clicável e o retorna."""
        return self.wait.until(EC.element_to_be_clickable((by, valor)))
    
    def esperar_elemento_visivel(self, by, valor):
        """Aguarda até que o elemento seja visivel e o retorna."""
        return self.wait.until(EC.visibility_of_element_located((by, valor)))
    
    def esperar_presenca_elemento(self, by, valor):
        """Aguarda até que o elemento esteja presente e o retorna"""
        return self.wait.until(EC.presence_of_element_located((by, valor)))

    def clicar_elemento(self, by, valor):
        """Aguarda e clica no elemento."""
        elemento = self.esperar_elemento_clicavel(by, valor)
        elemento.click()
    
    def texto_elemento(self, by, valor):
        """Aguarda e captura o texto do elemento"""
        elemento = self.esperar_elemento_visivel(by, valor)
        return elemento.text
    
    def contar_elementos(self, by, valor, by_tag, tag):
        elemento = self.esperar_elemento_visivel(by, valor)
        return elemento.find_elements(by_tag, tag)
    
    def insert_keys_elemento(self, by, valor, keys):
        elemento = self.esperar_elemento_clicavel(by, valor)
        elemento.send_keys(keys)

    def clear_keys_elemento(self, by, valor):
        elemento = self.esperar_elemento_clicavel(by, valor)
        elemento.clear()
    
    def mover_para(self, by, valor, driver):
        elemento = self.esperar_presenca_elemento(by, valor)
        driver.switch_to.frame(elemento)

#Classe do log
class logs:
    log = "log.txt"
    def __init__(self, filename=log):
        logging.basicConfig(filename=filename, format = "%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO, encoding='UTF-8')

    """Def para quando for uma informação"""
    @staticmethod
    def info(str):
        logging.info(str)

    """Def para quando for um erro"""
    @staticmethod
    def erro(str):
        logging.error(str)

"""Def para entrar no ecac"""
def login(driver):
    helper = SeleniumHelper(driver)
    # Tentando acessar o link do portal
    try:
        driver.get("https://cav.receita.fazenda.gov.br/autenticacao/login")

        # Tentando clicar nos botões para logar com o certificado
        try:
            sleep(3)
            helper.clicar_elemento(By.XPATH, '/html/body/div[2]/div/div[2]/div/form/div[2]/p[2]/input') #/html/body/div[2]/div/div[2]/div/form/div[2]/p[2]/input

            sleep(3)
            helper.clicar_elemento(By.ID, "login-certificate")    

            logs.info(f"Login feito com sucesso.")

            sleep(10)
            return True
        
        except TimeoutError:
            print("Tempo de espera estourado")
            logs.erro(f"Erro: {TimeoutError}")
            return False

        except Exception as e:
            print(f"Erro nível 2: ({e})")
            logs.erro(f"Ocorreu algum problema ao passar pelo captcha: {e}")

            try:
                driver.delete_all_cookies()
                driver.execute_cdp_cmd('Network.clearBrowserCache', {})
                driver.refresh()

                try:
                    helper.clicar_elemento(By.XPATH, '/html/body/div[2]/div/div[2]/div/form/div[2]/p[2]/input') #/html/body/div[2]/div/div[2]/div/form/div[2]/p[2]/input
                    helper.clicar_elemento(By.ID, "login-certificate")
                    sleep(10)

                except Exception as e:
                    print(f"Erro nível 2: ({e})")
        
            except Exception as e:
                print(f"Erro ao limpar cookies e cache: {e}")
                return False

    except FileNotFoundError:
        print("Este endereço não existe.")
        logs.erro(f"este endereço não existe: {FileNotFoundError}")
        return False
    except ConnectionError:
        print("Sem acesso a internet ou o site está fora do ar")
        logs.erro(f"Sem conexação com a internet ou o site está fora do ar.")
        return False
    except TimeoutException as e:
        print(f"Tempo de espera estourado: {e}")
        logs.erro(f"Tempo de espera estourado: {e}")
        return False
    except Exception as e:
        print(f"Erro nível 1: ({e})")
        logs.erro(f"Não foi possível localizar alguma referência de elemento da página ao tentar logar no portal e-CAC: {e}")
        return False
    
"""Def para sair com segurança do e-cac"""
def leave_safely(driver):
    helper = SeleniumHelper(driver)
    try:
    # Indo para a página incial do e-cac
        driver.get('https://cav.receita.fazenda.gov.br/ecac/Default.aspx')
        sleep(3)

        helper.clicar_elemento(By.ID, 'sairSeguranca')

        # Verificando se deu certo
        return helper.texto_elemento(By.XPATH, '/html/body/div[1]/div[3]/h1')

    except Exception as e:
        print(f"Não foi possível localizar alguma coisa: {e}")
        logs.erro(f"Não foi possível localizar alguma coisa ao fazer o logout: {e}")

"""Def para pesquisar as procurações"""
def search_procuracoes(driver, situacao):
    helper = SeleniumHelper(driver)
    # Tentando get na app das procurações
    try:
        driver.get("https://cav.receita.fazenda.gov.br/servicos/ATSDR/Procuracoes.app/ProcuracoesControlador.asp?acao=Iniciar")

        # Selecionando os filtros para as procurações
        try:
            helper.clicar_elemento(By.ID, "consultaProcurador")
            print("Ativei os filtros")
            id_situacao = f"radioSituacaoProcuracao{situacao}"
            helper.clicar_elemento(By.ID, id_situacao)
            print(f"Selecionei só as {situacao}")

            helper.clicar_elemento(By.ID, "botProcurador")
            print("Consultar...")
            logs.info("Consultamos as procurações.")
            sleep(5)
            return True

        except Exception as e:
            print(f"Erro nível 2: ({e})")
            logs.erro(f"Falha ao buscar as prourações: {e}")
            return False

    except FileNotFoundError:
        print("Este endereço não existe.")
        logs.erro(f"Erro: {FileNotFoundError}")
        return False
    except ConnectionError:
        print("Sem acesso a internet ou o site está fora do ar.")
        logs.erro(f"Erro: {ConnectionError}")
        return False
    except Exception as e:
        print(f"Erro nível 1: ({e})")
        logs.erro(f"Erro: {e}")
        return False
    
"""Def para ler as procurações"""
def readProcurations(driver, line, situacao):
    env_list = []
    helper = SeleniumHelper(driver)

    # Iterando sobre as colunas de cada linha
    for column in range(1, 6):
        # Esse será o método para capturar o CNPJ e Razão Social
        if column in (1, 2):
            try:
                # Definindo o Xpath de acordo com as variáveis
                env_list.append(helper.texto_elemento(By.XPATH, f"/html/body/div/div[2]/form/table[2]/tbody/tr[{line}]/td[{column}]/font"))
            except ConnectionResetError:
                print("Conexão com o servidor resetada, reiniciar processo.")
                logs.erro(f"Falha na conexão ao ler Cnpj ou Razão Social: {ConnectionResetError}")
            except Exception as e:
                if column == 1:
                    print(f"Erro ao capturar o valor do CNPJ: ({e})")
                if column == 2:
                    print(f"Erro ao capturar o valor da Razão Social: ({e})")
                logs.info(f"Houve algum erro ao tentar encontrar o elemento de leitura do CNPJ ou da Razão Social. {e}")

        # Esse será o método para capturar a data final da vigência
        if column == 3:
            try:
                value = helper.texto_elemento(By.XPATH, f"/html/body/div/div[2]/form/table[2]/tbody/tr[{line}]/td[3]/font")
                # Tratando o value para pegar apenas a data de vigência final
                if value:
                    final_date = value[13:23]
                    inicial_date = value[:10]
                    env_list.append(inicial_date)
                    env_list.append(final_date)
            except ConnectionResetError:
                print("Conexão com o servidor resetada, reiniciar processo.")
                logs.erro(f"Falha na conexão ao ler vigencias: {ConnectionResetError}")
            except Exception as e:
                logs.info(f"Erro ao capturar o valor da Vigência: ({e})")
                print(f"Erro ao capturar o valor da Vigência: ({e})")
        
        #Esse será o método para capturar os itens dos serviços disponíveis na procuração
        if column == 4:
            try:
                # Exibindo os detalhes
                helper.clicar_elemento(By.XPATH, f"/html/body/div/div[2]/form/table[2]/tbody/tr[{line}]/td[4]/div[1]/label")

                try:
                    # Contando quantos itens temos na procuração
                    li_elements = helper.contar_elementos(By.XPATH, f"/html/body/div/div[2]/form/table[2]/tbody/tr[{line}]/td[4]/div[2]/font", By.TAG_NAME, "li")
                    quant_servicos = len(li_elements)

                    env_serv = []
                    
                    # Verificando quantos servicos tem em cada procuração para modificar a logica
                    if quant_servicos > 1:
                        # Iterando sobre os serviços
                        try:
                            for serv in range(1, quant_servicos + 1):
                                env_serv.append(helper.texto_elemento(By.XPATH, f"/html/body/div/div[2]/form/table[2]/tbody/tr[{line}]/td[4]/div[2]/font/li[{serv}]"))

                        except NoSuchElementException:
                            print(f"Não foi possível encontrar o XPATH: (/html/body/div/div[2]/form/table[2]/tbody/tr[{line}]/td[4]/div[2]/font/li[{serv}]")
                            logs.erro(f"Não foi possível encontrar o elemento: (/html/body/div/div[2]/form/table[2]/tbody/tr[{line}]/td[4]/div[2]/font/li[{serv}]")
                        except Exception as e:
                            print(f"Erro ao capturar o valor do serviço: ({e})")
                            logs.erro(f"Erro ao capturar o valor do serviço: ({e})")

                    elif quant_servicos == 1:
                        env_serv.append(helper.texto_elemento(By.XPATH, f"/html/body/div/div[2]/form/table[2]/tbody/tr[{line}]/td[4]/div[2]/font/li"))

                    else:
                        print("Houve algum erro ao calcular a quantidade de servicos disponíveis na procuração.")
                        logs.info("Houve algum erro ao calcular a quantidade de serviços na procuração.")

                except NoSuchElementException:
                    print("Não achei o elemento 'font'")
                    logs.info(f"Não achei o elemento 'font': {NoSuchElementException}")
                except Exception as e:
                    print(f"Erro ao contar os elementos dentro dos servicos: ({e})")
                    logs.erro(f"Erro ao contar os elementos dentro dos serviços: ({e})")
            except ConnectionResetError:
                print("Conexão com o servidor resetada, reiniciar processo.")
                logs.erro(f"Conexão com o servidor resetada, tente novamente.")
            except Exception as e:
                print(f"Erro ao exibir os detalhes da procuração: ({e})")
                logs.erro(f"Erro ao exibir os detalhes dos serviços: ({e})")
            
            env_list.append(env_serv)
            logs.info(f"Lista de serviços lida com sucesso: ({env_list[1]})")

        # Esse será o método para capturar a situação
        if column == 5:
            dados_cancelamento = []
            if situacao == "Ativas":
                # Para quando a situação for "Ativa"
                try:
                    env_list.append(helper.texto_elemento(By.XPATH, f"/html/body/div/div[2]/form/table[2]/tbody/tr[{line}]/td[5]/font"))
                except TimeoutException:
                    print("Demorou muito pra clicar no botão.")
                    logs.info(f"Não foi possível ler a situação da procuração. Operação das Ativas.")

            if situacao == "Canceladas":
                # Para quando a situação for "Cancelada"
                try:
                    print("Procuração Cancelada.")
                    helper.clicar_elemento(By.XPATH, f"/html/body/div/div[2]/form/table[2]/tbody/tr[{line}]/td[5]/div[1]/label")

                    try:
                        detalhes = helper.contar_elementos(By.XPATH, f"/html/body/div/div[2]/form/table[2]/tbody/tr[{line}]/td[5]/div[2]/font", By.TAG_NAME, "li")
                        quant_cancel = len(detalhes)
        
                        try:
                            # Iterando sobre as linhas dos detalhes
                            for linha in range(1, quant_cancel + 1):
                                dados_cancelamento.append(helper.texto_elemento(By.XPATH, f"/html/body/div/div[2]/form/table[2]/tbody/tr[{line}]/td[5]/div[2]/font/li[{linha}]"))
                            env_list.append(dados_cancelamento)
                        except Exception as e:
                            print(f"Erro ao capturar os detalhes do cancelamento: ({e})")
                            logs.erro(f"Erro ao caputurar os detalhes do cancelamento: ({e})")
                    except Exception as e:
                        print(f"Erro ao calcular os detalhes da procuração: ({e})")
                        logs.erro(f"Erro ao caputurar os detalhes da procuração: ({e})")
                except ConnectionResetError:
                    print("Conexão com o servidor resetada, reiniciar processo.")
                    logs.erro(f"Caímos no ConnectionResetError ao ler os detalhes do cancelamento")
                except Exception as e:
                    print(f"Erro ao exibir detalhes do cancelamento da procuração: ({e})")
                    logs.erro(f"Erro ao exibir detalhes do cancelamento da procuração: ({e})")

    # retornando a lista com as informações
    logs.info(f"Procuração lida com sucesso.")
    return env_list

"""Def para contar as páginas disponíveis"""
def count_pages(driver):
    helper = SeleniumHelper(driver)
    # Tentando contar quantas páginas temos disponíveis
    try:
        inputs = helper.contar_elementos(By.XPATH, f"/html/body/div/div[2]/form/table[3]/tbody/tr[1]/td", By.TAG_NAME, "input")
        quant_pages = len(inputs)
        print(f"Achei {quant_pages} páginas de procurações.")
        logs.info(f"Achei {quant_pages} páginas de procurações.")
        return quant_pages
    except NoSuchElementException:
        print(f"Erro: não foi possível encontrar o xpath (/html/body/div/div[2]/form/table[3]/tbody/tr[1]/td")
        logs.erro(f"Erro: não foi possível encontrar o xpath (/html/body/div/div[2]/form/table[3]/tbody/tr[1]/td)")
    except Exception as e:
        print(f"Houve um erro ao contar quantas páginas temos disponíveis: ({e})")
        logs.erro(f"Houve um erro ao contar quantas páginas temos disponíveis: ({e})")

"""Def para criar o caminho do output"""
def arquive(env_list, path):
    serie_id = uuid.uuid4()
    serie_id = f"{serie_id}"
    serie_id = serie_id.replace("-", "_")
    # Criando o caminho do output
    format_cnpj = env_list[0].replace(".", "").replace("/", "").replace("-", "")
    now = datetime.now()
    formatNow = now.strftime('%Y%m%d_%H%M')
    format_name = f"{format_cnpj}_{formatNow}_{serie_id}.xml"
    caminho = os.path.join(path, format_name)
    return caminho

"""Def para trocar de página"""
def trocar_pag(driver, pag):
    helper = SeleniumHelper(driver)
    try:
        helper.clicar_elemento(By.XPATH, f"/html/body/div/div[2]/form/table[3]/tbody/tr[1]/td/input[{pag}]")
        return True
    except Exception as e:
        print(f"Houve um erro ao trocar de página: '{e}'")
        logs.erro(f"Houve um erro ao trocar de página: '{e}'")

"""Def para formatar os dados para o Post"""
def formatar(env_list):

    #CNPJ
    cnpj = env_list[0].replace(".", "").replace("/", "").replace("-", "")
    
    #Vigencia Inicial
    date_obj = datetime.strptime(env_list[2], '%d/%m/%Y')
    VigenciaInicial = date_obj.strftime('%Y-%m-%dT00:00:00.123Z')

    #Vigencia Final
    date_obj = datetime.strptime(env_list[3], '%d/%m/%Y')
    VigenciaFinal = date_obj.strftime('%Y-%m-%dT00:00:00.123Z')

    #Servicos
    poderes = [i.lstrip('-') for i in env_list[4]]

    #Cancelado
    if env_list[5] == "Ativa":

        env_post = {
        "cnpj": cnpj,
        "vigenciaInicio": VigenciaInicial,
        "vigenciaFim": VigenciaFinal,
        "poderes": poderes,
        "cancelado": False
        }

        return env_post

    else:
        #cpfResponsavel
        cpf = env_list[5][0]
        formatCPF = cpf.split(':', 1)[1].strip()
        cpfResponsavel = formatCPF.replace('.', '').replace('-', '')

        #dataCancelamento
        Data = env_list[5][1].split(':', 1)[1].strip()
        formatData = datetime.strptime(Data, '%d/%m/%Y')
        dataCancelamento = formatData.strftime('%Y-%m-%dT00:00:00.123Z')

        env_post = {
        "cnpj": cnpj,
        "vigenciaInicio": VigenciaInicial,
        "vigenciaFim": VigenciaFinal,
        "poderes": poderes,
        "cancelado": True,
        "cpfResponsavel": cpfResponsavel,
        "dataCancelamento": dataCancelamento
        }

        return env_post

"""Def Post Endpoint"""
def PostEndPoint(env_post, token):
    if env_post['cancelado'] == False:
        jsonPost = {
        "cnpjCpf": env_post['cnpj'],
        "vigenciaInicio": env_post['vigenciaInicio'],
        "vigenciaFim": env_post['vigenciaFim'],
        "poderes": env_post['poderes'],
        "cancelado": env_post['cancelado']
        }
    else:
        jsonPost = {
        "cnpjCpf": env_post['cnpj'],
        "vigenciaInicio": env_post['vigenciaInicio'],
        "vigenciaFim": env_post['vigenciaFim'],
        "poderes": env_post['poderes'],
        "cancelado": env_post['cancelado'],
        "cpfResponsavel": env_post['cpfResponsavel'],
        "dataCancelamento": env_post['dataCancelamento']
        }

    headers = {
        'accept': '*/*',
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"    
    }

    response = requests.post("https://padroestabela-api-fiscoplan.azurewebsites.net/api/v1/Procuracao", headers=headers, json=jsonPost)

    logs.info("Starting request...")

    return response

"""Def para capturar o token de acesso"""
def accessToken():

    try:
        url = 'https://autenticador-fiscoplan.azurewebsites.net/api/v1/identidade/login'

        body = {
            "email": "victor.gomes@grupofiscoplan.com.br",
            "password": "Victor072013$",
            "sistemaId": "67F2EE26-6160-4A19-7595-08DBC9B8A8E9"
        }

        headers = {
            'accept': 'text/plain',
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, json=body)
        logs.info("Starting request access token...")

        if response.status_code == 200:
            listResponse = response.json()

            if listResponse:
                token = listResponse["accessToken"]
                return token
            else:
                print("Obtivemos um erro ao tentar obter o Token de autenticação.")
                logs.erro("Obtivemos um erro ao tentar obter o Token de autenticação.")
                return False
        else:
            print(f"Request negada: {response.status_code} - {response.text}")
            logs.erro(f"Request negada: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"Houve um erro ao obter o token de acesso: {e}")
        logs.erro(f"Houve um erro ao obter o token de acesso: {e}")

"""Def para fazer o login com o perfil do procurador"""
def perfil_procurador(driver, cnpj):
    helper = SeleniumHelper(driver)

    try:
        helper.clicar_elemento(By.ID, 'btnPerfil')

        helper.insert_keys_elemento(By.ID, 'txtNIPapel2', keys=cnpj)

        helper.clicar_elemento(By.XPATH, '/html/body/div[11]/div[2]/div[3]/form[2]/input[4]') #/html/body/div[11]/div[2]/div[3]/form[2]/input[4]
        sleep(3)

        try:
            msg_erro = helper.texto_elemento(By.XPATH, '/html/body/div[11]/div[2]/div[1]/p')

            print(f"Erro ao realizar o login: {msg_erro}")
            logs.erro(f"Erro ao realizar o login no perfil do procurador: {msg_erro}")
            return False
        
        except:
            try:
                procurador = helper.texto_elemento(By.XPATH, "/html/body/div[2]/div[1]/div[2]/span")
                print(procurador)
                logging.info(procurador)
                return True

            except Exception as e:
                print(f"Erro ao realizar o login no perfil do procurador. {e}")
                logs.info(f"Erro ao realizar o login no perfil do procurador. {e}")
                return False

    except Exception as e:
        print(f"Houve um erro ao trocar de perfil: ({e})")
        logs.info(f"Houve um erro ao trocar de perfil: ({e})")
        return False
    
"""Def para passar do checkbox do Captcha"""
def captcha(driver):
    helper = SeleniumHelper(driver)
   # Alternar para o iframe que contém o hCaptcha
    helper.mover_para(By.CSS_SELECTOR, "iframe[title*='Widget contendo caixa de seleção']", driver=driver)

    # Tentar localizar o checkbox dentro do iframe
    try:
        helper.clicar_elemento(By.ID, "checkbox")
        print("Checkbox clicado com sucesso.")

        # Voltar ao contexto principal
        driver.switch_to.default_content()
        sleep(3)

        # Clicando no botão de prosseguir
        try:
            helper.clicar_elemento(By.ID, 'ctl00_cphConteudo_btnProsseguir')

            # Verificando se apareceu alguma mensagem de erro
            try:
                sleep(3)
                error = driver.find_element(By.ID, 'ctl00_cphConteudo_PnlMensagem_painelMensagem') #ctl00_cphConteudo_PnlMensagem_lblMensagem
                print(f"{error.text}")
                logging.info(f"{error.text}")
                return False
            except NoSuchElementException:
                print("Não achei nenhuma mensagem de erro de Captcha. Continuando o processo...")
                logs.info("Não achei nenhuma mensagem de erro de Captcha. Continuando o processo...")
                return True
            except Exception as e:
                print(f"Houve um erro ao passar pelo Captcha: {e}")
                logs.erro(f"Houve um erro ao passar pelo Captcha: {e}")
                return False
        
        except Exception as e:
            print(f"Não foi possível localizar ou clicar no botão de prosseguir: {e}")
            logs.erro(f"Não foi possível localizar ou clicar no botão de prosseguir: {e}")
            return False
    except Exception as e:
        print(f"Não foi possível localizar ou clicar no checkbox: {e}")
        logs.erro(f"Não foi possível localizar ou clicar no checkbox: {e}")
        return False

"""Def para gerar a lista dos Períodos de Apuração"""
def ApurList():
    try:
        now = datetime.now()
        envList = []
        PerApur = []
        # formatando a data
        fData = now - relativedelta(years=5, months=1)
        fData = fData.replace(day=1)
        fData_fim = fData.replace(month=12).replace(day=31)

        # Adicionando as datas as listas
        envList.append(fData.strftime('%d/%m/%Y'))
        envList.append(fData_fim.strftime('%d/%m/%Y'))

        PerApur.append(envList)

        # Criando o laço para montar a lista completa
        now = datetime.now()
        while fData_fim < now:
            date = fData + relativedelta(years=1)
            fData = date.replace(month=1).replace(day=1)
            fData_fim = date.replace(month=12).replace(day=31)

            if fData_fim > now:
                fData_fim = now
            envList = []
            envList.append(fData.strftime('%d/%m/%Y'))
            envList.append(fData_fim.strftime('%d/%m/%Y'))
            PerApur.append(envList)

        logs.info(PerApur)
        return PerApur

    except Exception as e:
        print(f"Houve um erro ao tentar montar a lista dos períodos de Apuração: {e}")
        logs.erro(f"Houve um erro ao tentar montar a lista dos períodos de Apuração: {e}")

"""Def para pesquisar as DCTFWeb"""
def search_dctfweb(driver, ano, attempt):
    helper = SeleniumHelper(driver)

    # Preenchendo os campos de datas
    try:
        helper.clear_keys_elemento(By.ID, 'txtDataInicio')
        helper.insert_keys_elemento(By.ID, 'txtDataInicio', ano[0])

        helper.clear_keys_elemento(By.ID, 'txtDataFinal')
        helper.insert_keys_elemento(By.ID, 'txtDataFinal', ano[1])

        try: # Limpando os campos de datas de transmissão
            helper.clear_keys_elemento(By.ID, 'txtDataTransmissaoInicial')

            helper.clear_keys_elemento(By.ID, 'txtDataTransmissaoFinal')

            helper.clicar_elemento(By.ID, "ctl00_lblVersaoAplicacao")

            # Verificando se é a primeira vez do código
            if attempt:
                try: # Tentando acessar o select de tipo DCTFWeb
                    dropdown_element = helper.esperar_presenca_elemento(By.ID, 'ctl00_cphConteudo_ddlCategoriaDeclaracao')
                    select = Select(dropdown_element)

                    select.deselect_all()
                    sleep(1)
                    select.select_by_index(4)

                    try: # Tentando acessar o select de situacao DCTFWeb
                        dropdown_element = helper.esperar_presenca_elemento(By.ID, 'ctl00_cphConteudo_ddlSituacaoDeclaracao')
                        select = Select(dropdown_element)

                        select.deselect_all()
                        sleep(1)
                        select.select_by_visible_text("Ativa")
                        sleep(1)

                        try:
                            helper.clicar_elemento(By.ID, 'ctl00_cphConteudo_btnFiltar')
                            return True
                        
                        except Exception as e:
                            print(f"Houve um erro ao clicar no botão de filtrar: {e}")
                            logs.erro(f"Houve um erro ao clicar no botão de filtrar: {e}")
                            return False                           

                    except Exception as e:
                        print(f"Houve um erro ao parametrizar o campo de situação da DCTFWeb: {e}")
                        logs.erro(f"Houve um erro ao parametrizar o campo de situação da DCTFWeb: {e}")
                        return False
            
                except Exception as e:
                    print(f"Houve um erro parametrizar o campo do tipo da DCTF: {e}")
                    logs.erro(f"Houve um erro parametrizar o campo do tipo da DCTF: {e}")
                    return False
            else:
                # attempt == False -> não é a primeira vez que estamos pesquisando as DCTFs, não precisamos colocar todos os filtros novamente
                try:
                    helper.clicar_elemento(By.ID, 'ctl00_cphConteudo_btnFiltar')
                    return True
                        
                except Exception as e:
                    print(f"Houve um erro ao clicar no botão de filtrar: {e}")
                    logs.erro(f"Houve um erro ao clicar no botão de filtrar: {e}")
                    return False      

        except Exception as e:
            print(f"Houve um erro ao limpar os campos de data de transmissão: {e}")
            logs.erro(f"Houve um erro ao limpar os campos de data de transmissão: {e}")
            return False
    
    except Exception as e:
        print(f"Houve um erro ao enviar as datas do período de apuração: {e}")
        logs.erro(f"Houve um erro ao enviar as datas do período de apuração: {e}")
        return False
    
"""Def para verificar se a pesquisa retornou resultado"""
def verify_search(driver):
    helper = SeleniumHelper(driver)

    try:
        message = helper.texto_elemento(By.CSS_SELECTOR, 'div.alert.alert-info')
        return message
    
    except TimeoutException:
        try:
            situacao = helper.texto_elemento(By.ID, 'ctl00_cphConteudo_tabelaListagemDctf_GridViewDctfs_ctl02_lblSituacao')
            print(f"Aparentemente deu certo sim. {situacao}")
            return situacao
        
        except Exception as e:
            print(f"Não foi possível verificar se a pesquisa deu certo: {e}")
            logs.erro(f"Não foi possível verificar se a pesquisa deu certo: {e}")
            return f"False"
        
    except Exception as e:
        print(f"Algo deu errado na verificação da pesquisa: {e}")
        logs.erro(f"Algo deu errado na verificação da pesquisa: {e}")

"""Def para baixar os arquivos"""
def download_DCTFWeb(driver, i):
    helper = SeleniumHelper(driver)

    if i <= 9:
        id = f"ctl00_cphConteudo_tabelaListagemDctf_GridViewDctfs_ctl0{i}_lbkVisualizarDctf"

    else:
        id = f"ctl00_cphConteudo_tabelaListagemDctf_GridViewDctfs_ctl{i}_lbkVisualizarDctf"

    try:
        helper.clicar_elemento(By.ID, id)

        try:
            menu_element = helper.esperar_presenca_elemento(By.ID, "dropDown_Relatorios")
            actions = ActionChains(driver)
            actions.move_to_element(menu_element).perform()

            helper.clicar_elemento(By.XPATH, '/html/body/form/div[4]/div/ul/li[3]/ul/li[3]/a')
            sleep(1)
            driver.back()
            return True

        except Exception as e:
            print(f"Houve um erro ao interagir com o menu Pai: {e}")
            logs.erro(f"Houve um erro ao interagir com o menu Pai: {e}")
            return False
            
    except NoSuchElementException:
        print("Não achei esse XPATH, provavél que já esteja fora do intervalo do resultado.")
        logs.info("Não achei esse XPATH, provavél que já esteja fora do intervalo do resultado.")
        return False
    
    except TimeoutException:
        print("Elemento não encontrado, passando para a próxima linha...")
        logs.info("Elemento não encontrado, passando para a próxima linha...")
        return False
    
    except Exception as e:
        print(f"Houve algum erro ao clicar no botão de visualizar: {e}")
        logs.erro(f"Houve algum erro ao clicar no botão de visualizar: {e}")
        return False
    
"""Def para pesquisar os Darfs"""
def search_darf(driver, data_inicial, data_final):
    helper = SeleniumHelper(driver)
    try:
        helper.clear_keys_elemento(By.ID, 'campoDataArrecadacaoInicial')
        helper.insert_keys_elemento(By.ID, 'campoDataArrecadacaoInicial', data_final)

        helper.clear_keys_elemento(By.ID, 'campoDataArrecadacaoFinal')
        helper.insert_keys_elemento(By.ID, 'campoDataArrecadacaoFinal', data_final)

        # Continuando para a próxima página
        try:
            helper.clicar_elemento(By.XPATH, '/html/body/div[7]/form/div[5]/p/input')
            logs.info(f"Pesquisando Darfs de {data_inicial} a {data_final}")
            print(f"Pesquisando Darfs de {data_inicial} a {data_final}")
            return True

        except Exception as e:
            logs.erro(f"Não foi possível clicar no botão de continuar na pesquisa do DARF: ({e})")
            return False
    except Exception as e:
        logs.erro(f"Não foi possível acessar os campos de input de data na pesquisa do DARF: ({e})")
        return False
    
"""Def para imprimir a página"""
def print_page(driver):
    try:
        driver.execute_script('window.print()')
    except Exception as e:
        logs.erro(f"Erro ao tentar imprimir a página: {e}")

# """Def para ativar a janela do windows"""
# def window_activate():
#     chrome_windows = gw.getWindowsWithTitle('Sem título - Google Chrome')

#     if chrome_windows:
#         chrome_windows[0].activate()
#         sleep(1)
#     else:
#         logs.erro("Nenhuma janela do Chrome foi encontrada.")

"""Def para montar a lista com os meses"""
def lista_meses():
    months_list = []

    now = datetime.now()

    old_init = (now - relativedelta(years=5, months=2)).replace(day=1)
    ultimo_dia = monthrange(old_init.year, old_init.month)[1]
    old_final = old_init.replace(day=ultimo_dia)
    
    while old_final < now:
        env_list = []
        
        env_list.append(old_init.strftime('%d/%m/%Y'))
        env_list.append(old_final.strftime('%d/%m/%Y'))
        months_list.append(env_list)

        # Incrementa um mês nas datas
        old_init += relativedelta(months=1)
        ultimo_dia = monthrange(old_init.year, old_init.month)[1]
        old_final = old_init.replace(day=ultimo_dia)

        if old_final >= now:
            env_list = [old_init.strftime('%d/%m/%Y'), old_final.strftime('%d/%m/%Y')]
            months_list.append(env_list)
            break
    
    return months_list

"""Def para o pop up da avaliação da receita"""
def popUpAvaliacao(driver):
    helper = SeleniumHelper(driver)
    try: # Testando o alerta da avaliação da receita
        alert = driver.switch_to.alert
        alert_text = alert.text
        print(f"Texto do alerta: {alert_text}")
        alert.dismiss()

        helper.clicar_elemento(By.NAME, 'BtnRetornar')
        return True

    except NoAlertPresentException: 
        helper.clicar_elemento(By.NAME, 'BtnRetornar')
        return False
    
    except Exception as e:
        logs.erro(f"Houve um erro ao tratar o alerta da avaliação da receita na pesquisa do DARF: {e}")
        return False
    
"""Def para contar as linhas na busca"""
def CountLines(driver):
    helper = SeleniumHelper(driver)
    try:
        # Procurando a tabela
        tbody = helper.contar_elementos(By.XPATH, '/html/body/div/form/div[3]/table/tbody/tr/td/div/table/tbody', By.TAG_NAME, "tr")
        return len(tbody)
    
    except Exception as e:
        logs.erro(f"Houve um erro ao obter a quantidade de linhas da página de resultado: {e}")

"""Def para retornar a lista com os códigos disponíveis"""
def codigosList(driver, quantLines):
    helper = SeleniumHelper(driver)
    try:
        AllCods = []
        # Iterando sobre as linhas para capturar o código dos pagamentos
        for i in range(2, quantLines+1):
            codReceita = helper.texto_elemento(By.XPATH, f'/html/body/div/form/div[3]/table/tbody/tr/td/div/table/tbody/tr[{i}]/td[9]')
            AllCods.append(codReceita)
    except Exception as e:
        logs.erro(f"Houve um erro ao capturar os códigos disponíveis no resultado da pesquisa: {e}")
    
    if AllCods:
        # Retirando os códigos repetidos
        ListaDosCodigos = list(set(AllCods))
        logs.info("Códigos de receita de DARF lidos com sucesso!")
        return ListaDosCodigos
    
"""Def para passar da avaliação da receita"""
def attempt(driver, varAttempt, path):
    helper = SeleniumHelper(driver)
    # Passando pelo popup de avaliação da receita
    if varAttempt == True:
        helper.clicar_elemento(By.ID, 'CheckBoxTodos')
        sleep(1)
        helper.clicar_elemento(By.ID, 'BtnImprimirConprovante')
        sleep(2)
        hotkey('alt', 'f4')
        sleep(1)
        helper.clicar_elemento(By.ID, 'BtnRetornar')
        sleep(2)
        if popUpAvaliacao(driver):
            print("Alerta de avaliação. Passamos...")
            logs.info("Alerta de avaliação. Passamos...")
            varAttempt =  False
            # Excluindo esse arquivo que acabamos de baixar
            try:
                arquivos = os.listdir(path)
                if len(arquivos) == 1:
                    caminho_arquivo = os.path.join(path, arquivos[0])
                    os.remove(caminho_arquivo)
            except Exception as e:
                print(f"Houve um erro excluir o arquivo de teste. {e}")
                logs.info(f"Houve um erro excluir o arquivo de teste do DARF {e}")

            return varAttempt
        else:
            logs.erro("Deu erro ao tentar passar pelo popup de avaliação da receita...")
            return False

"""Def para selecionar os pagamentos referentes ao código e baixar"""
def download_pdf(driver, code, quantLines):
    helper = SeleniumHelper(driver)
    try:
        # Iterando sobre as linhas novamente
        for i in range(2, quantLines + 1):
            validador = False
            codReceita = helper.texto_elemento(By.XPATH, f'/html/body/div/form/div[3]/table/tbody/tr/td/div/table/tbody/tr[{i}]/td[9]')
            if codReceita == code:
                helper.clicar_elemento(By.XPATH, f"/html/body/div/form/div[3]/table/tbody/tr/td/div/table/tbody/tr[{i}]/td[1]/input")
                sleep(5)
            validador = True
    except Exception as e:
        logs.erro(f"Houve um erro ao verificar os códigos de Receita de cada linha: {e}")

    if validador:
        try:
            # Chamando o pdf
            helper.clicar_elemento(By.ID, 'BtnImprimirConprovante')
            sleep(1)
        except Exception as e:
            logs.erro(f"Houve um erro nesse teste de obter o DARF: {e}")
        
        # Imprimindo o pdf
        try:
            janelas = driver.window_handles
            driver.switch_to.window(janelas[1])

            sleep(2)

            hotkey('alt', 'f4')
            driver.switch_to.window(janelas[0])

            # Desmarcando todos os checkbox 
            helper.clicar_elemento(By.ID, 'CheckBoxTodos')
            sleep(1)
            helper.clicar_elemento(By.ID, 'CheckBoxTodos')
            sleep(2)
            return True

        except Exception as e:
            logs.erro(f"Houve um erro ao imprimir os comprovantes DARF: {e}")
            return False
    return False

"""Def para renomear os arquivos"""
def rename_file_darf(code, comp, path):
    try:
        mes = datetime.strptime(comp, '%d/%m/%Y')

        # montando o nome do arquivo
        arquivo = f"{code}_{mes.strftime('%m-%Y')}.pdf"
        
        arquivos = [os.path.join(path, arquive) for arquive in os.listdir(path) if os.path.isfile(os.path.join(path, arquive))]
        lastArquive = max(arquivos, key=os.path.getmtime)

        newWalk = os.path.join(path, arquivo)

        os.rename(lastArquive, newWalk)
    except Exception as e:
        logs.erro(f"Houve um erro ao renomear o arquivo DARF: {e}")

"""Def para renomear o nome do arquivo"""
def rename_file_dctf(path, data):
    data = datetime.strptime(data, '%d/%m/%Y')
    month = data.strftime('%Y-%m')
    # pegando o último arquivo da pasta
    date_pattern = re.compile(r"\d{4}-\d{2}")
    filename = max([os.path.join(path, f) for f in os.listdir(path) if not date_pattern.match(f)], key=os.path.getctime)

    new_name = os.path.join(path, f"{month}.pdf")

    try:
        os.rename(filename, new_name)
        return True

    except Exception as e:
        print(f"Houve algum erro ao renomear o arquivo: ({e})")
        logging.info(f"Houve algum erro ao renomear o arquivo: ({e})")

"""Def para contar quantas linhas temos na tabela"""
def quantLines(driver):
    helper = SeleniumHelper(driver)
    # Contando os elementos na página html
    try:
        all_tr = helper.contar_elementos(By.XPATH, '/html/body/div/div[2]/div/form/table/tbody', By.TAG_NAME, "tr")
        quant_tr = len(all_tr)
        return quant_tr
    except Exception as e:
        logs.erro(f"Houve um erro ao contar as linhas da página da DCTF: {e}")

"""Def para imprimir a página"""
def print_page(driver):
    try:
        driver.execute_script('window.print()')
    except Exception as e:
        logs.erro(f"Erro ao tentar imprimir a página da DCTF: {e}")

# """Def para ativar a janela do windows"""
# def window_activate():
#     chrome_windows = gw.getWindowsWithTitle('Impressão da Declaração - 2004 ')

#     if chrome_windows:
#         chrome_windows[0].activate()
#         sleep(1)
#     else:
#         logs.erro("Nenhuma janela do Chrome foi encontrada.")

"""Def para pegar a data da DCTF e renomear o arquivo"""
def get_date(driver, tr):
    helper = SeleniumHelper(driver)
    # Pegando a data
    try:
        dataInicial = helper.texto_elemento(By.XPATH, f"/html/body/div/div[2]/div/form/table/tbody/tr[{tr}]/td[4]")
        return dataInicial
    except Exception as e:
        logs.erro(f"Não consegui encontrar o periodo inicial para renomear o arquivo: {e}")

"""Def para baixar as DCTF"""
def download_dctf(driver, tr, parametro_inicial, parametro_final):
    helper = SeleniumHelper(driver)
    # Pegando as informações necessárias
    try:
        dataInicial = helper.texto_elemento(By.XPATH, f"/html/body/div/div[2]/div/form/table/tbody/tr[{tr}]/td[4]")
        situacao = helper.texto_elemento(By.XPATH, f"/html/body/div/div[2]/div/form/table/tbody/tr[{tr}]/td[7]")
        try:
            # tratando a dataInicial para verificar condicao
            if dataInicial:
                data_formatada = datetime.strptime(dataInicial, '%d/%m/%Y')
                format_parametro_inicial = datetime.strptime(parametro_inicial, '%d/%m/%Y')
                format_parametro_final = datetime.strptime(parametro_final, '%d/%m/%Y')
                if format_parametro_inicial <= data_formatada <= format_parametro_final:
                    if situacao in ('Original/ Ativa', 'Retificadora/ Ativa'):
                        print(f"Declaração do período {dataInicial} está Ativa.")
                        logs.info(f"Declaração do período {dataInicial} está Ativa.")

                        helper.clicar_elemento(By.XPATH, f'/html/body/div/div[2]/div/form/table/tbody/tr[{tr}]/td[8]/input[2]')

                        # Tratando o alerta
                        try:
                            alert = driver.switch_to.alert
                            alert.accept()
                            sleep(2)

                            # Iniciando a baixa dos arquivos
                            try:
                                janelas = driver.window_handles
                                driver.switch_to.window(janelas[1])
                                sleep(1)
                                print_page(driver)

                                driver.close()

                                driver.switch_to.window(janelas[0])
                                sleep(1)
                                return True
                                
                            except Exception as e:
                                logs.erro(f"É pra sempre aparecer o alerta do tamanho da folha. Verificar o que aconteceu no mês {dataInicial}")
                                return False
                        except NoAlertPresentException:
                            logs.erro(f"É pra sempre aparecer o alerta do tamanho da folha. Verificar o que aconteceu no mês {dataInicial}")
                            return False
                        except UnexpectedAlertPresentException:
                            logs.erro(f"Alerta inexperado no mês {dataInicial} para a pesquisa das DCTF.")
                            return False
                        except Exception as e:
                            logs.erro(f"Houve algum erro ao lidar com o alerta no mês {dataInicial} para a pesquisa das DCTF.")
                            return False
                else:
                    print("Período de apuração menor que o intervalo parametrizado.")
                    logs.info("Período de apuração menor que o intervalo parametrizavel.")

            else:
                logs.erro("Data Inicial não encontrada.")
                return False
        except Exception as e:
            logs.erro(f"[DCTF] Houve algum erro nas verificações de condições: {e}")
            return False
    except Exception as e:
        logs.erro(f"[DCTF] Não consegui pegar as informações dos campos das tabelas. {e}")
        return False
    
def download_FontesPagadoras(driver, path, value):
    helper = SeleniumHelper(driver)

    try:
        helper.clicar_elemento(By.ID, "btnExecutar")

        try:
            helper.clicar_elemento(By.NAME, "bimg4")

            try:
                while any(arquivo.endswith(".crdownload") for arquivo in os.listdir(path)):
                    print("Aguardando o término do download....")
                print(f"Download realizado com sucesso: {value}")
                helper.clicar_elemento(By.ID, "btnVoltar")
                return True
            except Exception as e:
                print(f"Houve algum erro ao tentar ver se o download foi realizado: {e}")
                logs.erro(f"Houve algum erro ao tentar ver se o download foi realizado: {e}")
                return False
    
        except Exception as e:
            print("Não consegui localizar o botão de download.")
            try:
                mensage = helper.esperar_elemento_visivel(By.XPATH,"/html/body/div[2]/div[2]/table/tbody/tr[1]/td[2]/b")
                if mensage.text == "Até o momento, não há informações em Dirf aceita, processada, para o contribuinte.":
                    print(f"Para o ano {value} ainda não existe Fontes Pagadoras: ({mensage.text})")
                    logs.info(f"Para o ano {value} ainda não existe Fontes Pagadoras: ({mensage.text})")
                    helper.clicar_elemento(By.ID, "btnVoltar_msg")
                    return True
                else:
                    print(f"""Mensagem não tratada para a busca do período {value}:
                        {mensage.text}""")
                    logs.info(f"Mensagem não tratada para a busca do período {value}: {mensage.text}")
                    helper.clicar_elemento(By.ID, "btnVoltar_msg")
                    return False
            except Exception as e:
                print(f"Não consegui interagir com a mensagem: {e}")
                logs.erro(f"[FONTESPAGADORAS] - Não consegui interagir com a mensagem: {e}")
                helper.clicar_elemento(By.ID, 'btnVoltar_msg')
                sleep(5)
                return False
    except NoSuchElementException:
        print(f"Não consegui encontrar o botão de 'consultar'.")
        logs.erro("[FONTESPAGADORAS] - Não consegui encontrar o botão de 'consultar'.")
        return False
    except Exception as e:
        print(f"Não consegui interagir com o botão de 'continuar': {e}")
        logs.erro(f"[FONTESPAGADORAS] - Não consegui interagir com o botão de 'continuar': {e}")
        return False

def upload_arquivo(acces_token, download, dropbox_path):
    dbx = dropbox.Dropbox(acces_token)

    with open(download, "rb") as f:
        dbx.files_upload(f.read, dropbox_path, mode=dropbox.files.WriteMode("overwrite"))


def periodo(data_inicial, data_final):
    try:
        data_inicial = datetime.strptime(data_inicial, '%Y-%m-%d')
        data_final = datetime.strptime(data_final, "%Y-%m-%d")

        try:
            data_inicial = data_inicial.replace(day=1)

            periodos = []
            while data_inicial <= data_final:
                ptemp = []
                ptemp.append(data_inicial.strftime('%d/%m/%Y'))

                ultimo_dia = monthrange(data_inicial.year, data_inicial.month)[1]
                temp_data_final = data_inicial.replace(day=ultimo_dia)
                ptemp.append(temp_data_final.strftime('%d/%m/%Y'))
                periodos.append(ptemp)

                data_inicial += relativedelta(months=1)
            
            return periodos

        except Exception as e:
            logs.erro(f"Houve um erro ao montar a lista dos periodos: {e}")

    except Exception as e:
        logs.erro(f"Houve um erro ao formatar as datas: {e}")

def anos_periodo(periodos):
    try:
        anos = []
        for periodo in periodos:
            ano = periodo[0].split('/')[2]
            print(ano)
            if ano not in anos:
                anos.append(ano)
        return anos

    except Exception as e:
        logs.erro(f"Houve um erro ao montar a lista dos anos: {e}")
