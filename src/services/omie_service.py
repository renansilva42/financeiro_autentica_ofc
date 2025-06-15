import requests
import json
from typing import Dict, List, Optional
from config import Settings

class OmieService:
    def __init__(self):
        self.settings = Settings()
        self.base_url = self.settings.BASE_URL
        self.app_key = self.settings.OMIE_APP_KEY
        self.app_secret = self.settings.OMIE_APP_SECRET
        self.headers = {"Content-Type": "application/json"}
    
    def _make_request(self, resource: str, body: dict) -> dict:
        """Faz uma requisição para a API do Omie"""
        try:
            response = requests.post(
                url=f"{self.base_url}{resource}",
                headers=self.headers,
                json=body,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Erro na API: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro de conexão: {str(e)}")
    
    def get_clients_page(self, page: int = 1, records_per_page: int = 100) -> dict:
        """Busca uma página de clientes"""
        resource = "geral/clientes/"
        action = "ListarClientes"
        
        params = {
            "pagina": page,
            "registros_por_pagina": records_per_page,
            "apenas_importado_api": "N"
        }
        
        body = {
            "call": action,
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [params]
        }
        
        return self._make_request(resource, body)
    
    def get_all_clients(self) -> List[dict]:
        """Busca todos os clientes de todas as páginas"""
        all_clients = []
        page = 1
        
        try:
            # Primeira requisição para saber o total de páginas
            first_response = self.get_clients_page(page)
            total_pages = first_response.get("total_de_paginas", 1)
            
            # Adiciona os clientes da primeira página
            clients = first_response.get("clientes_cadastro", [])
            all_clients.extend(clients)
            
            # Busca as páginas restantes
            for page in range(2, total_pages + 1):
                response = self.get_clients_page(page)
                clients = response.get("clientes_cadastro", [])
                all_clients.extend(clients)
            
            return all_clients
            
        except Exception as e:
            print(f"Erro ao buscar clientes: {str(e)}")
            return []
    
    def get_client_by_id(self, client_id: int) -> Optional[dict]:
        """Busca um cliente específico pelo ID"""
        try:
            all_clients = self.get_all_clients()
            for client in all_clients:
                if client.get("codigo_cliente_omie") == client_id:
                    return client
            return None
        except Exception as e:
            print(f"Erro ao buscar cliente {client_id}: {str(e)}")
            return None
    
    def search_clients(self, search_term: str) -> List[dict]:
        """Busca clientes por nome, razão social ou CNPJ/CPF"""
        try:
            all_clients = self.get_all_clients()
            search_term = search_term.lower()
            
            filtered_clients = []
            for client in all_clients:
                # Busca em nome fantasia, razão social e CNPJ/CPF
                nome_fantasia = client.get("nome_fantasia", "").lower()
                razao_social = client.get("razao_social", "").lower()
                cnpj_cpf = client.get("cnpj_cpf", "").lower()
                
                if (search_term in nome_fantasia or 
                    search_term in razao_social or 
                    search_term in cnpj_cpf):
                    filtered_clients.append(client)
            
            return filtered_clients
            
        except Exception as e:
            print(f"Erro ao buscar clientes: {str(e)}")
            return []
    
    def get_clients_stats(self) -> dict:
        """Retorna estatísticas dos clientes"""
        try:
            all_clients = self.get_all_clients()
            
            total_clients = len(all_clients)
            active_clients = len([c for c in all_clients if c.get("inativo") == "N"])
            inactive_clients = total_clients - active_clients
            
            # Contagem por tipo de pessoa
            pessoa_fisica = len([c for c in all_clients if c.get("pessoa_fisica") == "S"])
            pessoa_juridica = total_clients - pessoa_fisica
            
            # Contagem por estado
            states = {}
            for client in all_clients:
                state = client.get("estado", "Não informado")
                if state == "":
                    state = "Não informado"
                states[state] = states.get(state, 0) + 1
            
            return {
                "total_clients": total_clients,
                "active_clients": active_clients,
                "inactive_clients": inactive_clients,
                "pessoa_fisica": pessoa_fisica,
                "pessoa_juridica": pessoa_juridica,
                "by_state": states
            }
            
        except Exception as e:
            print(f"Erro ao calcular estatísticas: {str(e)}")
            return {
                "total_clients": 0,
                "active_clients": 0,
                "inactive_clients": 0,
                "pessoa_fisica": 0,
                "pessoa_juridica": 0,
                "by_state": {}
            }