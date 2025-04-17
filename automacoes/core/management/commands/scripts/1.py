from biblioteca import *
from certificateSelector import *
from pathlib import Path
import sys

def main(cnpj, ambiente, certificado, data_inicial, data_final):
    # Garantindo que esse path existe
    path = Path(fr"C:\Users\victor.gomes\Documents\projeto_automacoes\automacoes\arquivos\{ambiente}\{cnpj}")
    path.mkdir(parents=True, exist_ok=True)

    if certificado == 'true':
        print("Tem que implementar a lógica do certificado próprio da empresa.")

    elif certificado == 'false':
        certificado_path = r"C:\Users\victor.gomes\Documents\projeto_automacoes\automacoes\Fiscoplan - Fisco2011.pfx"
        senha = "Fisco2011"
    
    CertificateSelector(certificado_path, senha)

    # iniciando uma instância no driver
    driver = chrome_options_def(path)
    helper = SeleniumHelper(driver)
    
    periodos = periodo(data_inicial, data_final)

    if login(driver):
        print("Login realizado com sucesso!")

        if perfil_procurador(driver, cnpj):
            try:
                url = "https://cav.receita.fazenda.gov.br/Servicos/ATSDR/DECWEB/dadosdec.asp?Declaracao=DCTF"
                driver.get(url)

                try:
                    anos = Select(helper.esperar_elemento_clicavel(By.NAME, "cboExercicio"))
                    lista_anos = anos_periodo(periodos)
                    for option in anos.options:
                        value = option.get_attribute("value")
                        if value and (value in lista_anos):
                            anos.select_by_value(value)
                            try:
                                mes = Select(helper.esperar_elemento_clicavel(By.NAME, "periodo"))
                                for option in mes.options:
                                    value = option.get_attribute("value")
                                    if value:
                                        if not value.startswith("32"):
                                            mes.select_by_value(value)
                                            
                                            # clicando pra pesquisar com os selects selecionados
                                            helper.clicar_elemento(By.XPATH, "/html/body/font/center/form/div[1]/input[1]")

                                            texto = helper.texto_elemento(By.XPATH, "/html/body/font/center/div/table/tbody/tr/td/font")
                                            if texto and "Não consta DCTF" in texto:
                                                driver.refresh()
                                            else:
                                                helper.clicar_elemento(By.XPATH, "/html/body/font/center/form/div[3]/input")
                                                print("Download realizado com sucesso!")
                                                driver.refresh()
                                        else:
                                            print("Não baixamos declaração de semestre.")
                                    else:
                                        print("Não foi possível encontrar o valor do elemento select Mês.")
                            except NoSuchElementException as e:
                                print(f"Elemento não encontrado: {e}")
                            except Exception as e:
                                print(f"Houve algum erro ao tentar interagir com o combo select de mês: {e}")
                        else:
                            print("Não foi possível encontrar o valor do elemento select Ano.")
                except NoSuchElementException as e:
                    print(f"Elemento não encontrado: {e}")
                except Exception as e:
                    print(f"Houve algum erro ao tentar interagir com o combo select de ano: {e}")
            except FileNotFoundError:
                print(f"O endereço {url} não existe: {FileNotFoundError}")
            except ConnectionError:
                print(f"Sem acesso a internet ou o site {url} está fora do ar: {ConnectionError}")
            except Exception as e:
                print(f"Houve algum erro ao tentar ir para a página da Fontes Pagadoras: {e}")
        else:
            print("Não foi possível realizar o login no perfil do procurador.")
    else:
        print("Houve um erro ao realizar o login no e-cac.")


if __name__ == "__main__":
    # cnpj = sys.argv[1]
    # ambiente = sys.argv[2]
    # certificado = sys.argv[3]
    # data_inicial = sys.argv[4]
    # data_final = sys.argv[5]

    cnpj = "28121387000153"
    ambiente = "fiscoplan24.grupofiscoplan.com.br"
    certificado = "false"
    data_inicial = "2024-01-01"
    data_final = "2024-12-31"

    main(cnpj, ambiente, certificado, data_inicial, data_final)