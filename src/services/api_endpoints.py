"""
Endpoints API Otimizados para Carregamento Progressivo
Implementa endpoints específicos para diferentes tipos de carregamento
"""

from flask import Blueprint, jsonify, request, session
from typing import Dict, Any, Optional
import asyncio
import time
from datetime import datetime

from .omie_service import OmieService
from .cache_service import SupabaseCacheService
from .progressive_loader import ProgressiveDataLoader, LoadingStageManager
from utils.auth_decorators import login_required

# Blueprint para endpoints otimizados
optimized_api = Blueprint('optimized_api', __name__, url_prefix='/api/v2')

# Instâncias globais (serão inicializadas externamente)
omie_service: Optional[OmieService] = None
cache_service: Optional[SupabaseCacheService] = None
progressive_loader: Optional[ProgressiveDataLoader] = None

def initialize_services(omie_svc: OmieService, cache_svc: SupabaseCacheService):
    """Inicializa os serviços para os endpoints"""
    global omie_service, cache_service, progressive_loader
    
    omie_service = omie_svc
    cache_service = cache_svc
    progressive_loader = ProgressiveDataLoader(omie_service, cache_service)
    
    # Configurar cache inteligente no OmieService
    omie_service.set_intelligent_cache(cache_service)
    
    print("✅ Serviços otimizados inicializados")

