#!/usr/bin/env python3
"""
Teste específico para verificar o filtro Julho 2025 + Imersão BLI
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.omie_service import OmieService
from datetime import datetime

def test_july_bli_filter():
    """Testa o filtro específico Julho 2025 + Imersão BLI"""
    print("🧪 Testando filtro: Julho 2025 + Imersão BLI")
    
    # Inicializar serviço
    omie_service = OmieService()
    
    # 1. Buscar todas as ordens de serviço
    print("\n1. Carregando todas as ordens de serviço...")
    all_orders = omie_service.get_all_service_orders()
    print(f"   Total de ordens carregadas: {len(all_orders)}")
    
    # 2. Simular exatamente o que acontece no app.py
    month_filter = "07/2025"
    service_filter = "Imersão BLI"
    
    print(f"\n2. Aplicando filtros:")
    print(f"   - Mês: {month_filter}")
    print(f"   - Serviço: {service_filter}")
    
    # Filtrar por mês primeiro (como no app.py)
    print("\n3. Filtrando por mês...")
    filtered_orders = []
    for order in all_orders:
        cabecalho = order.get('Cabecalho', {})
        date_str = cabecalho.get('dDtPrevisao', '')
        if date_str:
            try:
                # Extrair mês/ano da data (formato dd/mm/yyyy)
                month_year = "/".join(date_str.split("/")[1:])  # mm/yyyy
                if month_year == month_filter:
                    filtered_orders.append(order)
            except:
                pass
    
    print(f"   Ordens após filtro de mês: {len(filtered_orders)}")
    
    # Filtrar por serviço (como no app.py)
    print("\n4. Filtrando por serviço...")
    if service_filter:
        service_filtered_orders = []
        for order in filtered_orders:
            servicos = order.get('ServicosPrestados', [])
            if any(s.get('cDescServ', '').strip() == service_filter for s in servicos):
                service_filtered_orders.append(order)
        filtered_orders = service_filtered_orders
    
    print(f"   Ordens após filtro de serviço: {len(filtered_orders)}")
    
    # 5. Verificar quais serviços estão presentes nos dados filtrados
    print("\n5. Analisando serviços presentes nos dados filtrados...")
    services_in_data = set()
    for order in filtered_orders:
        servicos = order.get('ServicosPrestados', [])
        for servico in servicos:
            service_desc = servico.get('cDescServ', '').strip()
            if service_desc:
                services_in_data.add(service_desc)
    
    print(f"   Serviços únicos nos dados filtrados: {len(services_in_data)}")
    for service in sorted(services_in_data):
        print(f"     - {service}")
    
    # 6. Calcular estatísticas SEM passar o service_filter
    print("\n6. Calculando estatísticas SEM service_filter...")
    stats_without = omie_service.get_service_orders_stats(orders=filtered_orders)
    breakdown_without = stats_without.get('service_breakdown', {})
    print(f"   Serviços no breakdown: {len(breakdown_without)}")
    
    # 7. Calcular estatísticas COM service_filter
    print("\n7. Calculando estatísticas COM service_filter...")
    stats_with = omie_service.get_service_orders_stats(orders=filtered_orders, service_filter=service_filter)
    breakdown_with = stats_with.get('service_breakdown', {})
    print(f"   Serviços no breakdown: {len(breakdown_with)}")
    
    # 8. Comparar resultados
    print("\n8. Comparando resultados...")
    print(f"   SEM service_filter: {list(breakdown_without.keys())}")
    print(f"   COM service_filter: {list(breakdown_with.keys())}")
    
    # 9. Verificar se o problema persiste
    print("\n9. Verificação do problema...")
    
    # O problema é que mesmo com service_filter, ainda mostra todos os serviços?
    if len(breakdown_with) > len(services_in_data):
        print(f"   ❌ PROBLEMA CONFIRMADO!")
        print(f"      - Serviços nos dados: {len(services_in_data)}")
        print(f"      - Serviços no breakdown: {len(breakdown_with)}")
        print(f"      - Diferença: {len(breakdown_with) - len(services_in_data)} serviços extras")
        
        # Mostrar quais serviços extras estão sendo incluídos
        extra_services = set(breakdown_with.keys()) - services_in_data
        if extra_services:
            print(f"      - Serviços extras: {list(extra_services)}")
    else:
        print(f"   ✅ Problema resolvido!")
        print(f"      - Serviços nos dados: {len(services_in_data)}")
        print(f"      - Serviços no breakdown: {len(breakdown_with)}")
    
    # 10. Verificar dados específicos do serviço filtrado
    if service_filter in breakdown_with:
        service_data = breakdown_with[service_filter]
        print(f"\n10. Dados do serviço '{service_filter}':")
        print(f"    - Total de ordens: {service_data['total_count']}")
        print(f"    - Valor total: R$ {service_data['total_value']:,.2f}")
        print(f"    - Faturadas: {service_data['faturada']['count']}")
        print(f"    - Pendentes: {service_data['pendente']['count']}")
        print(f"    - Etapa 00: {service_data['etapa_00']['count']}")
    
    return len(breakdown_with) == len(services_in_data)

if __name__ == "__main__":
    try:
        success = test_july_bli_filter()
        if success:
            print("\n🎉 TESTE PASSOU! O filtro está funcionando corretamente.")
        else:
            print("\n❌ TESTE FALHOU! O problema ainda persiste.")
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()