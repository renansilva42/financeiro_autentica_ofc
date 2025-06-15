import requests
from config import Settings

settings = Settings()

base_url = settings.BASE_URL
app_key = settings.OMIE_APP_KEY
app_secret = settings.OMIE_APP_SECRET

endpoints = [
    {
        "resources": "geral/clientes/",
        "action": "ListarClientes",
        "params": {
            "pagina": 1,
            "registros_por_pagina": 100,
            "apenas_importado_api": "N"
        }
    }
]

HEADERS = {
    "Content-Type": "application/json",
}

def request(resource: str, body: dict) -> dict:
    response = requests.post(
        url=f"{base_url}{resource}",
        headers=HEADERS, 
        json=body
    )

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code}")

def get_total_of_pages(resource: str, action: str, params: dict) -> int:
    payload = {
        "call": action,
        "app_key": app_key,
        "app_secret": app_secret,
        "param": [params]
    }
    
    response = request(resource, payload)
    total_of_pages = response.get("total_de_paginas", 0)
    records = response.get("total_de_registros", 0)
    print(f"Total of pages: {total_of_pages}")
    print(f"Total of records: {records}")
    
    return total_of_pages

def save_to_file(resoure:str, content: dict):
    file_name = resource.split("/")[-1]
    print(file_name)

    # with open('output.json', 'wb') as file:
    #     file.write(content)

for endpoint in endpoints:
    resource = endpoint.get("resources", "")
    action = endpoint.get("action", "")
    params = endpoint.get("params", {})

    total_of_pages = get_total_of_pages(resource, action, params)

    records_fetched = 0
    for page in range(1, total_of_pages + 1):
        params["pagina"] = page

        body = {
            "call": action,
            "app_key": app_key,
            "app_secret": app_secret,
            "param": [params]
        }
        
        # Corrigido: removido o terceiro parâmetro 'params'
        response = request(resource, body)
        records_fetched += response.get("registros", 0)
        
        print(f"Page: {page}", f"Records fetched: {records_fetched}")

# Você pode adicionar aqui o código para processar todas as páginas
# e salvar os resultados em um arquivo, se necessário.