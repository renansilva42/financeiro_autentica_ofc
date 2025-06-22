import requests
import json
from typing import Dict, List, Optional
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Settings

class OmieService:
    def __init__(self):
        self.settings = Settings()
        self.base_url = self.settings.BASE_URL
        self.app_key = self.settings.OMIE_APP_KEY
        self.app_secret = self.settings.OMIE_APP_SECRET
        self.headers = {"Content-Type": "application/json"}
        
        # Cache simples com expiração configurável
        self._cache = {}
        self._cache_expiry = 300  # 5 minutos em segundos (padrão)
        self._service_cache_expiry = 900  # 15 minutos para ordens de serviço
    
    def _get_cache_key(self, method_name: str, **kwargs) -> str:
        """Gera uma chave de cache baseada no método e parâmetros"""
        key_parts = [method_name]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        return "|".join(key_parts)
    
    def _get_from_cache(self, cache_key: str, use_service_expiry: bool = False):
        """Recupera dados do cache se ainda válidos"""
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            expiry_time = self._service_cache_expiry if use_service_expiry else self._cache_expiry
            if time.time() - timestamp < expiry_time:
                return data
            else:
                # Remove entrada expirada
                del self._cache[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, data):
        """Armazena dados no cache com timestamp"""
        self._cache[cache_key] = (data, time.time())
    
    def clear_cache(self):
        """Limpa todo o cache"""
        self._cache.clear()
    
    def clear_cache_by_pattern(self, pattern: str):
        """Limpa entradas do cache que contenham o padrão especificado"""
        keys_to_remove = [key for key in self._cache.keys() if pattern in key]
        for key in keys_to_remove:
            del self._cache[key]
    
    def _make_request(self, resource: str, body: dict) -> dict:
        """Faz uma requisição para a API do Omie"""
        try:
            response = requests.post(
                url=f"{self.base_url}{resource}",
                headers=self.headers,
                json=body,
                timeout=15  # Reduzido para 15 segundos para falhar mais rápido
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
    
    def get_clients_summary_page(self, page: int = 1, records_per_page: int = 50) -> dict:
        """Busca uma página de clientes resumido (mais rápido para mapeamento)"""
        resource = "geral/clientes/"
        action = "ListarClientesResumido"
        
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
    
    def get_all_clients_summary(self) -> List[dict]:
        """Busca todos os clientes resumido (mais rápido para mapeamento de nomes)"""
        # Verificar cache primeiro
        cache_key = self._get_cache_key("get_all_clients_summary")
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        all_clients = []
        page = 1
        
        try:
            # Primeira requisição para saber o total de páginas
            first_response = self.get_clients_summary_page(page)
            total_pages = first_response.get("total_de_paginas", 1)
            
            # Adiciona os clientes da primeira página
            clients = first_response.get("clientes_cadastro_resumido", [])
            all_clients.extend(clients)
            
            # Busca as páginas restantes
            for page in range(2, total_pages + 1):
                response = self.get_clients_summary_page(page)
                clients = response.get("clientes_cadastro_resumido", [])
                all_clients.extend(clients)
            
            # Armazenar no cache
            self._set_cache(cache_key, all_clients)
            return all_clients
            
        except Exception as e:
            print(f"Erro ao buscar clientes resumido: {str(e)}")
            return []
    
    def get_client_name_mapping(self) -> Dict[int, str]:
        """Retorna um dicionário mapeando código do cliente para nome"""
        # Verificar cache primeiro
        cache_key = self._get_cache_key("get_client_name_mapping")
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            clients_summary = self.get_all_clients_summary()
            mapping = {}
            
            for client in clients_summary:
                client_code = client.get("codigo_cliente")
                # Priorizar nome fantasia, depois razão social
                client_name = client.get("nome_fantasia", "").strip()
                if not client_name:
                    client_name = client.get("razao_social", "").strip()
                if not client_name:
                    client_name = f"Cliente {client_code}"
                
                if client_code:
                    mapping[client_code] = client_name
            
            # Armazenar no cache
            self._set_cache(cache_key, mapping)
            return mapping
            
        except Exception as e:
            print(f"Erro ao criar mapeamento de clientes: {str(e)}")
            return {}
    
    def get_client_by_id(self, client_id: int) -> Optional[dict]:
        """Busca um cliente específico pelo ID"""
        try:
            all_clients = self.get_all_clients()
            for client in all_clients:
                # Try both field names for compatibility
                if (client.get("codigo_cliente_omie") == client_id or 
                    client.get("codigo_cliente") == client_id):
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
    
    def get_purchase_orders_page(self, page: int = 1, records_per_page: int = 100, 
                                show_pending: str = "T", show_invoiced: str = "F",
                                show_received: str = "F", show_cancelled: str = "F",
                                show_closed: str = "F", show_partial_received: str = "F",
                                show_partial_invoiced: str = "F", start_date: str = "01/01/2021",
                                end_date: str = "31/12/2021") -> dict:
        """Busca uma página de pedidos de compra"""
        resource = "produtos/pedidocompra/"
        action = "PesquisarPedCompra"
        
        params = {
            "nPagina": page,
            "nRegsPorPagina": records_per_page,
            "lApenasImportadoApi": "F",
            "lExibirPedidosPendentes": show_pending,
            "lExibirPedidosFaturados": show_invoiced,
            "lExibirPedidosRecebidos": show_received,
            "lExibirPedidosCancelados": show_cancelled,
            "lExibirPedidosEncerrados": show_closed,
            "lExibirPedidosRecParciais": show_partial_received,
            "lExibirPedidosFatParciais": show_partial_invoiced,
            "dDataInicial": start_date,
            "dDataFinal": end_date,
            "lApenasAlterados": "F"
        }
        
        body = {
            "call": action,
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [params]
        }
        
        return self._make_request(resource, body)
    
    def get_invoiced_purchase_orders(self, start_date: str = "01/01/2021", 
                                   end_date: str = "31/12/2021") -> List[dict]:
        """Busca todos os pedidos de compra faturados"""
        all_orders = []
        page = 1
        
        try:
            # Primeira requisição para saber o total de páginas
            first_response = self.get_purchase_orders_page(
                page=page, 
                show_pending="F", 
                show_invoiced="T",
                start_date=start_date,
                end_date=end_date
            )
            
            total_pages = first_response.get("nTotPaginas", 1)
            
            # Adiciona os pedidos da primeira página
            orders = first_response.get("pedido_compra_produto", [])
            all_orders.extend(orders)
            
            # Busca as páginas restantes
            for page in range(2, total_pages + 1):
                response = self.get_purchase_orders_page(
                    page=page, 
                    show_pending="F", 
                    show_invoiced="T",
                    start_date=start_date,
                    end_date=end_date
                )
                orders = response.get("pedido_compra_produto", [])
                all_orders.extend(orders)
            
            return all_orders
            
        except Exception as e:
            print(f"Erro ao buscar pedidos de compra faturados: {str(e)}")
            return []
    
    def get_purchase_orders_stats(self, start_date: str = "01/01/2021", 
                                end_date: str = "31/12/2021") -> dict:
        """Retorna estatísticas dos pedidos de compra faturados"""
        try:
            orders = self.get_invoiced_purchase_orders(start_date, end_date)
            
            total_orders = len(orders)
            total_value = sum(float(order.get("nValorTotal", 0)) for order in orders)
            
            # Contagem por fornecedor
            suppliers = {}
            for order in orders:
                supplier = order.get("cNomeFor", "Não informado")
                if supplier == "":
                    supplier = "Não informado"
                suppliers[supplier] = suppliers.get(supplier, 0) + 1
            
            # Contagem por mês
            monthly_stats = {}
            for order in orders:
                date_str = order.get("dDtEmissao", "")
                if date_str:
                    try:
                        # Assumindo formato dd/mm/yyyy
                        month_year = "/".join(date_str.split("/")[1:])  # mm/yyyy
                        monthly_stats[month_year] = monthly_stats.get(month_year, 0) + 1
                    except:
                        pass
            
            # Ordenar os dados mensais cronologicamente
            def sort_month_year(month_year):
                try:
                    month, year = month_year.split('/')
                    return (int(year), int(month))
                except:
                    return (0, 0)
            
            sorted_months = sorted(monthly_stats.keys(), key=sort_month_year)
            monthly_stats = {month: monthly_stats[month] for month in sorted_months}
            
            # Top 5 fornecedores
            top_suppliers = sorted(suppliers.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "total_orders": total_orders,
                "total_value": total_value,
                "average_value": total_value / total_orders if total_orders > 0 else 0,
                "by_supplier": suppliers,
                "top_suppliers": top_suppliers,
                "monthly_stats": monthly_stats
            }
            
        except Exception as e:
            print(f"Erro ao calcular estatísticas de pedidos: {str(e)}")
            return {
                "total_orders": 0,
                "total_value": 0,
                "average_value": 0,
                "by_supplier": {},
                "top_suppliers": [],
                "monthly_stats": {}
            }
    
    def get_sales_orders_page(self, page: int = 1, records_per_page: int = 100) -> dict:
        """Busca uma página de pedidos de venda"""
        resource = "produtos/pedido/"
        action = "ListarPedidos"
        
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
    
    def get_all_sales_orders(self) -> List[dict]:
        """Busca todos os pedidos de venda de todas as páginas"""
        all_orders = []
        page = 1
        
        try:
            # Primeira requisição para saber o total de páginas
            first_response = self.get_sales_orders_page(page)
            total_pages = first_response.get("total_de_paginas", 1)
            
            # Adiciona os pedidos da primeira página
            orders = first_response.get("pedido_venda_produto", [])
            all_orders.extend(orders)
            
            # Busca as páginas restantes
            for page in range(2, total_pages + 1):
                response = self.get_sales_orders_page(page)
                orders = response.get("pedido_venda_produto", [])
                all_orders.extend(orders)
            
            return all_orders
            
        except Exception as e:
            print(f"Erro ao buscar pedidos de venda: {str(e)}")
            return []
    
    def get_sales_orders_stats(self) -> dict:
        """Retorna estatísticas dos pedidos de venda"""
        try:
            orders = self.get_all_sales_orders()
            
            total_orders = len(orders)
            total_value = sum(float(order.get("valor_total_pedido", 0)) for order in orders)
            
            # Contagem por cliente
            clients = {}
            for order in orders:
                client = order.get("nome_cliente", "Não informado")
                if client == "":
                    client = "Não informado"
                clients[client] = clients.get(client, 0) + 1
            
            # Contagem por status
            status_count = {}
            for order in orders:
                status = order.get("etapa", "Não informado")
                if status == "":
                    status = "Não informado"
                status_count[status] = status_count.get(status, 0) + 1
            
            # Contagem por mês
            monthly_stats = {}
            monthly_values = {}
            for order in orders:
                date_str = order.get("data_previsao", "")
                if date_str:
                    try:
                        # Assumindo formato dd/mm/yyyy
                        month_year = "/".join(date_str.split("/")[1:])  # mm/yyyy
                        monthly_stats[month_year] = monthly_stats.get(month_year, 0) + 1
                        monthly_values[month_year] = monthly_values.get(month_year, 0) + float(order.get("valor_total_pedido", 0))
                    except:
                        pass
            
            # Ordenar os dados mensais cronologicamente
            def sort_month_year(month_year):
                try:
                    month, year = month_year.split('/')
                    return (int(year), int(month))
                except:
                    return (0, 0)
            
            sorted_months = sorted(monthly_stats.keys(), key=sort_month_year)
            monthly_stats = {month: monthly_stats[month] for month in sorted_months}
            monthly_values = {month: monthly_values[month] for month in sorted_months}
            
            # Top 5 clientes
            top_clients = sorted(clients.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Pedidos por vendedor
            sellers = {}
            for order in orders:
                seller = order.get("codigo_vendedor", "")
                if seller:
                    seller_name = f"Vendedor {seller}"
                    sellers[seller_name] = sellers.get(seller_name, 0) + 1
            
            return {
                "total_orders": total_orders,
                "total_value": total_value,
                "average_value": total_value / total_orders if total_orders > 0 else 0,
                "by_client": clients,
                "top_clients": top_clients,
                "by_status": status_count,
                "by_seller": sellers,
                "monthly_stats": monthly_stats,
                "monthly_values": monthly_values
            }
            
        except Exception as e:
            print(f"Erro ao calcular estatísticas de vendas: {str(e)}")
            return {
                "total_orders": 0,
                "total_value": 0,
                "average_value": 0,
                "by_client": {},
                "top_clients": [],
                "by_status": {},
                "by_seller": {},
                "monthly_stats": {},
                "monthly_values": {}
            }
    
    def get_service_orders_page(self, page: int = 1, records_per_page: int = 50) -> dict:
        """Busca uma página de ordens de serviço"""
        resource = "servicos/os/"
        action = "ListarOS"
        
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
    
    def get_all_service_orders(self, max_pages: int = None, use_background_loading: bool = True) -> List[dict]:
        """Busca todas as ordens de serviço com estratégia de carregamento otimizada"""
        # Verificar cache primeiro (com tempo de vida estendido)
        cache_key = self._get_cache_key("get_all_service_orders", max_pages=max_pages)
        cached_data = self._get_from_cache(cache_key, use_service_expiry=True)
        if cached_data is not None:
            print(f"Dados de ordens de serviço carregados do cache: {len(cached_data)} registros")
            return cached_data
        
        all_orders = []
        page = 1
        
        try:
            # Primeira requisição para saber o total de páginas
            first_response = self.get_service_orders_page(page)
            total_pages = first_response.get("total_de_paginas", 1)
            total_records = first_response.get("total_de_registros", 0)
            
            print(f"Total de páginas de OS: {total_pages}, Total de registros: {total_records}")
            
            # Se há muitas páginas e use_background_loading está ativo, usar estratégia otimizada
            if total_pages > 10 and use_background_loading:
                return self._get_service_orders_optimized(first_response, total_pages)
            
            # Limitar o número de páginas se especificado
            if max_pages:
                total_pages = min(total_pages, max_pages)
            
            # Adiciona as ordens da primeira página
            orders = first_response.get("osCadastro", [])
            all_orders.extend(orders)
            
            # Busca as páginas restantes com timeout por página
            for page in range(2, total_pages + 1):
                try:
                    response = self.get_service_orders_page(page)
                    orders = response.get("osCadastro", [])
                    all_orders.extend(orders)
                    
                    # Log de progresso a cada 5 páginas
                    if page % 5 == 0:
                        print(f"Progresso: {page}/{total_pages} páginas carregadas")
                        
                except Exception as page_error:
                    print(f"Erro ao buscar página {page}: {str(page_error)}")
                    # Continue com as próximas páginas mesmo se uma falhar
                    continue
            
            # Armazenar no cache
            self._set_cache(cache_key, all_orders)
            return all_orders
            
        except Exception as e:
            print(f"Erro ao buscar ordens de serviço: {str(e)}")
            return []
    
    def _get_service_orders_optimized(self, first_response: dict, total_pages: int) -> List[dict]:
        """Estratégia otimizada para muitas páginas - carrega em lotes menores"""
        all_orders = []
        
        # Adiciona as ordens da primeira página
        orders = first_response.get("osCadastro", [])
        all_orders.extend(orders)
        
        # Carrega em lotes de 5 páginas por vez
        batch_size = 5
        current_page = 2
        
        while current_page <= total_pages:
            batch_end = min(current_page + batch_size - 1, total_pages)
            print(f"Carregando lote: páginas {current_page} a {batch_end}")
            
            # Carrega o lote atual
            for page in range(current_page, batch_end + 1):
                try:
                    response = self.get_service_orders_page(page)
                    orders = response.get("osCadastro", [])
                    all_orders.extend(orders)
                except Exception as page_error:
                    print(f"Erro ao buscar página {page}: {str(page_error)}")
                    continue
            
            current_page = batch_end + 1
            
            # Pequena pausa entre lotes para não sobrecarregar a API
            import time
            time.sleep(0.1)
        
        # Cache com tempo de vida maior para dados completos
        cache_key = self._get_cache_key("get_all_service_orders", max_pages=None)
        self._set_cache(cache_key, all_orders)
        
        return all_orders
    
    def get_service_orders_stats(self) -> dict:
        """Retorna estatísticas das ordens de serviço"""
        try:
            # Buscar todas as ordens com carregamento otimizado
            orders = self.get_all_service_orders()
            
            total_orders = len(orders)
            
            # Calcular valor total - a estrutura é diferente
            total_value = 0
            for order in orders:
                cabecalho = order.get("Cabecalho", {})
                total_value += float(cabecalho.get("nValorTotal", 0))
            
            # Buscar mapeamento de nomes de clientes
            client_name_mapping = self.get_client_name_mapping()
            
            # Contagem por cliente - usar nomes reais dos clientes
            clients = {}
            for order in orders:
                cabecalho = order.get("Cabecalho", {})
                client_code = cabecalho.get("nCodCli", "")
                if client_code:
                    # Usar nome real do cliente se disponível
                    client_name = client_name_mapping.get(client_code, f"Cliente {client_code}")
                else:
                    client_name = "Não informado"
                clients[client_name] = clients.get(client_name, 0) + 1
            
            # Contagem por status/etapa
            status_count = {}
            for order in orders:
                cabecalho = order.get("Cabecalho", {})
                status = cabecalho.get("cEtapa", "Não informado")
                if status == "":
                    status = "Não informado"
                # Mapear códigos de etapa para nomes mais amigáveis
                status_map = {
                    "10": "Pendente",
                    "20": "Em Andamento", 
                    "30": "Aguardando Aprovação",
                    "40": "Aprovada",
                    "50": "Em Execução",
                    "60": "Faturada",
                    "70": "Cancelada"
                }
                status_name = status_map.get(status, f"Etapa {status}")
                status_count[status_name] = status_count.get(status_name, 0) + 1
            
            # Contagem por tipo de serviço
            service_types = {}
            for order in orders:
                servicos = order.get("ServicosPrestados", [])
                for servico in servicos:
                    service_type = servico.get("cDescServ", "Não informado")
                    if service_type == "":
                        service_type = "Não informado"
                    service_types[service_type] = service_types.get(service_type, 0) + 1
            
            # Contagem por mês
            monthly_stats = {}
            monthly_values = {}
            for order in orders:
                cabecalho = order.get("Cabecalho", {})
                date_str = cabecalho.get("dDtPrevisao", "")
                if date_str:
                    try:
                        # Assumindo formato dd/mm/yyyy
                        month_year = "/".join(date_str.split("/")[1:])  # mm/yyyy
                        monthly_stats[month_year] = monthly_stats.get(month_year, 0) + 1
                        monthly_values[month_year] = monthly_values.get(month_year, 0) + float(cabecalho.get("nValorTotal", 0))
                    except:
                        pass
            
            # Ordenar os dados mensais cronologicamente
            def sort_month_year(month_year):
                try:
                    month, year = month_year.split('/')
                    return (int(year), int(month))
                except:
                    return (0, 0)
            
            sorted_months = sorted(monthly_stats.keys(), key=sort_month_year)
            monthly_stats = {month: monthly_stats[month] for month in sorted_months}
            monthly_values = {month: monthly_values[month] for month in sorted_months}
            
            # Top 5 clientes
            top_clients = sorted(clients.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Top 5 tipos de serviço
            top_services = sorted(service_types.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Ordens por vendedor (usando nCodVend)
            sellers = {}
            for order in orders:
                cabecalho = order.get("Cabecalho", {})
                seller_code = cabecalho.get("nCodVend", "")
                if seller_code:
                    seller_name = f"Vendedor {seller_code}"
                    sellers[seller_name] = sellers.get(seller_name, 0) + 1
            
            return {
                "total_orders": total_orders,
                "total_value": total_value,
                "average_value": total_value / total_orders if total_orders > 0 else 0,
                "by_client": clients,
                "top_clients": top_clients,
                "by_status": status_count,
                "by_service_type": service_types,
                "top_services": top_services,
                "by_technician": sellers,  # Usando vendedores como "técnicos"
                "monthly_stats": monthly_stats,
                "monthly_values": monthly_values
            }
            
        except Exception as e:
            print(f"Erro ao calcular estatísticas de ordens de serviço: {str(e)}")
            return {
                "total_orders": 0,
                "total_value": 0,
                "average_value": 0,
                "by_client": {},
                "top_clients": [],
                "by_status": {},
                "by_service_type": {},
                "top_services": [],
                "by_technician": {},
                "monthly_stats": {},
                "monthly_values": {}
            }
    
    def get_available_months_for_services(self) -> List[dict]:
        """Retorna lista de meses disponíveis para filtro de ordens de serviço"""
        try:
            # Buscar todas as ordens para ter lista completa de meses
            orders = self.get_all_service_orders()
            months_set = set()
            
            for order in orders:
                cabecalho = order.get("Cabecalho", {})
                date_str = cabecalho.get("dDtPrevisao", "")
                if date_str:
                    try:
                        # Extrair mês/ano da data (formato dd/mm/yyyy)
                        parts = date_str.split("/")
                        if len(parts) >= 3:
                            month_year = f"{parts[1]}/{parts[2]}"  # mm/yyyy
                            months_set.add(month_year)
                    except:
                        pass
            
            # Converter para lista e ordenar cronologicamente
            def sort_month_year(month_year):
                try:
                    month, year = month_year.split('/')
                    return (int(year), int(month))
                except:
                    return (0, 0)
            
            sorted_months = sorted(list(months_set), key=sort_month_year, reverse=True)
            
            # Converter para formato mais amigável
            month_names = {
                '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março', '04': 'Abril',
                '05': 'Maio', '06': 'Junho', '07': 'Julho', '08': 'Agosto',
                '09': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'
            }
            
            result = []
            for month_year in sorted_months:
                try:
                    month, year = month_year.split('/')
                    month_name = month_names.get(month, month)
                    result.append({
                        'value': month_year,
                        'label': f"{month_name} {year}"
                    })
                except:
                    result.append({
                        'value': month_year,
                        'label': month_year
                    })
            
            return result
            
        except Exception as e:
            print(f"Erro ao buscar meses disponíveis: {str(e)}")
            return []
    
    def get_monthly_service_stats(self, month_filter: str) -> dict:
        """Retorna estatísticas das ordens de serviço para um mês específico"""
        try:
            # Buscar todas as ordens para estatísticas precisas
            all_orders = self.get_all_service_orders()
            
            # Filtrar ordens pelo mês especificado
            filtered_orders = []
            for order in all_orders:
                cabecalho = order.get("Cabecalho", {})
                date_str = cabecalho.get("dDtPrevisao", "")
                if date_str:
                    try:
                        # Extrair mês/ano da data (formato dd/mm/yyyy)
                        month_year = "/".join(date_str.split("/")[1:])  # mm/yyyy
                        if month_year == month_filter:
                            filtered_orders.append(order)
                    except:
                        pass
            
            total_orders = len(filtered_orders)
            
            # Calcular valor total
            total_value = 0
            for order in filtered_orders:
                cabecalho = order.get("Cabecalho", {})
                total_value += float(cabecalho.get("nValorTotal", 0))
            
            # Calcular ticket médio
            average_value = total_value / total_orders if total_orders > 0 else 0
            
            # Contar clientes únicos
            unique_clients = set()
            for order in filtered_orders:
                cabecalho = order.get("Cabecalho", {})
                client_code = cabecalho.get("nCodCli", "")
                if client_code:
                    unique_clients.add(client_code)
            
            unique_clients_count = len(unique_clients)
            
            # Formatar o nome do mês para exibição
            month_names = {
                '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março', '04': 'Abril',
                '05': 'Maio', '06': 'Junho', '07': 'Julho', '08': 'Agosto',
                '09': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'
            }
            
            try:
                month, year = month_filter.split('/')
                month_name = month_names.get(month, month)
                formatted_month = f"{month_name} {year}"
            except:
                formatted_month = month_filter
            
            return {
                "month_filter": month_filter,
                "formatted_month": formatted_month,
                "total_orders": total_orders,
                "total_value": total_value,
                "average_value": average_value,
                "unique_clients": unique_clients_count
            }
            
        except Exception as e:
            print(f"Erro ao calcular estatísticas mensais: {str(e)}")
            return {
                "month_filter": month_filter,
                "formatted_month": month_filter,
                "total_orders": 0,
                "total_value": 0,
                "average_value": 0,
                "unique_clients": 0
            }