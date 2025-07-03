#!/usr/bin/env python3
"""
Teste para verificar se o filtro de serviços está funcionando corretamente
nas estatísticas do Dashboard de Serviços.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.omie_service import OmieService

def test_service_filter_fix():
    """Testa se o filtro de serviços está funcionando corretamente"""
    print("🧪 Testando correção do filtro de serviços...")
    
    # Inicializar serviço
    omie_service = OmieService()
    
    # 1. Buscar todas as ordens de serviço
    print("\n1. Carregando todas as ordens de serviço...")
    all_orders = omie_service.get_all_service_orders()
    print(f"   Total de ordens carregadas: {len(all_orders)}")
    
    # 2. Filtrar ordens por um serviço específico (simulando o que acontece no app.py)
    service_filter = "Imersão BLI"
    print(f"\n2. Filtrando ordens por serviço: '{service_filter}'")
    
    filtered_orders = []
    for order in all_orders:
        servicos = order.get("ServicosPrestados", [])
        if any(s.get('cDescServ', '').strip() == service_filter for s in servicos):
            filtered_orders.append(order)
    
    print(f"   Ordens filtradas: {len(filtered_orders)}")
    
    # 3. Testar estatísticas SEM filtro de serviço
    print("\n3. Testando estatísticas SEM filtro de serviço...")
    stats_without_filter = omie_service.get_service_orders_stats(orders=filtered_orders)
    service_breakdown_without = stats_without_filter.get('service_breakdown', {})
    print(f"   Serviços no breakdown: {len(service_breakdown_without)}")
    print(f"   Serviços: {list(service_breakdown_without.keys())}")
    
    # 4. Testar estatísticas COM filtro de serviço
    print("\n4. Testando estatísticas COM filtro de serviço...")
    stats_with_filter = omie_service.get_service_orders_stats(orders=filtered_orders, service_filter=service_filter)
    service_breakdown_with = stats_with_filter.get('service_breakdown', {})
    print(f"   Serviços no breakdown: {len(service_breakdown_with)}")
    print(f"   Serviços: {list(service_breakdown_with.keys())}")
    
    # 5. Verificar se a correção funcionou
    print("\n5. Verificando resultados...")
    
    # Sem filtro: deve mostrar todos os serviços cadastrados (16)
    expected_without_filter = 16
    if len(service_breakdown_without) == expected_without_filter:
        print(f"   ✅ SEM filtro: {len(service_breakdown_without)} serviços (esperado: {expected_without_filter})")
    else:
        print(f"   ❌ SEM filtro: {len(service_breakdown_without)} serviços (esperado: {expected_without_filter})")
    
    # Com filtro: deve mostrar apenas os serviços presentes nos dados filtrados
    services_in_filtered_data = set()
    for order in filtered_orders:
        servicos = order.get("ServicosPrestados", [])
        for servico in servicos:
            service_desc = servico.get("cDescServ", "").strip()
            if service_desc:
                services_in_filtered_data.add(service_desc)
    
    expected_with_filter = len(services_in_filtered_data)
    if len(service_breakdown_with) == expected_with_filter:
        print(f"   ✅ COM filtro: {len(service_breakdown_with)} serviços (esperado: {expected_with_filter})")
    else:
        print(f"   ❌ COM filtro: {len(service_breakdown_with)} serviços (esperado: {expected_with_filter})")
    
    # 6. Verificar se o serviço filtrado está presente
    if service_filter in service_breakdown_with:
        service_data = service_breakdown_with[service_filter]
        print(f"   ✅ Serviço '{service_filter}' encontrado com {service_data['total_count']} ordens")
    else:
        print(f"   ❌ Serviço '{service_filter}' não encontrado no breakdown")
    
    # 7. Resumo final
    print("\n📊 RESUMO DO TESTE:")
    print(f"   • Ordens totais: {len(all_orders)}")
    print(f"   • Ordens filtradas por '{service_filter}': {len(filtered_orders)}")
    print(f"   • Serviços sem filtro: {len(service_breakdown_without)}")
    print(f"   • Serviços com filtro: {len(service_breakdown_with)}")
    
    # Verificar se a correção foi bem-sucedida
    success = (
        len(service_breakdown_without) == expected_without_filter and
        len(service_breakdown_with) == expected_with_filter and
        service_filter in service_breakdown_with
    )
    
    if success:
        print("\n🎉 TESTE PASSOU! A correção do filtro de serviços está funcionando corretamente.")
    else:
        print("\n❌ TESTE FALHOU! Ainda há problemas com o filtro de serviços.")
    
    return success

if __name__ == "__main__":
    try:
        test_service_filter_fix()
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()