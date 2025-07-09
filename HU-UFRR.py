from requests import get
import fitz
from bs4 import BeautifulSoup
from os import listdir, remove
import re
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe

## baixar os editais de convocação

for i in range(0,1001, 20):
  url = f"https://www.gov.br/ebserh/pt-br/acesso-a-informacao/agentes-publicos/concursos-e-selecoes/concursos/2024/convocacoes/hu-ufrr?b_start:int={i}"
  res = get(url)
  if res.status_code != 200:
    break
  html = BeautifulSoup(res.content, features="html.parser")
  if html.select(".discreet").__len__() > 0: ## não há conteudo no site se houver esta classe
    break
  els = html.select("[Title='File']")
  for el in els: 
    link = el["href"].replace("/view", "/@@download/file")
    download = get(link)
    if download.status_code == 200:
      with open(el.text, "wb") as f:
        f.write(download.content)
        print(f"{el.text} baixado com sucesso")
    else:
      print(f"Falha ao baixar {el.text}")

  print(f"Página start_int = {i} concluída")


##
print("segunda sessão do script")

all_files = listdir('.')

pdf_files = [f for f in all_files if f.endswith('.pdf')]

dados_estruturados = {
    "area": [],
    "cargo": [],
    "listagem": [],
    "colocacao": [],
    "nome": []
}

for pdf in pdf_files:
  text= ""
  with fitz.open(pdf) as doc:
    text=""
    for page in doc:
      text+=page.get_text()

    convocacoes = re.findall(r"1\.\d[\s\S]*?;", text, re.DOTALL)
    for convocacao in convocacoes:
      partes = convocacao.split(")")
      area, tmp, = partes if len(partes) == 2 else [partes[0], partes[1]] 
      cargo, listagem = re.sub(r"1\.[0-9] ", "", area).split("(")
      if " - " in cargo:
        partes = cargo.split(" - ")
        cargo_geral, cargo_especifico = partes if len(partes) == 2 else [partes[0], partes[2]]
        cargo_geral = re.sub(r"^\d+\.\d+\s+", "",cargo_geral)
        dados_estruturados["area"].append(cargo_geral.strip())
        dados_estruturados["cargo"].append(cargo_especifico.strip())
      else: 
        cargo_tmp = re.sub(r"^\d+\.\d+\s+", "",cargo)
        dados_estruturados["area"].append(cargo_tmp.strip())
        dados_estruturados["cargo"].append(cargo_tmp.strip())

      colocacao, nome = tmp.replace("\n", " ").split("º ")

      dados_estruturados["listagem"].append(listagem.strip().replace("\n",""))
      dados_estruturados["colocacao"].append(colocacao.strip())
      dados_estruturados["nome"].append(nome.strip())

df = pd.DataFrame(dados_estruturados)
df[["nome", "motivo"]] = df["nome"].str.split("(", expand=True)
df["nome"] = df["nome"].str.strip()
df["motivo"] = df["motivo"].str.strip()
df["motivo"] = df["motivo"].str.replace(")", "")


# Caminho para o seu arquivo JSON de credenciais
caminho_credenciais = 'token.json'

# Nome da planilha
nome_planilha = 'HU-UFRR - convocados'

# Nome da aba (sheet)
nome_aba = 'Página1'

# Autenticando com gspread
gc = gspread.service_account(filename=caminho_credenciais)

# Abrindo a planilha e a aba
planilha = gc.open(nome_planilha)
aba = planilha.worksheet(nome_aba)

# Enviar para o Google Sheets
set_with_dataframe(aba, df)

print("script encerrado")