#!/usr/bin/env python3
"""
Teste abrangente para verificar se TODAS as seções de estatísticas 
estão sendo filtradas corretamente quando há filtros aplicados.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.omie_service import OmieService

def test_all_stats_sections():
    """Testa se todas as seções de estatísticas respeitam os filtros"""
    print("🧪 Testando TODAS as seções de estatísticas com filtros")
    
    # Inicializar serviço
    omie_service = OmieService()
    
    # 1. Buscar todas as ordens de serviço
    print("\n1. Carregando todas as ordens de serviço...")
    all_orders = omie_service.get_all_service_orders()
    print(f"   Total de ordens carregadas: {len(all_orders)}")
    
    # 2. Aplicar filtros (Julho 2025 + Imersão BLI)
    month_filter = "07/2025"
    service_filter = "Imersão BLI"
    
    print(f"\n2. Aplicando filtros: {month_filter} + {service_filter}")
    
    # Filtrar por mês
    filtered_orders = []
    for order in all_orders:
        cabecalho = order.get('Cabecalho', {})
        date_str = cabecalho.get('dDtPrevisao', '')
        if date_str:
            try:
                month_year = "/".join(date_str.split("/")[1:])
                if month_year == month_filter:
                    filtered_orders.append(order)
            except:
                pass
    
    # Filtrar por serviço
    if service_filter:
        service_filtered_orders = []
        for order in filtered_orders:
            servicos = order.get('ServicosPrestados', [])
            if any(s.get('cDescServ', '').strip() == service_filter for s in servicos):
                service_filtered_orders.append(order)
        filtered_orders = service_filtered_orders
    
    print(f"   Ordens após filtros: {len(filtered_orders)}")
    
    # 3. Calcular estatísticas com filtros
    print("\n3. Calculando estatísticas com filtros...")
    stats = omie_service.get_service_orders_stats(orders=filtered_orders, service_filter=service_filter)
    
    # 4. Analisar cada seção de estatísticas
    print("\n4. Analisando seções de estatísticas:")
    
    # 4.1 Service Breakdown
    service_breakdown = stats.get('service_breakdown', {})
    print(f"\n   📊 Service Breakdown:")
    print(f"      - Serviços no breakdown: {len(service_breakdown)}")
    for service_name, data in service_breakdown.items():
        if data['total_count'] > 0:
            print(f"        ✓ {service_name}: {data['total_count']} ordens")
    
    # 4.2 Top 5 Clientes
    top_clients = stats.get('top_clients', [])
    print(f"\n   👥 Top 5 Clientes:")
    print(f"      - Clientes listados: {len(top_clients)}")
    for client, count in top_clients:
        print(f"        ✓ {client}: {count} ordens")
    
    # 4.3 Top 5 Serviços
    top_services = stats.get('top_services', [])
    print(f"\n   🔧 Top 5 Serviços:")
    print(f"      - Serviços listados: {len(top_services)}")
    for service, count in top_services:
        print(f"        ✓ {service}: {count} ordens")
    
    # 4.4 Vendedores
    by_technician = stats.get('by_technician', {})
    print(f"\n   💼 Vendedores:")
    print(f"      - Vendedores listados: {len(by_technician)}")
    for seller, count in by_technician.items():
        print(f"        ✓ {seller}: {count} ordens")
    
    # 4.5 Estatísticas mensais
    monthly_stats = stats.get('monthly_stats', {})
    print(f"\n   📅 Estatísticas Mensais:")
    print(f"      - Meses com dados: {len(monthly_stats)}")
    for month, count in monthly_stats.items():
        print(f"        ✓ {month}: {count} ordens")
    
    # 4.6 Totais gerais
    print(f"\n   📈 Totais Gerais:")
    print(f"      - Total de ordens: {stats.get('total_orders', 0)}")
    print(f"      - Valor total: R$ {stats.get('total_value', 0):,.2f}")
    print(f"      - Ticket médio: R$ {stats.get('average_value', 0):,.2f}")
    
    # 5. Verificar se os dados estão consistentes com os filtros
    print("\n5. Verificação de consistência:")
    
    # 5.1 Verificar se apenas o serviço filtrado aparece no breakdown
    services_with_data = [name for name, data in service_breakdown.items() if data['total_count'] > 0]
    if len(services_with_data) == 1 and services_with_data[0] == service_filter:
        print(f"   ✅ Service Breakdown: Apenas '{service_filter}' com dados")
    else:
        print(f"   ❌ Service Breakdown: Múltiplos serviços com dados: {services_with_data}")
    
    # 5.2 Verificar se o total de ordens bate
    if stats.get('total_orders', 0) == len(filtered_orders):
        print(f"   ✅ Total de ordens: {stats.get('total_orders', 0)} (correto)")
    else:
        print(f"   ❌ Total de ordens: {stats.get('total_orders', 0)} (esperado: {len(filtered_orders)})")
    
    # 5.3 Verificar se apenas o mês filtrado aparece nas estatísticas mensais
    expected_month = month_filter
    if len(monthly_stats) == 1 and expected_month in monthly_stats:
        print(f"   ✅ Estatísticas mensais: Apenas '{expected_month}' com dados")
    elif len(monthly_stats) == 0:
        print(f"   ⚠️  Estatísticas mensais: Nenhum dado (pode ser normal se não há ordens faturadas)")
    else:
        print(f"   ❌ Estatísticas mensais: Múltiplos meses: {list(monthly_stats.keys())}")
    
    # 6. Verificar se há dados de ordens faturadas (etapa 60)
    faturadas_count = sum(1 for order in filtered_orders 
                         if order.get('Cabecalho', {}).get('cEtapa') == '60')
    print(f"\n6. Análise de status das ordens:")
    print(f"   - Total de ordens filtradas: {len(filtered_orders)}")
    print(f"   - Ordens faturadas (etapa 60): {faturadas_count}")
    print(f"   - Ordens não faturadas: {len(filtered_orders) - faturadas_count}")
    
    if faturadas_count == 0:
        print(f"   ⚠️  ATENÇÃO: Nenhuma ordem faturada encontrada!")
        print(f"      Isso pode explicar por que algumas estatísticas estão vazias.")
        
        # Mostrar status das ordens
        status_count = {}
        for order in filtered_orders:
            status = order.get('Cabecalho', {}).get('cEtapa', 'Desconhecido')
            status_count[status] = status_count.get(status, 0) + 1
        
        print(f"      Status das ordens filtradas:")
        for status, count in status_count.items():
            status_name = {
                "10": "Pendente",
                "20": "Em Andamento", 
                "30": "Aguardando Aprovação",
                "40": "Aprovada",
                "50": "Em Execução",
                "60": "Faturada",
                "70": "Cancelada"
            }.get(status, f"Etapa {status}")
            print(f"        - {status_name}: {count} ordens")
    
    return True

if __name__ == "__main__":
    try:
        test_all_stats_sections()
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()