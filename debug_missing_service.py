#!/usr/bin/env python3
"""
Script para identificar qual serviço cadastrado está faltando no breakdown
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.omie_service import OmieService

def debug_missing_service():
    print("=== INVESTIGAÇÃO DO SERVIÇO FALTANTE ===")
    
    # Inicializar serviço
    omie_service = OmieService()
    
    # 1. Buscar serviços cadastrados
    print("\n1. SERVIÇOS CADASTRADOS (16):")
    service_mapping = omie_service.get_service_name_mapping()
    registered_services = set(service_mapping.values())
    
    for code, name in service_mapping.items():
        print(f"   {code}: {name}")
    
    print(f"\nTotal cadastrados: {len(registered_services)}")
    
    # 2. Buscar serviços no breakdown
    print("\n2. SERVIÇOS NO BREAKDOWN:")
    stats = omie_service.get_service_orders_stats()
    breakdown_services = set(stats['service_breakdown'].keys())
    
    for service_name in sorted(breakdown_services):
        count = stats['service_breakdown'][service_name]['total_count']
        value = stats['service_breakdown'][service_name]['total_value']
        print(f"   {service_name}: {count} OS | R$ {value:,.2f}")
    
    print(f"\nTotal no breakdown: {len(breakdown_services)}")
    
    # 3. Encontrar serviços cadastrados que não estão no breakdown
    print("\n3. SERVIÇOS CADASTRADOS QUE NÃO ESTÃO NO BREAKDOWN:")
    missing_services = registered_services - breakdown_services
    
    if missing_services:
        for service in missing_services:
            print(f"   ❌ FALTANDO: {service}")
    else:
        print("   ✅ Todos os serviços cadastrados estão no breakdown")
    
    # 4. Encontrar serviços no breakdown que não estão cadastrados
    print("\n4. SERVIÇOS NO BREAKDOWN QUE NÃO ESTÃO CADASTRADOS:")
    extra_services = breakdown_services - registered_services
    
    if extra_services:
        for service in extra_services:
            count = stats['service_breakdown'][service]['total_count']
            print(f"   ⚠️  EXTRA: {service} ({count} OS)")
    else:
        print("   ✅ Todos os serviços no breakdown estão cadastrados")
    
    # 5. Verificar se algum serviço cadastrado não tem ordens
    print("\n5. ANÁLISE DETALHADA:")
    print(f"   • Serviços cadastrados: {len(registered_services)}")
    print(f"   • Serviços no breakdown: {len(breakdown_services)}")
    print(f"   • Serviços faltantes: {len(missing_services)}")
    print(f"   • Serviços extras: {len(extra_services)}")
    
    # 6. Buscar ordens de serviço para verificar se o serviço faltante tem ordens
    if missing_services:
        print("\n6. VERIFICANDO ORDENS PARA SERVIÇOS FALTANTES:")
        orders = omie_service.get_all_service_orders()
        
        for missing_service in missing_services:
            print(f"\n   Procurando ordens para: {missing_service}")
            
            # Buscar por código do serviço
            service_code = None
            for code, name in service_mapping.items():
                if name == missing_service:
                    service_code = code
                    break
            
            if service_code:
                print(f"   Código do serviço: {service_code}")
                
                # Contar ordens com esse código
                orders_with_code = 0
                orders_with_desc = 0
                
                for order in orders:
                    servicos = order.get("ServicosPrestados", [])
                    for servico in servicos:
                        # Verificar por código
                        if servico.get("nCodServico") == service_code:
                            orders_with_code += 1
                        
                        # Verificar por descrição
                        desc = servico.get("cDescServ", "").strip()
                        if desc.lower() == missing_service.lower():
                            orders_with_desc += 1
                
                print(f"   Ordens encontradas por código: {orders_with_code}")
                print(f"   Ordens encontradas por descrição: {orders_with_desc}")
                
                if orders_with_code == 0 and orders_with_desc == 0:
                    print(f"   ✅ EXPLICAÇÃO: '{missing_service}' não tem ordens, por isso não aparece no breakdown")
                else:
                    print(f"   ❌ PROBLEMA: '{missing_service}' tem ordens mas não aparece no breakdown!")

if __name__ == "__main__":
    debug_missing_service()