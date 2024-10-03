# import os
# from pathlib import Path
# from uuid import uuid4

# filename = 'Alteração Forms Recuperação de Crédito.pdf'

# raiz, extensao = os.path.splitext(filename)
# novo_file_name_unique = str(uuid4())+extensao

# try:
#     path_filename_original = f"{Path(os.getcwd()) / 'uploads' / filename}" 
#     os.rename(path_filename_original, novo_file_name_unique)
# except OSError as error:
#     print(f"Erro ao renomear o arquivo: {error}")
# else:
#     print("Arquivo renomeado com sucesso!")

import requests
from requests.structures import CaseInsensitiveDict
import json
import os


# Dados do JSON
payload = {}
headers = { 
    'Content-Type': 'application/json',
    'Authorization': """Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyMzgyNzE4MCwianRpIjoiNDIyN2E2NzMtZWUyNi00NTJkLWFmZDMtYzA1ZWQwNjI4MDY5IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InVzZXJfdGVzdGUiLCJuYmYiOjE3MjM4MjcxODAsImNzcmYiOiJjOWM2MjI5MS0zNjM3LTQzODktYjdmMi0zM2ViNzU2ZDI4N2MiLCJleHAiOjE3MjM4MjgwODB9.w6UOF3acOEqsEOebVQeLLZRDRFfW6ZR0O90aZNkjcwk"""
}
# Converter dicionário para JSON
#data = json.dumps(payload)

#headers = CaseInsensitiveDict()
#headers["Accept"] = "application/json"
#headers["Content-Type"] = "application/json"

# Arquivo a ser enviado



# URL da API
url = "https://192.168.0.111:5000//fgb/v1/operations/download?id=rIUcQpidLI"


# Enviando a requisição POST
pasta = 'uploads'
pasta_destino = os.path.join(pasta,'TERMINALDECAIXAPASSOAPASSOCONTRATAO_2.PPTX')
response = requests.get(url,headers=headers,stream=True,verify=False)

if response.status_code == 200:
    content_type = response.headers.get('Content-Type')
    if content_type and content_type.startswith('application/'):
        # Definir o caminho do arquivo local
        #file_path = 'downloaded_file.ext'  # Substitua '.ext' pela extensão correta

        with open(pasta_destino, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Arquivo baixado com sucesso para {pasta_destino}")
else:
    print('Erro ao enviar a requisição:', response.text)
