#!/usr/bin/env python3
"""
Teste para verificar se todos os 16 serviços cadastrados estão no breakdown
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.omie_service import OmieService

def test_all_16_services():
    print("=== TESTE DOS 16 SERVIÇOS NO BREAKDOWN ===")
    
    # Inicializar serviço
    omie_service = OmieService()
    
    # Limpar cache para garantir dados frescos
    omie_service.clear_cache()
    print("Cache limpo")
    
    # 1. Buscar serviços cadastrados
    print("\n1. SERVIÇOS CADASTRADOS:")
    service_mapping = omie_service.get_service_name_mapping()
    registered_services = set(service_mapping.values())
    
    print(f"Total cadastrados: {len(registered_services)}")
    for code, name in service_mapping.items():
        print(f"   {code}: {name}")
    
    # 2. Buscar estatísticas com breakdown
    print("\n2. BREAKDOWN DE SERVIÇOS:")
    stats = omie_service.get_service_orders_stats()
    breakdown_services = set(stats['service_breakdown'].keys())
    
    print(f"Total no breakdown: {len(breakdown_services)}")
    
    # 3. Verificar se todos os 16 estão incluídos
    print("\n3. VERIFICAÇÃO DOS 16 SERVIÇOS:")
    
    missing_services = registered_services - breakdown_services
    if missing_services:
        print(f"❌ FALTANDO {len(missing_services)} serviços:")
        for service in missing_services:
            print(f"   - {service}")
    else:
        print("✅ TODOS OS 16 SERVIÇOS CADASTRADOS ESTÃO NO BREAKDOWN!")
    
    # 4. Mostrar breakdown ordenado por faturamento
    print("\n4. SERVIÇOS ORDENADOS POR FATURAMENTO:")
    if 'service_breakdown_sorted' in stats:
        for i, (service_name, service_data) in enumerate(stats['service_breakdown_sorted'], 1):
            total_count = service_data['total_count']
            total_value = service_data['total_value']
            
            if total_count == 0:
                status = "🔘 SEM ORDENS"
            else:
                status = f"📊 {total_count} OS"
            
            print(f"{i:2d}. {service_name}")
            print(f"     {status} | R$ {total_value:,.2f}")
    
    # 5. Verificar serviços sem ordens
    print("\n5. SERVIÇOS SEM ORDENS DE SERVIÇO:")
    services_without_orders = []
    for service_name, service_data in stats['service_breakdown'].items():
        if service_data['total_count'] == 0:
            services_without_orders.append(service_name)
    
    if services_without_orders:
        print(f"Encontrados {len(services_without_orders)} serviços sem ordens:")
        for service in services_without_orders:
            print(f"   🔘 {service}")
    else:
        print("Todos os serviços têm pelo menos uma ordem")
    
    # 6. Resumo final
    print(f"\n6. RESUMO FINAL:")
    print(f"   • Serviços cadastrados: {len(registered_services)}")
    print(f"   • Serviços no breakdown: {len(breakdown_services)}")
    print(f"   • Serviços com ordens: {len(breakdown_services) - len(services_without_orders)}")
    print(f"   • Serviços sem ordens: {len(services_without_orders)}")
    
    if len(breakdown_services) == 16:
        print("   ✅ SUCESSO: Todos os 16 serviços estão sendo exibidos!")
    else:
        print(f"   ❌ PROBLEMA: Esperado 16, encontrado {len(breakdown_services)}")

if __name__ == "__main__":
    test_all_16_services()