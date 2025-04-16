from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID
import winreg

def GetCertificate(certificado, senha):
    with open(certificado, "rb") as f:
      private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(f.read(), senha.encode())
    return certificate

def UpdateStringValue(strigValueName,newValueOfStrinValue, stringValuePath):
  key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, stringValuePath, 0, winreg.KEY_ALL_ACCESS)
  winreg.SetValueEx(key, strigValueName, 0, winreg.REG_SZ, newValueOfStrinValue)
  winreg.CloseKey(key)
  

def clearCertificate(strigValueName,newValueOfStrinValue, stringValuePath):  #Def pra limpar o certificado automático da máquina, usar para não travar outros de serem usados
  key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, stringValuePath, 0, winreg.KEY_ALL_ACCESS)
  winreg.SetValueEx(key, strigValueName, 0, winreg.REG_SZ, newValueOfStrinValue)
  winreg.CloseKey(key)

def CertificateSelector(certificado, senha): 
    pathOfstringValue = 'SOFTWARE\Policies\Google\Chrome\AutoSelectCertificateForUrls'
    stringValueName = '1'

    certificate = GetCertificate(certificado, senha)
    subject = certificate.subject
    issuer = certificate.issuer

    # Extrair o CN, C e O do issuer e do subject
    issuer_cn = issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    subject_cn = subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value

    # Você pode verificar se o C e O existem antes de acessá-los
    issuer_country = issuer.get_attributes_for_oid(NameOID.COUNTRY_NAME)[0].value if issuer.get_attributes_for_oid(NameOID.COUNTRY_NAME) else ""
    issuer_org = issuer.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value if issuer.get_attributes_for_oid(NameOID.ORGANIZATION_NAME) else ""

    subject_country = subject.get_attributes_for_oid(NameOID.COUNTRY_NAME)[0].value if subject.get_attributes_for_oid(NameOID.COUNTRY_NAME) else ""
    subject_org = subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value if subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME) else ""

    url_where_certificate_will_be_send = "https://certificado.sso.acesso.gov.br/login?client_id=login.esocial.gov.br"
    jjson = (
        '{"pattern":"' + url_where_certificate_will_be_send + '","filter":{"ISSUER":{"CN":"'
        + issuer_cn + '","C":"' + issuer_country + '","O":"' + issuer_org
        + '"},"SUBJECT":{"CN":"' + subject_cn + '","C":"' + subject_country
        + '","O":"' + subject_org + '"}}}'
    )
    
    UpdateStringValue(stringValueName, jjson, pathOfstringValue)

# def UpdateStringValue(cert_data, url_where_certificate_will_be_send):
#     json_path = os.path.join(os.getcwd(), 'auto_select_certificate.json')

#     # Crie o dicionário do JSON usando as variáveis
#     policy = {
#         "AutoSelectCertificateForUrls": [
#             {
#                 "pattern": url_where_certificate_will_be_send,
#                 "filter": {
#                     "ISSUER": {
#                         "CN": cert_data["issuer_cn"],
#                         "C": cert_data["issuer_country"],
#                         "O": cert_data["issuer_org"]
#                     },
#                     "SUBJECT": {
#                         "CN": cert_data["subject_cn"],
#                         "C": cert_data["subject_country"],
#                         "O": cert_data["subject_org"]
#                     }
#                 }
#             }
#         ]
#     }

#     # Salve o JSON no arquivo
#     with open('/etc/opt/chrome/policies/managed/auto_select_certificate.json', 'w') as file:
#         json.dump(policy, file, indent=4)

# def CertificateSelector(certificado, senha): 
#     certificate = GetCertificate(certificado, senha)
#     subject = certificate.subject
#     issuer = certificate.issuer

#     issuer_cn = issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
#     subject_cn = subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value

#     issuer_country = issuer.get_attributes_for_oid(NameOID.COUNTRY_NAME)[0].value if issuer.get_attributes_for_oid(NameOID.COUNTRY_NAME) else ""
#     issuer_org = issuer.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value if issuer.get_attributes_for_oid(NameOID.ORGANIZATION_NAME) else ""

#     subject_country = subject.get_attributes_for_oid(NameOID.COUNTRY_NAME)[0].value if subject.get_attributes_for_oid(NameOID.COUNTRY_NAME) else ""
#     subject_org = subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value if subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME) else ""

#     url_where_certificate_will_be_send = "https://certificado.sso.acesso.gov.br/login?client_id=login.esocial.gov.br"
    
#     UpdateStringValue({
#     "issuer_cn": issuer_cn,
#     "issuer_country": issuer_country,
#     "issuer_org": issuer_org,
#     "subject_cn": subject_cn,
#     "subject_country": subject_country,
#     "subject_org": subject_org
#     }, url_where_certificate_will_be_send)