@optimized_api.route('/dashboard/progressive', methods=['GET'])
@login_required
def api_dashboard_progressive():
    """Endpoint para carregamento progressivo do dashboard"""
    try:
        if not progressive_loader:
            return jsonify({'error': 'Serviços não inicializados'}), 500
        
        # Executar carregamento progressivo
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            data = loop.run_until_complete(progressive_loader.load_dashboard_data())
            return jsonify({
                'status': 'success',
                'data': data,
                'loaded_at': datetime.now().isoformat()
            })
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@optimized_api.route('/dashboard/status', methods=['GET'])
@login_required
def api_dashboard_status():
    """Endpoint para verificar status do carregamento progressivo"""
    try:
        if not progressive_loader:
            return jsonify({'error': 'Serviços não inicializados'}), 500
        
        status = progressive_loader.get_current_status()
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@optimized_api.route('/services/summary', methods=['GET'])
@login_required
def api_services_summary():
    """Endpoint otimizado para resumo de serviços"""
    try:
        if not cache_service:
            return jsonify({'error': 'Cache não disponível'}), 500
        
        # Buscar dados resumidos do cache
        cache_key = "services_summary_v2"
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            cached_data = loop.run_until_complete(
                cache_service.get(cache_key, "stats")
            )
            
            if cached_data:
                return jsonify({
                    'status': 'success',
                    'data': cached_data,
                    'from_cache': True,
                    'timestamp': datetime.now().isoformat()
                })
            
            # Calcular resumo otimizado
            summary = loop.run_until_complete(_calculate_services_summary())
            
            # Cache por 30 minutos
            loop.run_until_complete(
                cache_service.set(cache_key, summary, "stats", 0.5)
            )
            
            return jsonify({
                'status': 'success',
                'data': summary,
                'from_cache': False,
                'timestamp': datetime.now().isoformat()
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@optimized_api.route('/clients/mapping', methods=['GET'])
@login_required
def api_clients_mapping():
    """Endpoint otimizado para mapeamento de clientes"""
    try:
        if not cache_service or not omie_service:
            return jsonify({'error': 'Serviços não disponíveis'}), 500
        
        cache_key = "client_mapping_optimized"
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Tentar cache primeiro
            cached_mapping = loop.run_until_complete(
                cache_service.get(cache_key, "mappings")
            )
            
            if cached_mapping:
                return jsonify({
                    'status': 'success',
                    'mapping': cached_mapping,
                    'from_cache': True,
                    'count': len(cached_mapping),
                    'timestamp': datetime.now().isoformat()
                })
            
            # Carregar da API
            mapping = omie_service.get_client_name_mapping()
            
            # Salvar no cache
            loop.run_until_complete(
                cache_service.set(cache_key, mapping, "mappings")
            )
            
            return jsonify({
                'status': 'success',
                'mapping': mapping,
                'from_cache': False,
                'count': len(mapping),
                'timestamp': datetime.now().isoformat()
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@optimized_api.route('/sellers/mapping', methods=['GET'])
@login_required
def api_sellers_mapping():
    """Endpoint otimizado para mapeamento de vendedores"""
    try:
        if not cache_service or not omie_service:
            return jsonify({'error': 'Serviços não disponíveis'}), 500
        
        cache_key = "seller_mapping_optimized"
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Tentar cache primeiro
            cached_mapping = loop.run_until_complete(
                cache_service.get(cache_key, "mappings")
            )
            
            if cached_mapping:
                return jsonify({
                    'status': 'success',
                    'mapping': cached_mapping,
                    'from_cache': True,
                    'count': len(cached_mapping),
                    'timestamp': datetime.now().isoformat()
                })
            
            # Carregar da API
            mapping = omie_service.get_seller_name_mapping()
            
            # Salvar no cache
            loop.run_until_complete(
                cache_service.set(cache_key, mapping, "mappings")
            )
            
            return jsonify({
                'status': 'success',
                'mapping': mapping,
                'from_cache': False,
                'count': len(mapping),
                'timestamp': datetime.now().isoformat()
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@optimized_api.route('/services/paginated', methods=['GET'])
@login_required
def api_services_paginated():
    """Endpoint para carregamento paginado inteligente de serviços"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '', type=str)
        month_filter = request.args.get('month', '', type=str)
        week_filter = request.args.get('week', '', type=str)
        
        # Limitar per_page para evitar sobrecarga
        per_page = min(per_page, 100)
        
        if not omie_service:
            return jsonify({'error': 'Serviço não disponível'}), 500
        
        # Buscar dados com cache inteligente
        cache_key = f"services_paginated_{page}_{per_page}_{search}_{month_filter}_{week_filter}"
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Verificar cache primeiro
            if cache_service:
                cached_data = loop.run_until_complete(
                    cache_service.get(cache_key, "service_orders")
                )
                
                if cached_data:
                    return jsonify({
                        'status': 'success',
                        'data': cached_data,
                        'from_cache': True,
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Carregar dados da API (usar lógica existente otimizada)
            orders = omie_service.get_all_service_orders()
            
            # Aplicar filtros (lógica simplificada para exemplo)
            filtered_orders = orders
            
            # Paginação
            total = len(filtered_orders)
            start = (page - 1) * per_page
            end = start + per_page
            orders_page = filtered_orders[start:end]
            
            result = {
                'orders': orders_page,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': (total + per_page - 1) // per_page,
                    'has_prev': page > 1,
                    'has_next': page < (total + per_page - 1) // per_page
                }
            }
            
            # Salvar no cache por tempo curto
            if cache_service:
                loop.run_until_complete(
                    cache_service.set(cache_key, result, "service_orders", 0.25)  # 15 minutos
                )
            
            return jsonify({
                'status': 'success',
                'data': result,
                'from_cache': False,
                'timestamp': datetime.now().isoformat()
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@optimized_api.route('/cache/stats', methods=['GET'])
@login_required
def api_cache_stats():
    """Endpoint para estatísticas do cache"""
    try:
        if not cache_service:
            return jsonify({'error': 'Cache não disponível'}), 500
        
        stats = cache_service.get_cache_stats()
        
        return jsonify({
            'status': 'success',
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@optimized_api.route('/cache/clear', methods=['POST'])
@login_required
def api_cache_clear():
    """Endpoint para limpeza seletiva do cache"""
    try:
        if not cache_service:
            return jsonify({'error': 'Cache não disponível'}), 500
        
        data = request.get_json() or {}
        pattern = data.get('pattern')
        data_type = data.get('data_type')
        
        cache_service.clear_cache(pattern=pattern, data_type=data_type)
        
        return jsonify({
            'status': 'success',
            'message': 'Cache limpo com sucesso',
            'pattern': pattern,
            'data_type': data_type,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@optimized_api.route('/sync/status', methods=['GET'])
@login_required
def api_sync_status():
    """Endpoint para status de sincronização"""
    try:
        if not cache_service:
            return jsonify({'error': 'Cache não disponível'}), 500
        
        data_type = request.args.get('data_type')
        sync_status = cache_service.get_sync_status(data_type)
        
        return jsonify({
            'status': 'success',
            'sync_status': sync_status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

async def _calculate_services_summary() -> Dict[str, Any]:
    """Calcula resumo otimizado de serviços"""
    try:
        if not omie_service:
            return {}
        
        # Usar dados em cache se disponível
        orders = omie_service.get_all_service_orders()
        
        total_orders = len(orders)
        total_value = sum(
            float(order.get('Cabecalho', {}).get('nValorTotal', 0)) 
            for order in orders
        )
        
        # Estatísticas básicas
        summary = {
            'total_orders': total_orders,
            'total_value': total_value,
            'average_value': total_value / total_orders if total_orders > 0 else 0,
            'last_updated': datetime.now().isoformat()
        }
        
        return summary
        
    except Exception as e:
        print(f"Erro ao calcular resumo de serviços: {e}")
        return {
            'total_orders': 0,
            'total_value': 0,
            'average_value': 0,
            'last_updated': datetime.now().isoformat(),
            'error': str(e)
        }