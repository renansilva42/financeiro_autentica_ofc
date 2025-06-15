"""
Script para buscar dados dos clientes da API Omie
Este script pode ser usado para sincronizar dados ou fazer backup
"""

import requests
import json
from datetime import datetime
from config import Settings

def fetch_all_clients():
    """Busca todos os clientes da API Omie e salva em arquivo JSON"""
    settings = Settings()
    
    base_url = settings.BASE_URL
    app_key = settings.OMIE_APP_KEY
    app_secret = settings.OMIE_APP_SECRET
    
    headers = {"Content-Type": "application/json"}
    
    def make_request(resource: str, body: dict) -> dict:
        response = requests.post(
            url=f"{base_url}{resource}",
            headers=headers, 
            json=body,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro na API: {response.status_code} - {response.text}")

    # Configuração da busca
    resource = "geral/clientes/"
    action = "ListarClientes"
    
    params = {
        "pagina": 1,
        "registros_por_pagina": 100,
        "apenas_importado_api": "N"
    }
    
    # Primeira requisição para saber o total de páginas
    body = {
        "call": action,
        "app_key": app_key,
        "app_secret": app_secret,
        "param": [params]
    }
    
    print("Buscando informações dos clientes...")
    first_response = make_request(resource, body)
    
    total_pages = first_response.get("total_de_paginas", 0)
    total_records = first_response.get("total_de_registros", 0)
    
    print(f"Total de páginas: {total_pages}")
    print(f"Total de registros: {total_records}")
    
    # Coleta todos os clientes
    all_clients = []
    all_clients.extend(first_response.get("clientes_cadastro", []))
    
    # Busca as páginas restantes
    for page in range(2, total_pages + 1):
        params["pagina"] = page
        
        body = {
            "call": action,
            "app_key": app_key,
            "app_secret": app_secret,
            "param": [params]
        }
        
        response = make_request(resource, body)
        clients = response.get("clientes_cadastro", [])
        all_clients.extend(clients)
        
        print(f"Página {page}/{total_pages} - {len(clients)} clientes")
    
    # Salva os dados em arquivo JSON
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "total_clients": len(all_clients),
        "clients": all_clients
    }
    
    with open('clients_backup.json', 'w', encoding='utf-8') as file:
        json.dump(output_data, file, ensure_ascii=False, indent=2)
    
    print(f"\nBackup concluído!")
    print(f"Total de clientes salvos: {len(all_clients)}")
    print(f"Arquivo salvo: clients_backup.json")
    
    return all_clients

if __name__ == "__main__":
    try:
        clients = fetch_all_clients()
        print("Script executado com sucesso!")
    except Exception as e:
        print(f"Erro ao executar script: {str(e)}")