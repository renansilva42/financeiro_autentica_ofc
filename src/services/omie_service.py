import requests
import json
from typing import Dict, List, Optional, Callable
import sys
import os
import time
import asyncio
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Settings

class OmieService:
    def __init__(self):
        self.settings = Settings()
        self.base_url = self.settings.BASE_URL
        self.app_key = self.settings.OMIE_APP_KEY
        self.app_secret = self.settings.OMIE_APP_SECRET
        self.headers = {"Content-Type": "application/json"}
        
        # Cache simples com expiração configurável (fallback)
        self._cache = {}
        self._cache_expiry = 600  # 10 minutos em segundos (padrão)
        self._service_cache_expiry = 1800  # 30 minutos para ordens de serviço
        self._mapping_cache_expiry = 3600  # 1 hora para mapeamentos (mudam menos)
        
        # Sistema de cache inteligente (será inicializado externamente)
        self.intelligent_cache = None
        self.progress_callback: Optional[Callable] = None
    
    def _get_cache_key(self, method_name: str, **kwargs) -> str:
        """Gera uma chave de cache baseada no método e parâmetros"""
        key_parts = [method_name]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        return "|".join(key_parts)
    
    def _get_from_cache(self, cache_key: str, use_service_expiry: bool = False, use_mapping_expiry: bool = False):
        """Recupera dados do cache se ainda válidos"""
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            
            # Determinar tempo de expiração baseado no tipo de dados
            if use_mapping_expiry:
                expiry_time = self._mapping_cache_expiry
            elif use_service_expiry:
                expiry_time = self._service_cache_expiry
            else:
                expiry_time = self._cache_expiry
                
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
    
    def clear_weeks_cache(self):
        """Limpa especificamente o cache de semanas disponíveis"""
        self.clear_cache_by_pattern("get_available_weeks_for_services")
        if self.intelligent_cache:
            asyncio.create_task(self.intelligent_cache.clear_cache(pattern="get_available_weeks_for_services"))
        print("Cache de semanas disponíveis limpo")
    
    def set_intelligent_cache(self, cache_service):
        """Define o serviço de cache inteligente"""
        self.intelligent_cache = cache_service
        print("Cache inteligente configurado para OmieService")
    
    def set_progress_callback(self, callback: Callable):
        """Define callback para progresso de carregamento"""
        self.progress_callback = callback
    
    async def _get_from_intelligent_cache(self, cache_key: str, data_type: str) -> Optional[any]:
        """Recupera dados do cache inteligente se disponível"""
        if self.intelligent_cache:
            try:
                return await self.intelligent_cache.get(cache_key, data_type)
            except Exception as e:
                print(f"Erro ao acessar cache inteligente: {e}")
        return None
    
    async def _set_intelligent_cache(self, cache_key: str, data: any, data_type: str) -> bool:
        """Armazena dados no cache inteligente se disponível"""
        if self.intelligent_cache:
            try:
                return await self.intelligent_cache.set(cache_key, data, data_type)
            except Exception as e:
                print(f"Erro ao salvar no cache inteligente: {e}")
        return False
    
    def _make_request(self, resource: str, body: dict, timeout: int = 10) -> dict:
        """Faz uma requisição para a API do Omie com timeout configurável"""
        try:
            response = requests.post(
                url=f"{self.base_url}{resource}",
                headers=self.headers,
                json=body,
                timeout=timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Erro na API: {response.status_code} - {response.text}")
        except requests.exceptions.Timeout:
            raise Exception(f"Timeout na requisição para {resource} após {timeout} segundos")
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
        # Verificar cache primeiro com tempo de vida estendido
        cache_key = self._get_cache_key("get_all_clients_summary")
        cached_data = self._get_from_cache(cache_key, use_mapping_expiry=True)
        if cached_data is not None:
            print(f"Clientes carregados do cache: {len(cached_data)} registros")
            return cached_data
        
        all_clients = []
        page = 1
        
        try:
            # Primeira requisição para saber o total de páginas
            first_response = self.get_clients_summary_page(page)
            total_pages = first_response.get("total_de_paginas", 1)
            total_records = first_response.get("total_de_registros", 0)
            
            print(f"Carregando clientes: {total_pages} páginas, {total_records} registros")
            
            # Adiciona os clientes da primeira página
            clients = first_response.get("clientes_cadastro_resumido", [])
            all_clients.extend(clients)
            
            # Busca as páginas restantes com timeout otimizado
            for page in range(2, total_pages + 1):
                try:
                    response = self.get_clients_summary_page(page)
                    clients = response.get("clientes_cadastro_resumido", [])
                    all_clients.extend(clients)
                    
                    # Log de progresso a cada 20 páginas
                    if page % 20 == 0:
                        print(f"Progresso clientes: {page}/{total_pages} páginas ({len(all_clients)} registros)")
                        
                except Exception as page_error:
                    print(f"Erro ao buscar página {page} de clientes: {str(page_error)}")
                    # Continue com as próximas páginas mesmo se uma falhar
                    continue
            
            print(f"Clientes carregados: {len(all_clients)} registros de {total_pages} páginas")
            
            # Armazenar no cache
            self._set_cache(cache_key, all_clients)
            return all_clients
            
        except Exception as e:
            print(f"Erro ao buscar clientes resumido: {str(e)}")
            return []
    
    def get_client_name_mapping(self) -> Dict[int, str]:
        """Retorna um dicionário mapeando código do cliente para nome"""
        cache_key = self._get_cache_key("get_client_name_mapping")
        
        # Tentar cache inteligente se disponível
        if self.intelligent_cache:
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    cached_mapping = loop.run_until_complete(
                        self._get_from_intelligent_cache(cache_key, "mappings")
                    )
                    if cached_mapping is not None:
                        print(f"Mapeamento de clientes carregado do cache inteligente: {len(cached_mapping)} clientes")
                        return cached_mapping
                finally:
                    loop.close()
            except Exception as e:
                print(f"Erro ao acessar cache inteligente para mapeamento: {e}")
        
        # Verificar cache local com tempo de vida estendido
        cached_data = self._get_from_cache(cache_key, use_mapping_expiry=True)
        if cached_data is not None:
            print(f"Mapeamento de clientes carregado do cache local: {len(cached_data)} clientes")
            return cached_data
        
        try:
            print("Criando mapeamento de clientes da API...")
            # Buscar todos os clientes para mapeamento completo
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
            
            # Armazenar no cache local
            self._set_cache(cache_key, mapping)
            
            # Salvar no cache inteligente se disponível
            if self.intelligent_cache:
                try:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(
                            self._set_intelligent_cache(cache_key, mapping, "mappings")
                        )
                        print("Mapeamento de clientes salvo no cache inteligente")
                    finally:
                        loop.close()
                except Exception as e:
                    print(f"Erro ao salvar mapeamento no cache inteligente: {e}")
            
            print(f"Mapeamento de clientes criado: {len(mapping)} clientes")
            return mapping
            
        except Exception as e:
            print(f"Erro ao criar mapeamento de clientes: {str(e)}")
            return {}
    
    def get_sellers_page(self, page: int = 1, records_per_page: int = 100) -> dict:
        """Busca uma página de vendedores"""
        resource = "geral/vendedores/"
        action = "ListarVendedores"
        
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
    
    def get_all_sellers(self) -> List[dict]:
        """Busca todos os vendedores de todas as páginas"""
        # Verificar cache primeiro com tempo de vida estendido
        cache_key = self._get_cache_key("get_all_sellers")
        cached_data = self._get_from_cache(cache_key, use_mapping_expiry=True)
        if cached_data is not None:
            print(f"Vendedores carregados do cache: {len(cached_data)} registros")
            return cached_data
        
        all_sellers = []
        page = 1
        
        try:
            # Primeira requisição para saber o total de páginas
            first_response = self.get_sellers_page(page)
            total_pages = first_response.get("total_de_paginas", 1)
            total_records = first_response.get("total_de_registros", 0)
            
            print(f"Carregando vendedores: {total_pages} páginas, {total_records} registros")
            
            # Adiciona os vendedores da primeira página
            sellers = first_response.get("cadastro", [])
            all_sellers.extend(sellers)
            
            # Busca as páginas restantes com timeout otimizado
            for page in range(2, total_pages + 1):
                try:
                    response = self.get_sellers_page(page)
                    sellers = response.get("cadastro", [])
                    all_sellers.extend(sellers)
                    
                    # Log de progresso a cada 10 páginas
                    if page % 10 == 0:
                        print(f"Progresso vendedores: {page}/{total_pages} páginas ({len(all_sellers)} registros)")
                        
                except Exception as page_error:
                    print(f"Erro ao buscar página {page} de vendedores: {str(page_error)}")
                    # Continue com as próximas páginas mesmo se uma falhar
                    continue
            
            print(f"Vendedores carregados: {len(all_sellers)} registros de {total_pages} páginas")
            
            # Armazenar no cache
            self._set_cache(cache_key, all_sellers)
            return all_sellers
            
        except Exception as e:
            print(f"Erro ao buscar vendedores: {str(e)}")
            return []
    
    def get_seller_name_mapping(self) -> Dict[int, str]:
        """Retorna um dicionário mapeando código do vendedor para nome"""
        # Verificar cache primeiro com tempo de vida estendido
        cache_key = self._get_cache_key("get_seller_name_mapping")
        cached_data = self._get_from_cache(cache_key, use_mapping_expiry=True)
        if cached_data is not None:
            print(f"Mapeamento de vendedores carregado do cache: {len(cached_data)} vendedores")
            return cached_data
        
        try:
            # Buscar todos os vendedores para mapeamento completo
            sellers = self.get_all_sellers()
            mapping = {}
            
            for seller in sellers:
                seller_code = seller.get("codigo")
                seller_name = seller.get("nome", "").strip()
                
                if not seller_name:
                    seller_name = f"Vendedor {seller_code}"
                
                if seller_code:
                    mapping[seller_code] = seller_name
            
            # Armazenar no cache
            self._set_cache(cache_key, mapping)
            print(f"Mapeamento de vendedores criado: {len(mapping)} vendedores")
            return mapping
            
        except Exception as e:
            print(f"Erro ao criar mapeamento de vendedores: {str(e)}")
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
        # Verificar cache inteligente primeiro
        cache_key = self._get_cache_key("get_clients_stats")
        
        # Tentar cache inteligente se disponível
        if self.intelligent_cache:
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    cached_stats = loop.run_until_complete(
                        self._get_from_intelligent_cache(cache_key, "stats")
                    )
                    if cached_stats is not None:
                        print("Estatísticas de clientes carregadas do cache inteligente")
                        return cached_stats
                finally:
                    loop.close()
            except Exception as e:
                print(f"Erro ao acessar cache inteligente para stats: {e}")
        
        # Verificar cache local
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            print("Estatísticas de clientes carregadas do cache local")
            return cached_data
        
        try:
            print("Calculando estatísticas de clientes da API...")
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
            
            stats = {
                "total_clients": total_clients,
                "active_clients": active_clients,
                "inactive_clients": inactive_clients,
                "pessoa_fisica": pessoa_fisica,
                "pessoa_juridica": pessoa_juridica,
                "by_state": states
            }
            
            # Salvar no cache local
            self._set_cache(cache_key, stats)
            
            # Salvar no cache inteligente se disponível
            if self.intelligent_cache:
                try:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(
                            self._set_intelligent_cache(cache_key, stats, "stats")
                        )
                        print("Estatísticas salvas no cache inteligente")
                    finally:
                        loop.close()
                except Exception as e:
                    print(f"Erro ao salvar no cache inteligente: {e}")
            
            return stats
            
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
    
    def get_all_service_orders(self, use_optimized_loading: bool = True) -> List[dict]:
        """Busca todas as ordens de serviço com estratégia de carregamento otimizada"""
        # Verificar cache primeiro (com tempo de vida estendido)
        cache_key = self._get_cache_key("get_all_service_orders")
        cached_data = self._get_from_cache(cache_key, use_service_expiry=True)
        if cached_data is not None:
            print(f"Ordens de serviço carregadas do cache: {len(cached_data)} registros")
            return cached_data
        
        all_orders = []
        page = 1
        
        try:
            # Primeira requisição para saber o total de páginas
            first_response = self.get_service_orders_page(page)
            total_pages = first_response.get("total_de_paginas", 1)
            total_records = first_response.get("total_de_registros", 0)
            
            print(f"Carregando ordens de serviço: {total_pages} páginas, {total_records} registros")
            
            # Se há muitas páginas, usar estratégia otimizada
            if total_pages > 10 and use_optimized_loading:
                return self._get_service_orders_optimized(first_response, total_pages)
            
            # Adiciona as ordens da primeira página
            orders = first_response.get("osCadastro", [])
            all_orders.extend(orders)
            
            # Busca as páginas restantes com timeout otimizado
            for page in range(2, total_pages + 1):
                try:
                    response = self.get_service_orders_page(page)
                    orders = response.get("osCadastro", [])
                    all_orders.extend(orders)
                    
                    # Log de progresso a cada 10 páginas
                    if page % 10 == 0:
                        print(f"Progresso OS: {page}/{total_pages} páginas ({len(all_orders)} registros)")
                        
                except Exception as page_error:
                    print(f"Erro ao buscar página {page} de OS: {str(page_error)}")
                    # Continue com as próximas páginas mesmo se uma falhar
                    continue
            
            print(f"Ordens de serviço carregadas: {len(all_orders)} registros de {total_pages} páginas")
            
            # Armazenar no cache
            self._set_cache(cache_key, all_orders)
            return all_orders
            
        except Exception as e:
            print(f"Erro ao buscar ordens de serviço: {str(e)}")
            return []
    
    def _get_service_orders_optimized(self, first_response: dict, total_pages: int) -> List[dict]:
        """Estratégia otimizada para muitas páginas - carrega em lotes com pausa"""
        all_orders = []
        
        # Adiciona as ordens da primeira página
        orders = first_response.get("osCadastro", [])
        all_orders.extend(orders)
        
        # Carrega em lotes de 8 páginas por vez com pausa entre lotes
        batch_size = 8
        current_page = 2
        
        while current_page <= total_pages:
            batch_end = min(current_page + batch_size - 1, total_pages)
            print(f"Carregando lote OS: páginas {current_page} a {batch_end}")
            
            # Carrega o lote atual
            batch_orders = 0
            for page in range(current_page, batch_end + 1):
                try:
                    response = self.get_service_orders_page(page)
                    orders = response.get("osCadastro", [])
                    all_orders.extend(orders)
                    batch_orders += len(orders)
                    
                    # Pequena pausa entre páginas para não sobrecarregar
                    time.sleep(0.05)
                    
                except Exception as page_error:
                    print(f"Erro ao buscar página {page} de OS: {str(page_error)}")
                    continue
            
            print(f"Lote concluído: {batch_orders} ordens carregadas ({len(all_orders)} total)")
            current_page = batch_end + 1
            
            # Pausa maior entre lotes para dar tempo ao servidor
            if current_page <= total_pages:
                time.sleep(0.2)
        
        print(f"Carregamento otimizado concluído: {len(all_orders)} ordens de serviço")
        
        # Cache com tempo de vida maior para dados completos
        cache_key = self._get_cache_key("get_all_service_orders")
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
            
            # Buscar mapeamento de serviços para usar nomes reais
            service_name_mapping = self.get_service_name_mapping()
            print(f"Mapeamento de serviços carregado: {len(service_name_mapping)} serviços")
            
            # Contagem por tipo de serviço
            service_types = {}
            service_breakdown = {}
            
            for order in orders:
                cabecalho = order.get("Cabecalho", {})
                order_status = cabecalho.get("cEtapa", "")
                order_code = cabecalho.get("nCodOS", "")
                
                servicos = order.get("ServicosPrestados", [])
                
                for i, servico in enumerate(servicos):
                    # Usar código do serviço (nCodServico) para buscar o nome real
                    service_code = servico.get("nCodServico", "")
                    service_desc = servico.get("cDescServ", "").strip()
                    
                    if service_code and service_code != 0:
                        # Usar código do serviço se disponível
                        service_type = service_name_mapping.get(service_code, f"Serviço {service_code}")
                    elif service_desc:
                        # Se código não está disponível, tentar mapear a descrição para um serviço cadastrado
                        service_type = self._map_service_description_to_registered(service_desc, service_name_mapping)
                    else:
                        service_type = "Não informado"
                    
                    # Calcular valor específico do item de serviço
                    quantidade = float(servico.get("nQtde", 1))
                    valor_unitario = float(servico.get("nValUnit", 0))
                    valor_desconto = float(servico.get("nValorDesconto", 0))
                    valor_acrescimos = float(servico.get("nValorAcrescimos", 0))
                    service_value = (quantidade * valor_unitario) - valor_desconto + valor_acrescimos
                    
                    # Contagem simples por tipo de serviço
                    service_types[service_type] = service_types.get(service_type, 0) + 1
                    
                    # Breakdown detalhado por serviço e status
                    if service_type not in service_breakdown:
                        service_breakdown[service_type] = {
                            'total_count': 0,
                            'total_value': 0,
                            'faturada': {'count': 0, 'value': 0},
                            'pendente': {'count': 0, 'value': 0},
                            'etapa_00': {'count': 0, 'value': 0}
                        }
                    
                    # Incrementar totais
                    service_breakdown[service_type]['total_count'] += 1
                    service_breakdown[service_type]['total_value'] += service_value
                    
                    # Classificar por status
                    if order_status == "60":  # Faturada
                        service_breakdown[service_type]['faturada']['count'] += 1
                        service_breakdown[service_type]['faturada']['value'] += service_value
                    elif order_status == "10":  # Pendente
                        service_breakdown[service_type]['pendente']['count'] += 1
                        service_breakdown[service_type]['pendente']['value'] += service_value
                    elif order_status == "00":  # Etapa 00
                        service_breakdown[service_type]['etapa_00']['count'] += 1
                        service_breakdown[service_type]['etapa_00']['value'] += service_value
            
            # Adicionar serviços cadastrados que não têm ordens (para mostrar todos os 16 serviços)
            for service_code, service_name in service_name_mapping.items():
                if service_name not in service_breakdown:
                    service_breakdown[service_name] = {
                        'total_count': 0,
                        'total_value': 0,
                        'faturada': {'count': 0, 'value': 0},
                        'pendente': {'count': 0, 'value': 0},
                        'etapa_00': {'count': 0, 'value': 0}
                    }
            
            # Debug: mostrar resumo do breakdown
            print(f"\nService Breakdown processado: {len(service_breakdown)} tipos de serviço")
            for service_name, data in service_breakdown.items():
                print(f"  {service_name}: Total={data['total_count']}, Faturada={data['faturada']['count']}, Pendente={data['pendente']['count']}, Etapa00={data['etapa_00']['count']}")
            
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
            
            # Buscar mapeamento de vendedores para usar nomes reais
            seller_name_mapping = self.get_seller_name_mapping()
            
            # Ordens por vendedor (usando nCodVend)
            sellers = {}
            for order in orders:
                cabecalho = order.get("Cabecalho", {})
                seller_code = cabecalho.get("nCodVend", "")
                if seller_code:
                    # Usar nome real do vendedor se disponível
                    seller_name = seller_name_mapping.get(seller_code, f"Vendedor {seller_code}")
                    sellers[seller_name] = sellers.get(seller_name, 0) + 1
            
            # Criar versão ordenada do service_breakdown por valor total (maior para menor)
            # Separar serviços cadastrados dos não cadastrados
            registered_service_names = set(service_name_mapping.values())
            
            # Serviços cadastrados ordenados por faturamento
            registered_services = {k: v for k, v in service_breakdown.items() if k in registered_service_names}
            service_breakdown_sorted = sorted(
                registered_services.items(), 
                key=lambda x: x[1]['total_value'], 
                reverse=True
            )
            
            # Serviços não cadastrados (como "Não informado")
            unregistered_services = {k: v for k, v in service_breakdown.items() if k not in registered_service_names}
            
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
                "monthly_values": monthly_values,
                "service_breakdown": service_breakdown,
                "service_breakdown_sorted": service_breakdown_sorted,
                "unregistered_services": unregistered_services
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
                "monthly_values": {},
                "service_breakdown": {},
                "service_breakdown_sorted": [],
                "unregistered_services": {}
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
    
    def get_available_weeks_for_services(self, fill_gaps: bool = True) -> List[dict]:
        """Retorna lista de semanas disponíveis para filtro de ordens de serviço
        
        Args:
            fill_gaps: Se True, preenche lacunas entre semanas para criar sequência contínua
        """
        try:
            # Verificar cache primeiro
            cache_key = self._get_cache_key("get_available_weeks_for_services", fill_gaps=fill_gaps)
            cached_data = self._get_from_cache(cache_key, use_mapping_expiry=True)
            if cached_data is not None:
                print(f"Semanas disponíveis carregadas do cache: {len(cached_data)} semanas")
                return cached_data
            
            # Buscar todas as ordens para ter lista completa de semanas
            orders = self.get_all_service_orders()
            weeks_with_orders = set()
            all_dates = []
            
            for order in orders:
                try:
                    cabecalho = order.get("Cabecalho", {})
                    date_str = cabecalho.get("dDtPrevisao", "")
                    if date_str and "/" in date_str:
                        # Converter data dd/mm/yyyy para datetime
                        parts = date_str.split("/")
                        if len(parts) == 3:
                            try:
                                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                                
                                # Validar se a data é válida
                                if 1 <= day <= 31 and 1 <= month <= 12 and year >= 2000:
                                    date_obj = datetime(year, month, day)
                                    all_dates.append(date_obj)
                                    
                                    # Calcular início da semana (segunda-feira)
                                    # weekday() retorna 0=segunda, 1=terça, ..., 6=domingo
                                    start_of_week = date_obj - timedelta(days=date_obj.weekday())
                                    end_of_week = start_of_week + timedelta(days=6)
                                    
                                    # Formato da semana: "YYYY-MM-DD_YYYY-MM-DD" (início_fim)
                                    week_key = f"{start_of_week.strftime('%Y-%m-%d')}_{end_of_week.strftime('%Y-%m-%d')}"
                                    weeks_with_orders.add(week_key)
                                else:
                                    print(f"Data inválida ignorada: {date_str}")
                            except ValueError as ve:
                                print(f"Erro ao converter data {date_str}: {ve}")
                except Exception as date_error:
                    # Log do erro específico mas continue processando
                    print(f"Erro ao processar data da ordem: {date_error}")
                    continue
            
            # Determinar conjunto final de semanas
            final_weeks_set = weeks_with_orders.copy()
            
            # Se fill_gaps está ativado, preencher lacunas
            if fill_gaps and all_dates:
                all_dates.sort()
                min_date = all_dates[0]
                max_date = all_dates[-1]
                
                # Calcular primeira e última semana
                first_week_start = min_date - timedelta(days=min_date.weekday())
                last_week_start = max_date - timedelta(days=max_date.weekday())
                
                # Gerar todas as semanas entre a primeira e a última
                current_week_start = first_week_start
                while current_week_start <= last_week_start:
                    current_week_end = current_week_start + timedelta(days=6)
                    week_key = f"{current_week_start.strftime('%Y-%m-%d')}_{current_week_end.strftime('%Y-%m-%d')}"
                    final_weeks_set.add(week_key)
                    current_week_start += timedelta(days=7)
                
                print(f"Preenchimento de lacunas: {len(weeks_with_orders)} semanas com ordens -> {len(final_weeks_set)} semanas totais")
            
            # Converter para lista e ordenar cronologicamente (mais recentes primeiro)
            def sort_week_key(week_key):
                try:
                    start_date_str = week_key.split("_")[0]
                    # Converter para datetime para garantir ordenação correta
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    return start_date
                except:
                    return datetime.min
            
            sorted_weeks = sorted(list(final_weeks_set), key=sort_week_key, reverse=True)
            
            # Converter para formato mais amigável
            result = []
            for week_key in sorted_weeks:
                try:
                    start_date_str, end_date_str = week_key.split("_")
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    
                    # Verificar se esta semana tem ordens
                    has_orders = week_key in weeks_with_orders
                    
                    # Formato amigável: "02/12 a 08/12/2024"
                    if start_date.year == end_date.year and start_date.month == end_date.month:
                        # Mesma semana, mesmo mês
                        label = f"{start_date.strftime('%d/%m')} a {end_date.strftime('%d/%m/%Y')}"
                    else:
                        # Semana que cruza meses
                        label = f"{start_date.strftime('%d/%m')} a {end_date.strftime('%d/%m/%Y')}"
                    
                    # Adicionar indicador visual para semanas sem ordens
                    if fill_gaps and not has_orders:
                        label += " (sem ordens)"
                    
                    result.append({
                        'value': week_key,
                        'label': label,
                        'start_date': start_date_str,
                        'end_date': end_date_str,
                        'has_orders': has_orders
                    })
                except Exception as format_error:
                    print(f"Erro ao formatar semana {week_key}: {format_error}")
                    result.append({
                        'value': week_key,
                        'label': week_key,
                        'start_date': '',
                        'end_date': '',
                        'has_orders': False
                    })
            
            # Armazenar no cache
            self._set_cache(cache_key, result)
            print(f"Semanas disponíveis processadas: {len(result)} semanas")
            
            # Debug: mostrar as primeiras 10 semanas para verificar ordenação
            if result:
                print("Primeiras 10 semanas (mais recentes):")
                for i, week in enumerate(result[:10]):
                    orders_indicator = "✓" if week.get('has_orders', True) else "○"
                    print(f"  {i+1}. {orders_indicator} {week['label']} ({week['value']})")
            
            return result
            
        except Exception as e:
            print(f"Erro ao buscar semanas disponíveis: {str(e)}")
            import traceback
            traceback.print_exc()
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
    
    def get_weekly_service_stats(self, week_filter: str) -> dict:
        """Retorna estatísticas das ordens de serviço para uma semana específica"""
        try:
            # Buscar todas as ordens para estatísticas precisas
            all_orders = self.get_all_service_orders()
            
            # Extrair datas de início e fim da semana
            start_date_str, end_date_str = week_filter.split("_")
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            
            # Filtrar ordens pela semana especificada
            filtered_orders = []
            for order in all_orders:
                cabecalho = order.get("Cabecalho", {})
                date_str = cabecalho.get("dDtPrevisao", "")
                if date_str:
                    try:
                        # Converter data dd/mm/yyyy para datetime
                        day, month, year = date_str.split("/")
                        order_date = datetime(int(year), int(month), int(day))
                        
                        # Verificar se a data está dentro da semana
                        if start_date <= order_date <= end_date:
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
            
            # Formatar o período da semana para exibição
            if start_date.year == end_date.year and start_date.month == end_date.month:
                formatted_week = f"{start_date.strftime('%d/%m')} a {end_date.strftime('%d/%m/%Y')}"
            else:
                formatted_week = f"{start_date.strftime('%d/%m')} a {end_date.strftime('%d/%m/%Y')}"
            
            return {
                "week_filter": week_filter,
                "formatted_week": formatted_week,
                "start_date": start_date_str,
                "end_date": end_date_str,
                "total_orders": total_orders,
                "total_value": total_value,
                "average_value": average_value,
                "unique_clients": unique_clients_count
            }
            
        except Exception as e:
            print(f"Erro ao calcular estatísticas semanais: {str(e)}")
            return {
                "week_filter": week_filter,
                "formatted_week": week_filter,
                "start_date": "",
                "end_date": "",
                "total_orders": 0,
                "total_value": 0,
                "average_value": 0,
                "unique_clients": 0
            }
    
    def filter_orders_by_date_range(self, start_date: str, end_date: str) -> List[dict]:
        """Filtra ordens de serviço por um período específico (formato YYYY-MM-DD)"""
        try:
            # Buscar todas as ordens
            all_orders = self.get_all_service_orders()
            
            # Converter datas de filtro
            start_filter = datetime.strptime(start_date, '%Y-%m-%d')
            end_filter = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Filtrar ordens pelo período especificado
            filtered_orders = []
            for order in all_orders:
                cabecalho = order.get("Cabecalho", {})
                date_str = cabecalho.get("dDtPrevisao", "")
                if date_str:
                    try:
                        # Converter data dd/mm/yyyy para datetime
                        day, month, year = date_str.split("/")
                        order_date = datetime(int(year), int(month), int(day))
                        
                        # Verificar se a data está dentro do período
                        if start_filter <= order_date <= end_filter:
                            filtered_orders.append(order)
                    except:
                        pass
            
            return filtered_orders
            
        except Exception as e:
            print(f"Erro ao filtrar ordens por período: {str(e)}")
            return []
    
    def get_current_week_key(self) -> str:
        """Retorna a chave da semana atual no formato usado pelos filtros"""
        try:
            today = datetime.now()
            # Calcular início da semana (segunda-feira)
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            
            # Formato da semana: "YYYY-MM-DD_YYYY-MM-DD"
            week_key = f"{start_of_week.strftime('%Y-%m-%d')}_{end_of_week.strftime('%Y-%m-%d')}"
            return week_key
            
        except Exception as e:
            print(f"Erro ao calcular semana atual: {str(e)}")
            return ""
    
    def load_full_data_background(self) -> dict:
        """Carrega todos os dados completos em background"""
        print("Iniciando carregamento completo de dados em background...")
        
        result = {
            'service_orders': [],
            'client_mapping': {},
            'seller_mapping': {},
            'loaded_at': time.time()
        }
        
        try:
            # Carregar ordens de serviço completas
            print("Carregando todas as ordens de serviço...")
            result['service_orders'] = self.get_all_service_orders(use_optimized_loading=True)
            print(f"Carregadas {len(result['service_orders'])} ordens de serviço")
            
            # Carregar mapeamento completo de clientes
            print("Carregando mapeamento completo de clientes...")
            result['client_mapping'] = self.get_client_name_mapping()
            print(f"Carregados {len(result['client_mapping'])} clientes")
            
            # Carregar mapeamento completo de vendedores
            print("Carregando mapeamento completo de vendedores...")
            result['seller_mapping'] = self.get_seller_name_mapping()
            print(f"Carregados {len(result['seller_mapping'])} vendedores")
            
            print("Carregamento completo de dados finalizado com sucesso!")
            return result
            
        except Exception as e:
            print(f"Erro no carregamento completo de dados: {str(e)}")
            raise e
    def get_services_page(self, page: int = 1, records_per_page: int = 20) -> dict:
        """Busca uma página de serviços cadastrados"""
        resource = "servicos/servico/"
        action = "ListarCadastroServico"
        
        params = {
            "nPagina": page,
            "nRegPorPagina": records_per_page
        }
        
        body = {
            "call": action,
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [params]
        }
        
        return self._make_request(resource, body)
    
    def get_all_services(self) -> List[dict]:
        """Busca todos os serviços cadastrados de todas as páginas"""
        # Verificar cache primeiro com tempo de vida estendido
        cache_key = self._get_cache_key("get_all_services")
        cached_data = self._get_from_cache(cache_key, use_mapping_expiry=True)
        if cached_data is not None:
            print(f"Serviços carregados do cache: {len(cached_data)} registros")
            return cached_data
        
        all_services = []
        page = 1
        
        try:
            # Primeira requisição para saber o total de páginas
            first_response = self.get_services_page(page)
            total_pages = first_response.get("total_de_paginas", 1)
            total_records = first_response.get("total_de_registros", 0)
            
            print(f"Carregando serviços: {total_pages} páginas, {total_records} registros")
            
            # Adiciona os serviços da primeira página
            services = first_response.get("cadastros", [])
            all_services.extend(services)
            
            # Busca as páginas restantes com timeout otimizado
            for page in range(2, total_pages + 1):
                try:
                    response = self.get_services_page(page)
                    services = response.get("cadastros", [])
                    all_services.extend(services)
                    
                    # Log de progresso a cada 10 páginas
                    if page % 10 == 0:
                        print(f"Progresso serviços: {page}/{total_pages} páginas ({len(all_services)} registros)")
                        
                except Exception as page_error:
                    print(f"Erro ao buscar página {page} de serviços: {str(page_error)}")
                    # Continue com as próximas páginas mesmo se uma falhar
                    continue
            
            print(f"Serviços carregados: {len(all_services)} registros de {total_pages} páginas")
            
            # Armazenar no cache
            self._set_cache(cache_key, all_services)
            return all_services
            
        except Exception as e:
            print(f"Erro ao buscar serviços: {str(e)}")
            return []
    
    def _map_service_description_to_registered(self, service_desc: str, service_name_mapping: Dict[int, str]) -> str:
        """Mapeia uma descrição de serviço para um serviço cadastrado usando lógica inteligente"""
        if not service_desc:
            return "Não informado"
        
        service_desc_clean = service_desc.strip()
        registered_names = list(service_name_mapping.values())
        
        # 1. Correspondência exata (case-insensitive)
        for reg_name in registered_names:
            if reg_name.lower() == service_desc_clean.lower():
                return reg_name
        
        # 2. Mapeamentos específicos conhecidos
        desc_lower = service_desc_clean.lower()
        
        # Mapeamentos para Be Master
        if any(keyword in desc_lower for keyword in ['be master', 'bemaster']):
            if 'parcial' in desc_lower:
                return "Be Master Parcial"
            elif 'renovação' in desc_lower or 'renovacao' in desc_lower:
                # Mapear "Renovação Be Master" para "Be Master" (serviço principal)
                return "Be Master"
            else:
                return "Be Master"
        
        # Mapeamentos para Imersão BLI
        if any(keyword in desc_lower for keyword in ['imersão bli', 'imersao bli', 'bli']):
            if 'almoço' in desc_lower or 'almoco' in desc_lower:
                return "Almoço Imersão BLI (Aplicação para o Be Master)"
            else:
                return "Imersão BLI"
        
        # Mapeamentos para BLA
        if 'bla' in desc_lower and ('advanced' in desc_lower or 'leader' in desc_lower):
            return "BLA (Be Leader Advanced)"
        
        # Mapeamentos para BLC
        if any(keyword in desc_lower for keyword in ['blc', 'be leader in company', 'consultoria de posicionamento']):
            return "BLC"
        
        # Mapeamentos para Escola de Vendedores
        if 'escola de vendedores' in desc_lower:
            return "Escola de Vendedores"
        
        # Mapeamentos para serviços genéricos
        if any(keyword in desc_lower for keyword in ['serviços prestados', 'servicos prestados']):
            if 'teste' in desc_lower:
                # Mapear para um serviço existente ou manter separado se necessário
                return "Serviços de produção de vídeos"  # ou outro serviço apropriado
            else:
                # Mapear serviços prestados genéricos para um serviço existente
                return "Serviços de produção de vídeos"  # ou outro serviço apropriado
        
        # Mapeamentos para BLP
        if 'blp' in desc_lower:
            return "BLC"  # Mapear BLP para BLC (serviço similar)
        
        # Mapeamentos para IPM
        if 'ipm' in desc_lower or 'imersão de posicionamento' in desc_lower:
            return "Imersão BLI"  # Mapear para serviço similar
        
        # 3. Correspondência parcial (contém palavras-chave)
        for reg_name in registered_names:
            reg_words = reg_name.lower().split()
            desc_words = service_desc_clean.lower().split()
            
            # Se pelo menos 50% das palavras do serviço registrado estão na descrição
            matching_words = sum(1 for word in reg_words if any(word in desc_word for desc_word in desc_words))
            if len(reg_words) > 0 and matching_words / len(reg_words) >= 0.5:
                return reg_name
        
        # 4. Se não encontrou correspondência, retornar a descrição original
        # mas com aviso de que não está cadastrado
        return f"⚠️ {service_desc_clean}"

    def get_service_name_mapping(self) -> Dict[int, str]:
        """Retorna um dicionário mapeando código do serviço para nome"""
        # Verificar cache primeiro com tempo de vida estendido
        cache_key = self._get_cache_key("get_service_name_mapping")
        cached_data = self._get_from_cache(cache_key, use_mapping_expiry=True)
        if cached_data is not None:
            print(f"Mapeamento de serviços carregado do cache: {len(cached_data)} serviços")
            return cached_data
        
        try:
            # Buscar todos os serviços para mapeamento completo
            services = self.get_all_services()
            mapping = {}
            
            for service in services:
                # Tentar diferentes estruturas para encontrar o c��digo do serviço
                service_code = None
                service_name = ""
                
                # Estrutura 1: intListar.nCodServ (estrutura atual)
                if "intListar" in service and "nCodServ" in service["intListar"]:
                    service_code = service["intListar"]["nCodServ"]
                    if "cabecalho" in service and "cDescricao" in service["cabecalho"]:
                        service_name = service["cabecalho"]["cDescricao"].strip()
                
                # Estrutura 2: nCodServ direto (conforme mencionado pelo usuário)
                elif "nCodServ" in service:
                    service_code = service["nCodServ"]
                    service_name = service.get("cDescricao", "").strip()
                
                # Estrutura 3: Outras possíveis estruturas
                elif "codigo" in service:
                    service_code = service["codigo"]
                    service_name = service.get("descricao", "").strip()
                
                # Se não encontrou nome, usar nome padrão
                if not service_name and service_code:
                    service_name = f"Serviço {service_code}"
                
                if service_code and service_name:
                    mapping[service_code] = service_name
            
            # Armazenar no cache
            self._set_cache(cache_key, mapping)
            print(f"Mapeamento de serviços criado: {len(mapping)} serviços")
            
            return mapping
            
        except Exception as e:
            print(f"Erro ao criar mapeamento de serviços: {str(e)}")
            return {}
