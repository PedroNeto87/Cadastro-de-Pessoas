import requests
import json

def consultaCep(cep):
    url = f"https://viacep.com.br/ws/{cep}/json/"
    
    response = requests.request("GET", url)
    resp = json.loads(response.text)

    return resp['logradouro'], resp['complemento'], resp['bairro'], resp['localidade'], resp['uf']