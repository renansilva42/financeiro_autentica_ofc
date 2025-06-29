"""
Sistema de Carregamento Progressivo
Implementa carregamento de dados em etapas com feedback de progresso
"""

import asyncio
import time
from typing import Any, Dict, Optional, Callable, List
from datetime import datetime
from .omie_service import OmieService
from .cache_service import SupabaseCacheService

class ProgressiveDataLoader:
    """Carregador de dados progressivo com feedback em tempo real"""
    
    def __init__(self, omie_service: OmieService, cache_service: SupabaseCacheService):
        self.omie_service = omie_service
        self.cache_service = cache_service
        self.current_progress = 0
        self.current_message = ""
        self.is_loading = False
        self.start_time = None
        
    def _update_progress(self, percentage: int, message: str, callback: Optional[Callable] = None):
        """Atualiza progresso e chama callback se fornecido"""
        self.current_progress = percentage
        self.current_message = message
        
        if callback:
            callback(percentage, message)
        
        print(f"[{percentage:3d}%] {message}")
    
    async def load_dashboard_data(self, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Carrega dados do dashboard em etapas progressivas
        
        Args:
            progress_callback: Função para receber atualizações de progresso
            
        Returns:
            Dicionário com todos os dados carregados
        """
        self.is_loading = True
        self.start_time = time.time()
        
        try:
            # Etapa 1: Verificar cache existente (5%)
            self._update_progress(5, "Verificando cache existente...", progress_callback)
            
            # Verificar se há dados básicos em cache
            basic_cache_key = "dashboard_basic_data"
            cached_basic = await self.cache_service.get(basic_cache_key, "dashboard")
            
            # Etapa 2: Carregar mapeamentos essenciais (25%)
            self._update_progress(15, "Carregando mapeamentos de clientes...", progress_callback)
            
            client_mapping = await self._load_with_cache(
                "client_name_mapping",
                lambda: self.omie_service.get_client_name_mapping(),
                "mappings"
            )
            
            self._update_progress(25, "Carregando mapeamentos de vendedores...", progress_callback)
            
            seller_mapping = await self._load_with_cache(
                "seller_name_mapping", 
                lambda: self.omie_service.get_seller_name_mapping(),
                "mappings"
            )
            
            # Etapa 3: Carregar dados de serviços (60%)
            self._update_progress(35, "Carregando ordens de serviço...", progress_callback)
            
            service_orders = await self._load_service_orders_progressive(progress_callback)
            
            # Etapa 4: Calcular estatísticas básicas (80%)
            self._update_progress(70, "Calculando estatísticas básicas...", progress_callback)
            
            basic_stats = await self._calculate_basic_stats(service_orders, client_mapping)
            
            # Etapa 5: Preparar dados do dashboard (90%)
            self._update_progress(85, "Preparando dados do dashboard...", progress_callback)
            
            dashboard_data = await self._prepare_dashboard_data(
                service_orders, client_mapping, seller_mapping, basic_stats
            )
            
            # Etapa 6: Cache dos dados processados (95%)
            self._update_progress(95, "Salvando dados em cache...", progress_callback)
            
            # Salvar dados básicos em cache para próximas consultas
            await self.cache_service.set(
                basic_cache_key,
                {
                    'basic_stats': basic_stats,
                    'client_mapping': client_mapping,
                    'seller_mapping': seller_mapping,
                    'generated_at': datetime.now().isoformat()
                },
                "dashboard",
                0.5  # 30 minutos
            )
            
            # Etapa 7: Finalização (100%)
            self._update_progress(100, "Carregamento concluído!", progress_callback)
            
            elapsed_time = time.time() - self.start_time
            print(f"✅ Carregamento progressivo concluído em {elapsed_time:.2f} segundos")
            
            return {
                'service_orders': service_orders,
                'client_mapping': client_mapping,
                'seller_mapping': seller_mapping,
                'basic_stats': basic_stats,
                'dashboard_data': dashboard_data,
                'loading_time': elapsed_time,
                'total_records': len(service_orders)
            }
            
        except Exception as e:
            self._update_progress(-1, f"Erro no carregamento: {str(e)}", progress_callback)
            raise e
        finally:
            self.is_loading = False
    
    async def _load_with_cache(self, cache_key: str, loader_func: Callable, data_type: str) -> Any:
        """Carrega dados com verificação de cache"""
        # Tentar carregar do cache primeiro
        cached_data = await self.cache_service.get(cache_key, data_type)
        
        if cached_data is not None:
            print(f"📦 Dados carregados do cache: {cache_key}")
            return cached_data
        
        # Se não há cache, carregar da API
        print(f"🔄 Carregando da API: {cache_key}")
        data = loader_func()
        
        # Salvar no cache
        await self.cache_service.set(cache_key, data, data_type)
        
        return data
    
    async def _load_service_orders_progressive(self, progress_callback: Optional[Callable] = None) -> List[Dict]:
        """Carrega ordens de serviço com progresso detalhado"""
        cache_key = "all_service_orders"
        
        # Verificar cache primeiro
        cached_orders = await self.cache_service.get(cache_key, "service_orders")
        
        if cached_orders is not None:
            self._update_progress(60, f"Ordens carregadas do cache ({len(cached_orders)} registros)", progress_callback)
            return cached_orders
        
        # Carregar da API com progresso
        self._update_progress(40, "Iniciando carregamento de ordens de serviço...", progress_callback)
        
        # Simular progresso durante carregamento da API
        orders = []
        try:
            # Hook no método do omie_service para capturar progresso
            original_method = self.omie_service.get_all_service_orders
            
            def progress_hook(current_page, total_pages, current_records):
                if total_pages > 0:
                    page_progress = int(40 + (current_page / total_pages) * 20)  # 40% a 60%
                    self._update_progress(
                        page_progress, 
                        f"Carregando página {current_page}/{total_pages} ({current_records} registros)",
                        progress_callback
                    )
            
            # Carregar com hook de progresso se disponível
            if hasattr(self.omie_service, 'set_progress_callback'):
                self.omie_service.set_progress_callback(progress_hook)
            
            orders = original_method()
            
            # Salvar no cache
            await self.cache_service.set(cache_key, orders, "service_orders")
            
            self._update_progress(60, f"Ordens carregadas da API ({len(orders)} registros)", progress_callback)
            
        except Exception as e:
            self._update_progress(60, f"Erro ao carregar ordens: {str(e)}", progress_callback)
            # Tentar carregar dados básicos mesmo com erro
            orders = []
        
        return orders
    
    async def _calculate_basic_stats(self, service_orders: List[Dict], client_mapping: Dict) -> Dict[str, Any]:
        """Calcula estatísticas básicas dos dados"""
        if not service_orders:
            return {
                'total_orders': 0,
                'total_value': 0,
                'average_value': 0,
                'unique_clients': 0,
                'recent_orders': 0
            }
        
        total_orders = len(service_orders)
        total_value = 0
        unique_clients = set()
        recent_orders = 0
        
        # Data limite para ordens recentes (últimos 30 dias)
        thirty_days_ago = datetime.now().replace(day=1)  # Simplificado para o mês atual
        
        for order in service_orders:
            cabecalho = order.get('Cabecalho', {})
            
            # Valor total
            valor = cabecalho.get('nValorTotal', 0)
            if isinstance(valor, (int, float)):
                total_value += valor
            
            # Cliente único
            client_code = cabecalho.get('nCodCli', '')
            if client_code:
                unique_clients.add(client_code)
            
            # Ordens recentes (simplificado)
            date_str = cabecalho.get('dDtPrevisao', '')
            if date_str:
                try:
                    # Assumir que ordens com data são recentes para simplificar
                    recent_orders += 1
                except:
                    pass
        
        average_value = total_value / total_orders if total_orders > 0 else 0
        
        return {
            'total_orders': total_orders,
            'total_value': total_value,
            'average_value': average_value,
            'unique_clients': len(unique_clients),
            'recent_orders': recent_orders,
            'client_mapping_size': len(client_mapping)
        }
    
    async def _prepare_dashboard_data(self, service_orders: List[Dict], client_mapping: Dict, 
                                    seller_mapping: Dict, basic_stats: Dict) -> Dict[str, Any]:
        """Prepara dados específicos para o dashboard"""
        
        # Top clientes por número de ordens
        client_order_count = {}
        for order in service_orders[:100]:  # Limitar para performance
            client_code = order.get('Cabecalho', {}).get('nCodCli', '')
            if client_code:
                client_order_count[client_code] = client_order_count.get(client_code, 0) + 1
        
        top_clients = sorted(
            client_order_count.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        # Converter códigos para nomes
        top_clients_with_names = [
            {
                'code': code,
                'name': client_mapping.get(code, f'Cliente {code}'),
                'order_count': count
            }
            for code, count in top_clients
        ]
        
        # Estatísticas por mês (simplificado)
        monthly_stats = {}
        for order in service_orders[:200]:  # Limitar para performance
            date_str = order.get('Cabecalho', {}).get('dDtPrevisao', '')
            if date_str:
                try:
                    month_key = "/".join(date_str.split("/")[1:])  # mm/yyyy
                    if month_key not in monthly_stats:
                        monthly_stats[month_key] = {'count': 0, 'value': 0}
                    
                    monthly_stats[month_key]['count'] += 1
                    valor = order.get('Cabecalho', {}).get('nValorTotal', 0)
                    if isinstance(valor, (int, float)):
                        monthly_stats[month_key]['value'] += valor
                except:
                    pass
        
        return {
            'top_clients': top_clients_with_names,
            'monthly_stats': monthly_stats,
            'summary': basic_stats,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_current_status(self) -> Dict[str, Any]:
        """Retorna status atual do carregamento"""
        return {
            'is_loading': self.is_loading,
            'progress': self.current_progress,
            'message': self.current_message,
            'elapsed_time': time.time() - self.start_time if self.start_time else 0
        }

class LoadingStageManager:
    """Gerenciador de estágios de carregamento para interface"""
    
    def __init__(self):
        self.stages = [
            {'id': 'cache', 'name': 'Verificando Cache', 'progress': 0},
            {'id': 'mappings', 'name': 'Carregando Mapeamentos', 'progress': 0},
            {'id': 'services', 'name': 'Carregando Serviços', 'progress': 0},
            {'id': 'stats', 'name': 'Calculando Estatísticas', 'progress': 0},
            {'id': 'dashboard', 'name': 'Preparando Dashboard', 'progress': 0}
        ]
        self.current_stage = 0
    
    def update_stage_progress(self, overall_progress: int, message: str):
        """Atualiza progresso baseado no progresso geral"""
        # Mapear progresso geral para estágios
        if overall_progress <= 10:
            self.current_stage = 0
            self.stages[0]['progress'] = overall_progress * 10
        elif overall_progress <= 30:
            self.current_stage = 1
            self.stages[0]['progress'] = 100
            self.stages[1]['progress'] = (overall_progress - 10) * 5
        elif overall_progress <= 70:
            self.current_stage = 2
            self.stages[0]['progress'] = 100
            self.stages[1]['progress'] = 100
            self.stages[2]['progress'] = (overall_progress - 30) * 2.5
        elif overall_progress <= 90:
            self.current_stage = 3
            self.stages[0]['progress'] = 100
            self.stages[1]['progress'] = 100
            self.stages[2]['progress'] = 100
            self.stages[3]['progress'] = (overall_progress - 70) * 5
        else:
            self.current_stage = 4
            for i in range(4):
                self.stages[i]['progress'] = 100
            self.stages[4]['progress'] = (overall_progress - 90) * 10
    
    def get_stages_status(self) -> List[Dict[str, Any]]:
        """Retorna status de todos os estágios"""
        return self.stages.copy()
    
    def get_current_stage(self) -> Dict[str, Any]:
        """Retorna estágio atual"""
        if self.current_stage < len(self.stages):
            return self.stages[self.current_stage].copy()
        return self.stages[-1].copy()