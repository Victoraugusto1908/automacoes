from lxml import etree
import logging
    
def bookeeping_xml(env_list, output):
    logging.basicConfig(filename= 'INFO.log', format = "%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO, encoding='UTF-8')

    # Criando elemento raiz
    root = etree.Element("procuracao")

    # Adicionando os subelementos
    cnpj = etree.SubElement(root, 'cnpj')
    cnpj.text = env_list[0]

    razao_social = etree.SubElement(root, 'razao_social')
    razao_social.text = env_list[1]

    vigencia = etree.SubElement(root, 'vigencia')
    inicial = etree.SubElement(vigencia, 'inicial')
    inicial.text = env_list[2]
    final = etree.SubElement(vigencia, 'final')
    final.text = env_list[3]

    # Criando a lógica para plotar os serviços
    servicos = etree.SubElement(root, 'servicos')
    services_list = env_list[4]

    for serv in services_list:
        li = etree.SubElement(servicos, 'li')
        li.text = serv

    # Criando a lógica para plotar a situacao
    if isinstance(env_list[5], list):
        situacao = etree.SubElement(root, 'situacao')
        situacao.text = "Cancelada"

        dados_cancelamento = env_list[5]
        dados = [item.split(": ")[1] for item in dados_cancelamento]

        cpf_responsavel = etree.SubElement(situacao, 'cpf_responsavel')
        cpf_responsavel.text = dados[0]

        data_cancelamento = etree.SubElement(situacao, 'data_cancelamento')
        data_cancelamento.text = dados[1]

        origem = etree.SubElement(situacao, 'origem')
        origem.text = dados[2]

    else:
        situacao = etree.SubElement(root, 'situacao')
        situacao.text = env_list[5]

    # Criar a árvore e salvar no arquivo XML
    tree = etree.ElementTree(root)
    tree.write(output, pretty_print=True, xml_declaration=True, encoding="UTF-8")
