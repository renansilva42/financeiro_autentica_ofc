"""
Sistema de Cache Inteligente com Supabase
Implementa cache persistente com diferentes TTLs baseados no tipo de dados
"""

import json
import gzip
import base64
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

class SupabaseCacheService:
    """Serviço de cache inteligente usando Supabase como backend persistente"""
    
    def __init__(self):
        """Inicializa o serviço de cache com conexão Supabase"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise Exception("Variáveis SUPABASE_URL e SUPABASE_KEY são obrigatórias")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        self.local_cache: Dict[str, tuple] = {}  # Cache em memória para dados frequentes
        
        # TTLs configuráveis por tipo de dados (em horas)
        self.ttl_config = {
            'clients': 24,          # Clientes: 24 horas
            'sellers': 24,          # Vendedores: 24 horas  
            'services': 12,         # Serviços: 12 horas
            'service_orders': 2,    # Ordens de serviço: 2 horas
            'mappings': 6,          # Mapeamentos: 6 horas
            'stats': 1,             # Estatísticas: 1 hora
            'dashboard': 0.5,       # Dashboard: 30 minutos
            'default': 1            # Padrão: 1 hora
        }
    
    def _compress_data(self, data: Any) -> str:
        """Comprime dados usando gzip e base64"""
        try:
            json_str = json.dumps(data, ensure_ascii=False)
            compressed = gzip.compress(json_str.encode('utf-8'))
            return base64.b64encode(compressed).decode('ascii')
        except Exception as e:
            print(f"Erro ao comprimir dados: {e}")
            return json.dumps(data, ensure_ascii=False)
    
    def _decompress_data(self, compressed_data: str, is_compressed: bool = True) -> Any:
        """Descomprime dados de gzip+base64"""
        try:
            if not is_compressed:
                return json.loads(compressed_data)
            
            compressed_bytes = base64.b64decode(compressed_data.encode('ascii'))
            decompressed = gzip.decompress(compressed_bytes)
            return json.loads(decompressed.decode('utf-8'))
        except Exception as e:
            print(f"Erro ao descomprimir dados: {e}")
            # Fallback para dados não comprimidos
            try:
                return json.loads(compressed_data)
            except:
                return None
    
    def _get_ttl_hours(self, data_type: str) -> float:
        """Retorna TTL em horas baseado no tipo de dados"""
        return self.ttl_config.get(data_type, self.ttl_config['default'])
    
    async def get(self, key: str, data_type: str = 'default') -> Optional[Any]:
        """
        Recupera dados do cache
        
        Args:
            key: Chave do cache
            data_type: Tipo de dados para determinar TTL
            
        Returns:
            Dados do cache ou None se não encontrado/expirado
        """
        try:
            # 1. Verificar cache local primeiro (mais rápido)
            if key in self.local_cache:
                data, expires_at = self.local_cache[key]
                if datetime.now() < expires_at:
                    return data
                else:
                    # Remove entrada expirada do cache local
                    del self.local_cache[key]
            
            # 2. Verificar cache no Supabase
            result = self.supabase.table('cache_data').select('*').eq('cache_key', key).execute()
            
            if result.data and len(result.data) > 0:
                cache_entry = result.data[0]
                expires_at = datetime.fromisoformat(cache_entry['expires_at'].replace('Z', '+00:00'))
                
                if datetime.now() < expires_at.replace(tzinfo=None):
                    # Dados ainda válidos
                    data = self._decompress_data(
                        cache_entry['data'], 
                        cache_entry.get('compressed', False)
                    )
                    
                    if data is not None:
                        # Adicionar ao cache local para próximas consultas
                        self.local_cache[key] = (data, expires_at.replace(tzinfo=None))
                        return data
                else:
                    # Dados expirados - remover do Supabase
                    self.supabase.table('cache_data').delete().eq('cache_key', key).execute()
            
            return None
            
        except Exception as e:
            print(f"Erro ao recuperar do cache {key}: {e}")
            return None
    
    async def set(self, key: str, data: Any, data_type: str = 'default', 
                  ttl_hours: Optional[float] = None) -> bool:
        """
        Armazena dados no cache
        
        Args:
            key: Chave do cache
            data: Dados para armazenar
            data_type: Tipo de dados para determinar TTL
            ttl_hours: TTL customizado em horas (opcional)
            
        Returns:
            True se armazenado com sucesso
        """
        try:
            # Determinar TTL
            if ttl_hours is None:
                ttl_hours = self._get_ttl_hours(data_type)
            
            expires_at = datetime.now() + timedelta(hours=ttl_hours)
            
            # Comprimir dados se forem grandes
            data_size = len(json.dumps(data, ensure_ascii=False))
            should_compress = data_size > 1024  # Comprimir se > 1KB
            
            if should_compress:
                compressed_data = self._compress_data(data)
            else:
                compressed_data = json.dumps(data, ensure_ascii=False)
            
            # Salvar no Supabase
            cache_record = {
                'cache_key': key,
                'data': compressed_data,
                'expires_at': expires_at.isoformat(),
                'data_type': data_type,
                'compressed': should_compress,
                'updated_at': datetime.now().isoformat()
            }
            
            # Usar upsert para inserir ou atualizar
            self.supabase.table('cache_data').upsert(cache_record).execute()
            
            # Salvar no cache local também
            self.local_cache[key] = (data, expires_at)
            
            print(f"Cache armazenado: {key} ({data_type}, TTL: {ttl_hours}h, Comprimido: {should_compress})")
            return True
            
        except Exception as e:
            print(f"Erro ao armazenar no cache {key}: {e}")
            return False
    
    def clear_cache(self, pattern: Optional[str] = None, data_type: Optional[str] = None):
        """
        Limpa cache baseado em padrão ou tipo de dados
        
        Args:
            pattern: Padrão para filtrar chaves (opcional)
            data_type: Tipo de dados para filtrar (opcional)
        """
        try:
            # Limpar cache local
            if pattern:
                keys_to_remove = [key for key in self.local_cache.keys() if pattern in key]
                for key in keys_to_remove:
                    del self.local_cache[key]
            elif data_type:
                # Para cache local, não temos info de data_type, então limpar tudo
                self.local_cache.clear()
            else:
                self.local_cache.clear()
            
            # Limpar cache no Supabase
            query = self.supabase.table('cache_data')
            
            if pattern and data_type:
                # Filtrar por ambos (Supabase não suporta LIKE diretamente, usar RPC se necessário)
                result = query.select('cache_key').eq('data_type', data_type).execute()
                keys_to_delete = [
                    row['cache_key'] for row in result.data 
                    if pattern in row['cache_key']
                ]
            elif pattern:
                # Buscar todas as chaves e filtrar localmente
                result = query.select('cache_key').execute()
                keys_to_delete = [
                    row['cache_key'] for row in result.data 
                    if pattern in row['cache_key']
                ]
            elif data_type:
                # Filtrar apenas por tipo
                result = query.select('cache_key').eq('data_type', data_type).execute()
                keys_to_delete = [row['cache_key'] for row in result.data]
            else:
                # Limpar tudo
                query.delete().neq('cache_key', '').execute()
                print("Cache completo limpo")
                return
            
            # Deletar chaves específicas
            for key in keys_to_delete:
                query.delete().eq('cache_key', key).execute()
            
            print(f"Cache limpo: {len(keys_to_delete)} entradas removidas")
            
        except Exception as e:
            print(f"Erro ao limpar cache: {e}")
    
    def clear_expired(self):
        """Remove entradas expiradas do cache"""
        try:
            now = datetime.now().isoformat()
            
            # Limpar cache local
            expired_keys = [
                key for key, (_, expires_at) in self.local_cache.items()
                if datetime.now() >= expires_at
            ]
            for key in expired_keys:
                del self.local_cache[key]
            
            # Limpar cache no Supabase
            result = self.supabase.table('cache_data').delete().lt('expires_at', now).execute()
            
            print(f"Cache expirado limpo: {len(expired_keys)} local, {len(result.data) if result.data else 0} Supabase")
            
        except Exception as e:
            print(f"Erro ao limpar cache expirado: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        try:
            # Stats do cache local
            local_count = len(self.local_cache)
            
            # Stats do Supabase
            result = self.supabase.table('cache_data').select('data_type', count='exact').execute()
            supabase_count = result.count if hasattr(result, 'count') else 0
            
            # Stats por tipo de dados
            type_stats = {}
            if result.data:
                for row in result.data:
                    data_type = row.get('data_type', 'unknown')
                    type_stats[data_type] = type_stats.get(data_type, 0) + 1
            
            return {
                'local_cache_entries': local_count,
                'supabase_cache_entries': supabase_count,
                'cache_by_type': type_stats,
                'ttl_config': self.ttl_config
            }
            
        except Exception as e:
            print(f"Erro ao obter estatísticas do cache: {e}")
            return {
                'local_cache_entries': len(self.local_cache),
                'supabase_cache_entries': 0,
                'cache_by_type': {},
                'ttl_config': self.ttl_config
            }
    
    def update_sync_status(self, data_type: str, status: str, records_count: int = 0, 
                          error_message: Optional[str] = None):
        """
        Atualiza status de sincronização de dados
        
        Args:
            data_type: Tipo de dados sincronizados
            status: Status da sincronização ('success', 'error', 'in_progress')
            records_count: Número de registros processados
            error_message: Mensagem de erro (se houver)
        """
        try:
            sync_record = {
                'data_type': data_type,
                'last_sync': datetime.now().isoformat(),
                'status': status,
                'records_count': records_count,
                'error_message': error_message
            }
            
            # Usar upsert para inserir ou atualizar
            self.supabase.table('sync_status').upsert(sync_record).execute()
            
            print(f"Status de sincronização atualizado: {data_type} - {status}")
            
        except Exception as e:
            print(f"Erro ao atualizar status de sincronização: {e}")
    
    def get_sync_status(self, data_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Recupera status de sincronização
        
        Args:
            data_type: Tipo específico de dados (opcional)
            
        Returns:
            Lista com status de sincronização
        """
        try:
            query = self.supabase.table('sync_status').select('*')
            
            if data_type:
                query = query.eq('data_type', data_type)
            
            result = query.order('last_sync', desc=True).execute()
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Erro ao recuperar status de sincronização: {e}")
            return []