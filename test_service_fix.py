#!/usr/bin/env python3
"""
Script para testar se o fix do mapeamento de serviços está funcionando
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.omie_service import OmieService

def test_service_fix():
    print("=== TESTE DO FIX DE MAPEAMENTO DE SERVIÇOS ===")
    
    # Inicializar serviço
    omie_service = OmieService()
    
    # Limpar cache para garantir dados frescos
    omie_service.clear_cache()
    print("Cache limpo")
    
    # Testar estatísticas de serviços
    print("\nTestando estatísticas de serviços...")
    try:
        stats = omie_service.get_service_orders_stats()
        
        print(f"Total de ordens: {stats['total_orders']}")
        print(f"Valor total: R$ {stats['total_value']:,.2f}")
        
        print(f"\nService breakdown encontrado: {len(stats['service_breakdown'])} tipos")
        
        # Verificar especificamente o serviço "Imersão BLI"
        if "Imersão BLI" in stats['service_breakdown']:
            bli_data = stats['service_breakdown']["Imersão BLI"]
            print(f"\n✅ IMERSÃO BLI ENCONTRADA:")
            print(f"  Total: {bli_data['total_count']}")
            print(f"  Faturada: {bli_data['faturada']['count']}")
            print(f"  Pendente: {bli_data['pendente']['count']}")
            print(f"  Etapa 00: {bli_data['etapa_00']['count']}")
            
            if bli_data['pendente']['count'] > 0:
                print(f"  ✅ PROBLEMA RESOLVIDO: {bli_data['pendente']['count']} pendentes encontrados!")
            else:
                print(f"  ❌ Ainda mostra 0 pendentes")
        else:
            print(f"\n❌ IMERSÃO BLI NÃO ENCONTRADA no breakdown")
            print("Serviços encontrados:")
            for service_name in stats['service_breakdown'].keys():
                print(f"  - {service_name}")
        
        # Mostrar todos os serviços com pendentes
        print(f"\nServiços com ordens pendentes:")
        for service_name, data in stats['service_breakdown'].items():
            if data['pendente']['count'] > 0:
                print(f"  {service_name}: {data['pendente']['count']} pendentes")
        
    except Exception as e:
        print(f"Erro ao testar estatísticas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_service_fix()