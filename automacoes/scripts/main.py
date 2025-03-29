from fastapi import FastAPI, UploadFile, File, HTTPException, status, Form
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
import json
import uuid
import os

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Essa é a minha API."}

class Solicitacao(BaseModel):
    cnpj: str = Field(...,min_length=14, max_length=14)
    ambiente: str = Field(...)
    certificado: bool = Field(...)
    data_inicial: Optional[str] = Field(None, pattern=r"^\d{2}/\d{2}/\d{4}$")
    data_final: Optional[str] = Field(None, pattern=r"^\d{2}/\d{2}/\d{4}$")
    documento: int = Field(...)

    @validator("cnpj")
    def validar_cnpj(cls, value):
        if not value.isdigit():
            raise ValueError("CNPJ deve conter apenas números")
        return value

    @validator("data_inicial")
    def validar_data_inicial(cls, value):
        if value is None:
            return value
        try:
            datetime.strptime(value, "%d/%m/%Y")
        except ValueError:
            raise ValueError("Formato inválido! Use DD/MM/YYYY e verifique se a data existe.")
        return value
    
    @validator("data_final")
    def validar_data_final(cls, value):
        if value is None:
            return value
        try:
            datetime.strptime(value, "%d/%m/%Y")
        except ValueError:
            raise ValueError("Formato inválido! Use DD/MM/YYYY e verifique se a data existe.")
        return value

class Certificado(BaseModel):
    senha: str = Field(...)
    cnpj: str = Field(..., min_length=14, max_length=14)

    @classmethod
    def validar_cnpj(cls, value):
        if not value.isdigit():
            raise ValueError("CNPJ deve conter apenas números")
        return value

@app.post("/upload-certificado/")
async def upload_certificado(
    certificado: UploadFile = File(...),
    senha: str = Form(...),
    cnpj: str = Form(..., min_length=14, max_length=14)
):
    if not cnpj.isdigit():
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="CNPJ deve conter apenas números."
            )
    
    if not certificado.filename.lower().endswith('.pfx'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "Apenas arquivos .pfx são permitidos."
        )
    
    path_certificate = "/app/certificados"
    os.makedirs(path_certificate, exist_ok= True)
    arquivo_caminho = os.path.join(path_certificate, f"{cnpj}-{senha}.pfx")
    
    if os.path.exists(arquivo_caminho):
        return {"mensagem": "Certificado já existe, não será salvo novamente."}
    
    with open(arquivo_caminho, "wb") as f:
        f.write(await certificado.read())

    return {"mensagem": f"Certificado enviado com sucesso! Arquivo salvo em {arquivo_caminho}"}

@app.post("/solicitacao")
def make_request(solicitacao: Solicitacao):
    archive_name = f"/app/txts/pendentes/{uuid.uuid4()}.json"
    with open(archive_name, 'w', encoding='UTF-8') as archive:
        json.dump(solicitacao.dict(), archive, ensure_ascii=False, indent=4)
    return {"mensagem": "Solicitacao recebida com sucesso!", "Solicitacao": solicitacao}
