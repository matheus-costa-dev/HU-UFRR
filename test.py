import json
import os
# Alternativa 1: Ler do arquivo
try:
    with open("token.json") as f:
        data = json.load(f)
        print("Dados do token.json:")
        print(f"Nome: {data}")
except Exception as e:
    print(f"Erro ao ler arquivo: {e}")
