#!/usr/bin/env python3
"""
Simula exatamente o que acontece quando o usuário acessa a página web
com os filtros Julho 2025 + Imersão BLI
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.omie_service import OmieService
from datetime import datetime

def simulate_web_request():
    """Simula exatamente o que acontece no app.py quando o usuário filtra"""
    print("🌐 Simulando requisição web: /services?month=07/2025&service=Imersão+BLI")
    
    # Simular parâmetros da requisição
    page = 1
    search = ""
    service_filter = "Imersão BLI"
    month_filter = "07/2025"
    week_filter = ""
    year_filter = ""
    per_page = 20
    
    print(f"\n📋 Parâmetros da requisição:")
    print(f"   - page: {page}")
    print(f"   - search: '{search}'")
    print(f"   - service_filter: '{service_filter}'")
    print(f"   - month_filter: '{month_filter}'")
    print(f"   - week_filter: '{week_filter}'")
    print(f"   - year_filter: '{year_filter}'")
    
    # Inicializar serviço (como no app.py)
    omie_service = OmieService()
    
    # Executar exatamente o mesmo código do app.py
    print(f"\n🔄 Executando lógica do app.py...")
    
    # Buscar ordens (como no app.py)
    print("Buscando ordens de serviço...")
    cache_key = omie_service._get_cache_key("get_all_service_orders", max_pages=None)
    cached_orders = omie_service._get_from_cache(cache_key, use_service_expiry=True)
    
    if cached_orders is not None:
        print(f"Dados carregados do cache: {len(cached_orders)} ordens")
        all_orders = cached_orders
    else:
        print("Cache vazio, carregando dados da API...")
        all_orders = omie_service.get_all_service_orders()
        print(f"Total de ordens carregadas da API: {len(all_orders)}")
    
    # Manter apenas ordens de serviço faturadas (como no app.py)
    all_orders = [o for o in all_orders if o.get('Cabecalho', {}).get('cEtapa') == '60']
    print(f"Ordens faturadas (etapa 60): {len(all_orders)}")
    
    # Aplicar filtros na mesma ordem do app.py
    
    # 1. Filtro de mês (como no app.py)
    if month_filter:
        print(f"\nAplicando filtro de mês: {month_filter}")
        filtered_orders = []
        for order in all_orders:
            cabecalho = order.get('Cabecalho', {})
            date_str = cabecalho.get('dDtPrevisao', '')
            if date_str:
                try:
                    month_year = "/".join(date_str.split("/")[1:])  # mm/yyyy
                    if month_year == month_filter:
                        filtered_orders.append(order)
                except:
                    pass
        all_orders = filtered_orders
        print(f"Ordens após filtro de mês: {len(all_orders)}")
    
    # 2. Filtro de serviço (como no app.py)
    if service_filter:
        print(f"\nAplicando filtro de serviço: {service_filter}")
        filtered_orders = []
        for order in all_orders:
            servicos = order.get('ServicosPrestados', [])
            if any(s.get('cDescServ', '').strip() == service_filter for s in servicos):
                filtered_orders.append(order)
        all_orders = filtered_orders
        print(f"Ordens após filtro de serviço: {len(all_orders)}")
    
    # 3. Buscar mapeamentos (como no app.py)
    print("\nBuscando mapeamentos...")
    try:
        client_name_mapping = omie_service.get_client_name_mapping()
        print(f"Mapeamento de clientes: {len(client_name_mapping)} clientes")
    except Exception as e:
        print(f"Erro ao carregar mapeamento de clientes: {str(e)}")
        client_name_mapping = {}
    
    try:
        seller_name_mapping = omie_service.get_seller_name_mapping()
        print(f"Mapeamento de vendedores: {len(seller_name_mapping)} vendedores")
    except Exception as e:
        print(f"Erro ao carregar mapeamento de vendedores: {str(e)}")
        seller_name_mapping = {}
    
    # 4. Calcular estatísticas (como no app.py)
    print("\nCalculando estatísticas...")
    try:
        stats = omie_service.get_service_orders_stats(orders=all_orders, service_filter=service_filter)
        
        # Adicionar informações sobre os filtros aplicados (como no app.py)
        stats['applied_filters'] = {
            'search': search,
            'service_filter': service_filter,
            'year_filter': year_filter,
            'month_filter': month_filter,
            'week_filter': week_filter,
            'total_filtered_orders': len(all_orders)
        }
        
        print(f"Estatísticas calculadas para {len(all_orders)} ordens filtradas")
        
    except Exception as e:
        print(f"Erro ao carregar estatísticas: {str(e)}")
        return False
    
    # 5. Analisar resultados que seriam enviados para o template
    print(f"\n📊 Resultados que seriam enviados para o template:")
    
    # Service Breakdown
    service_breakdown = stats.get('service_breakdown', {})
    print(f"\n🔧 Service Breakdown ({len(service_breakdown)} serviços):")
    for service_name, data in service_breakdown.items():
        if data['total_count'] > 0:
            print(f"   ✓ {service_name}: {data['total_count']} ordens, R$ {data['total_value']:,.2f}")
        else:
            print(f"   ○ {service_name}: 0 ordens")
    
    # Top Clients
    top_clients = stats.get('top_clients', [])
    print(f"\n👥 Top 5 Clientes ({len(top_clients)} clientes):")
    for client, count in top_clients:
        print(f"   ✓ {client}: {count} ordens")
    
    # Top Services
    top_services = stats.get('top_services', [])
    print(f"\n🏆 Top 5 Serviços ({len(top_services)} serviços):")
    for service, count in top_services:
        print(f"   ✓ {service}: {count} ordens")
    
    # Applied Filters
    applied_filters = stats.get('applied_filters', {})
    print(f"\n🎯 Filtros Aplicados:")
    print(f"   - service_filter: '{applied_filters.get('service_filter', '')}'")
    print(f"   - month_filter: '{applied_filters.get('month_filter', '')}'")
    print(f"   - total_filtered_orders: {applied_filters.get('total_filtered_orders', 0)}")
    
    # 6. Verificar se o problema está resolvido
    print(f"\n✅ Verificação Final:")
    
    # Verificar se apenas o serviço filtrado aparece com dados
    services_with_data = [name for name, data in service_breakdown.items() if data['total_count'] > 0]
    if len(services_with_data) == 1 and services_with_data[0] == service_filter:
        print(f"   ✅ Service Breakdown correto: apenas '{service_filter}' com dados")
        success = True
    else:
        print(f"   ❌ Service Breakdown incorreto: {services_with_data}")
        success = False
    
    # Verificar se os totais estão corretos
    if stats.get('total_orders', 0) == len(all_orders):
        print(f"   ✅ Total de ordens correto: {stats.get('total_orders', 0)}")
    else:
        print(f"   ❌ Total de ordens incorreto: {stats.get('total_orders', 0)} (esperado: {len(all_orders)})")
        success = False
    
    # Verificar se os filtros aplicados estão corretos
    if (applied_filters.get('service_filter') == service_filter and 
        applied_filters.get('month_filter') == month_filter):
        print(f"   ✅ Filtros aplicados corretos")
    else:
        print(f"   ❌ Filtros aplicados incorretos")
        success = False
    
    return success

if __name__ == "__main__":
    try:
        success = simulate_web_request()
        if success:
            print("\n🎉 SIMULAÇÃO PASSOU! O filtro está funcionando corretamente na aplicação.")
            print("\n💡 Se o usuário ainda vê o problema, pode ser:")
            print("   1. Cache do navegador - pressionar Ctrl+F5 para recarregar")
            print("   2. Cache da aplicação - usar o botão 'Limpar Cache' na interface")
            print("   3. Sessão antiga - fazer logout e login novamente")
        else:
            print("\n❌ SIMULAÇÃO FALHOU! Há um problema na aplicação.")
    except Exception as e:
        print(f"❌ Erro durante a simulação: {str(e)}")
        import traceback
        traceback.print_exc()