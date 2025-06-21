import requests
import json
from typing import Dict, List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
    
    def get_all_service_orders(self) -> List[dict]:
        """Busca todas as ordens de serviço de todas as páginas"""
        all_orders = []
        page = 1
        
        try:
            # Primeira requisição para saber o total de páginas
            first_response = self.get_service_orders_page(page)
            total_pages = first_response.get("total_de_paginas", 1)
            
            # Adiciona as ordens da primeira página - corrigindo o nome do campo
            orders = first_response.get("osCadastro", [])
            all_orders.extend(orders)
            
            # Busca as páginas restantes
            for page in range(2, total_pages + 1):
                response = self.get_service_orders_page(page)
                orders = response.get("osCadastro", [])
                all_orders.extend(orders)
            
            return all_orders
            
        except Exception as e:
            print(f"Erro ao buscar ordens de serviço: {str(e)}")
            return []
    
    def get_service_orders_stats(self) -> dict:
        """Retorna estatísticas das ordens de serviço"""
        try:
            orders = self.get_all_service_orders()
            
            total_orders = len(orders)
            
            # Calcular valor total - a estrutura é diferente
            total_value = 0
            for order in orders:
                cabecalho = order.get("Cabecalho", {})
                total_value += float(cabecalho.get("nValorTotal", 0))
            
            # Contagem por cliente - precisamos buscar o nome do cliente via código
            clients = {}
            for order in orders:
                cabecalho = order.get("Cabecalho", {})
                client_code = cabecalho.get("nCodCli", "")
                # Por enquanto, usar o código do cliente como identificador
                client_name = f"Cliente {client_code}" if client_code else "Não informado"
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