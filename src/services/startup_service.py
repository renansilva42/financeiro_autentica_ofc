import threading
import time
from typing import Optional
from .omie_service import OmieService

class StartupService:
    """Serviço para pré-carregar dados essenciais na inicialização"""
    
    def __init__(self, omie_service: OmieService):
        self.omie_service = omie_service
        self.preload_thread: Optional[threading.Thread] = None
        self.preload_status = {
            'started': False,
            'completed': False,
            'error': None,
            'progress': {}
        }
    
    def start_preload(self):
        """Inicia o pré-carregamento de dados em background"""
        if self.preload_thread and self.preload_thread.is_alive():
            print("Pré-carregamento já está em andamento")
            return
        
        self.preload_status = {
            'started': True,
            'completed': False,
            'error': None,
            'progress': {}
        }
        
        self.preload_thread = threading.Thread(target=self._preload_data, daemon=True)
        self.preload_thread.start()
        print("Pré-carregamento de dados iniciado em background")
    
    def _preload_data(self):
        """Executa o pré-carregamento de dados"""
        try:
            print("Iniciando pré-carregamento de dados essenciais...")
            
            # 1. Pré-carregar mapeamento de clientes (mais importante)
            print("Pré-carregando mapeamento de clientes...")
            self.preload_status['progress']['clients'] = 'loading'
            try:
                client_mapping = self.omie_service.get_client_name_mapping()
                self.preload_status['progress']['clients'] = f'completed ({len(client_mapping)} clientes)'
                print(f"Mapeamento de clientes pré-carregado: {len(client_mapping)} registros")
            except Exception as e:
                self.preload_status['progress']['clients'] = f'error: {str(e)}'
                print(f"Erro ao pré-carregar clientes: {e}")
            
            # 2. Pré-carregar mapeamento de vendedores
            print("Pré-carregando mapeamento de vendedores...")
            self.preload_status['progress']['sellers'] = 'loading'
            try:
                seller_mapping = self.omie_service.get_seller_name_mapping()
                self.preload_status['progress']['sellers'] = f'completed ({len(seller_mapping)} vendedores)'
                print(f"Mapeamento de vendedores pré-carregado: {len(seller_mapping)} registros")
            except Exception as e:
                self.preload_status['progress']['sellers'] = f'error: {str(e)}'
                print(f"Erro ao pré-carregar vendedores: {e}")
            
            # 3. Pré-carregar ordens de serviço (pode demorar mais)
            print("Pré-carregando ordens de serviço...")
            self.preload_status['progress']['service_orders'] = 'loading'
            try:
                service_orders = self.omie_service.get_all_service_orders()
                self.preload_status['progress']['service_orders'] = f'completed ({len(service_orders)} ordens)'
                print(f"Ordens de serviço pré-carregadas: {len(service_orders)} registros")
            except Exception as e:
                self.preload_status['progress']['service_orders'] = f'error: {str(e)}'
                print(f"Erro ao pré-carregar ordens de serviço: {e}")
            
            self.preload_status['completed'] = True
            print("Pré-carregamento de dados concluído com sucesso!")
            
        except Exception as e:
            self.preload_status['error'] = str(e)
            print(f"Erro no pré-carregamento: {e}")
    
    def get_status(self):
        """Retorna o status do pré-carregamento"""
        return self.preload_status.copy()
    
    def is_completed(self):
        """Verifica se o pré-carregamento foi concluído"""
        return self.preload_status.get('completed', False)
    
    def wait_for_completion(self, timeout: int = 300):
        """Aguarda a conclusão do pré-carregamento com timeout"""
        if not self.preload_thread:
            return False
        
        self.preload_thread.join(timeout=timeout)
        return self.is_completed()

# Instância global
startup_service: Optional[StartupService] = None

def initialize_startup_service(omie_service: OmieService):
    """Inicializa o serviço de startup"""
    global startup_service
    startup_service = StartupService(omie_service)
    return startup_service