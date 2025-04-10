from biblioteca import *
from certificateSelector import *

path = r"C:\Users\victor.gomes\Desktop\codigos\automacoes\FontesPagadoras"
cnpj = '09352161000119'

CertificateSelector(r"33242075000138.pfx", 'Fisco2024')

# iniciando uma instância no driver
driver = chrome_options_def(path)
helper = SeleniumHelper(driver)

if login(driver):
    print("Login realizado com sucesso!")

    if perfil_procurador(driver, cnpj):
        try:
            url = "https://cav.receita.fazenda.gov.br/Servicos/ATCTA/Rendimento/Rend/RendP000/RendP000.asp?Width=1536&Height=864&windowHeight=562"
            driver.get(url)

            try:
                select = Select(helper.esperar_elemento_clicavel(By.ID, "opcao_ano"))
                for option in select.options:
                    value = option.get_attribute('value')
                    if value:
                        try:
                            select.select_by_value(value)
                            if download_FontesPagadoras(driver, path, value):
                                continue
                            else:
                                print("Houve um erro ao relizar o download dos arquivos.")
                                logs.erro("[FONTESPAGADORAS] - Houve um erro ao realizar o download dos arquivos.")
                        except Exception as e:
                            print(f"Não foi possível selecionar a opção desejada: {e}")
                            logs.erro(f"[FONTESPAGADORAS]- Não foi possível selecionar a opção desejada: {e}")
                    else:
                        print("Não foi possível encontrar o valor do elemento select.")
                        logs.erro("[FONTESPAGADORAS] - Não foi possível encontrar o valor do elemento select.")
            except NoSuchElementException:
                print(f"Elemento não encontrado: {NoSuchElementException}")
                logs.erro(f"[FONTESPAGADORAS] - Não econtrei o elemento select de ano.")
            except Exception as e:
                print(f"Houve algum erro ao tentar interagir com o combo select de ano: {e}")
                logs.erro(f"[FONTESPAGADORAS] - Houve algum erro ao interagir o select de ano: {e}")
        except FileNotFoundError:
            print(f"O endereço {url} não existe: {FileNotFoundError}")
            logs.erro(f"O endereço {url} não existe: {FileNotFoundError}")
        except ConnectionError:
            print(f"Sem acesso a internet ou o site {url} está fora do ar: {ConnectionError}")
            logs.erro(f"Sem conexação com a internet ou o site {url} está fora do ar: {ConnectionError}")
        except Exception as e:
            print(f"Houve algum erro ao tentar ir para a página da Fontes Pagadoras: {e}")
            logs.erro(f"Houve algum erro ao tentar ir para a página da Fontes Pagadoras: {e}")
    else:
        print(f"Houve um erro ao realizar o login no perfil do Cnpj: {cnpj}")
        logs.erro(f"Houve um erro ao realizar o login no perfil do Cnpj: {cnpj}")
else:
    print("Houve um erro ao realizar o login no portal do e-cac.")
    logs.erro("Houve um erro ao realizar o login no portal do e-cac.")

# Limpando a pattern do certificado
pathOfstringValue = 'SOFTWARE\Policies\Google\Chrome\AutoSelectCertificateForUrls'
stringValueName = '1'
clearCertificate(stringValueName, 'limpo', pathOfstringValue)
logs.info(f"Pattern limpo com sucesso.")

if leave_safely(driver):
    driver.close()
    driver.quit()
else:
    print("Sai com segurança do e-cac.")
    logs.info("Script encerrado com sucesso.")