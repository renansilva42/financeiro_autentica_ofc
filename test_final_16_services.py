#!/usr/bin/env python3
"""
Teste final para verificar se todos os 16 serviços cadastrados estão sendo exibidos
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.omie_service import OmieService

def test_final_16_services():
    print("=== TESTE FINAL DOS 16 SERVIÇOS CADASTRADOS ===")
    
    # Inicializar serviço
    omie_service = OmieService()
    
    # Limpar cache
    omie_service.clear_cache()
    
    # Buscar estatísticas
    stats = omie_service.get_service_orders_stats()
    
    print("✅ RESULTADO FINAL:")
    print()
    
    # 1. Verificar serviços cadastrados
    print("1. SERVIÇOS CADASTRADOS NO BREAKDOWN:")
    print(f"   Total: {len(stats['service_breakdown_sorted'])}")
    
    services_with_orders = 0
    services_without_orders = 0
    
    for i, (service_name, service_data) in enumerate(stats['service_breakdown_sorted'], 1):
        total_count = service_data['total_count']
        total_value = service_data['total_value']
        
        if total_count > 0:
            services_with_orders += 1
            status = f"📊 {total_count} OS"
        else:
            services_without_orders += 1
            status = "🔘 SEM ORDENS"
        
        print(f"   {i:2d}. {service_name}")
        print(f"       {status} | R$ {total_value:,.2f}")
    
    print()
    
    # 2. Verificar serviços não cadastrados
    print("2. SERVIÇOS NÃO CADASTRADOS:")
    if stats['unregistered_services']:
        print(f"   Total: {len(stats['unregistered_services'])}")
        for service_name, service_data in stats['unregistered_services'].items():
            print(f"   ⚠️  {service_name}: {service_data['total_count']} OS | R$ {service_data['total_value']:,.2f}")
    else:
        print("   ✅ Nenhum serviço não cadastrado")
    
    print()
    
    # 3. Resumo
    print("3. RESUMO:")
    print(f"   📋 Serviços cadastrados exibidos: {len(stats['service_breakdown_sorted'])}/16")
    print(f"   📊 Serviços com ordens: {services_with_orders}")
    print(f"   🔘 Serviços sem ordens: {services_without_orders}")
    print(f"   ⚠️  Serviços não cadastrados: {len(stats['unregistered_services'])}")
    
    # 4. Verificação final
    print()
    print("4. VERIFICAÇÃO FINAL:")
    if len(stats['service_breakdown_sorted']) == 16:
        print("   ✅ SUCESSO: Todos os 16 serviços cadastrados estão sendo exibidos!")
        print("   ✅ Serviços sem ordens também estão incluídos!")
        print("   ✅ Serviços não cadastrados estão separados!")
    else:
        print(f"   ❌ PROBLEMA: Esperado 16 serviços cadastrados, encontrado {len(stats['service_breakdown_sorted'])}")
    
    # 5. Serviços sem ordens (os que estavam faltando)
    if services_without_orders > 0:
        print()
        print("5. SERVIÇOS SEM ORDENS (que estavam faltando antes):")
        for service_name, service_data in stats['service_breakdown_sorted']:
            if service_data['total_count'] == 0:
                print(f"   🔘 {service_name} - Agora incluído no breakdown!")

if __name__ == "__main__":
    test_final_16_services()