#!/usr/bin/env python3
"""
Script para testar as melhorias no breakdown de serviços
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.omie_service import OmieService

def test_breakdown_improvements():
    print("=== TESTE DAS MELHORIAS NO BREAKDOWN ===")
    
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
        
        # Verificar se service_breakdown_sorted existe
        if 'service_breakdown_sorted' in stats:
            print(f"\n✅ service_breakdown_sorted criado com {len(stats['service_breakdown_sorted'])} serviços")
            
            print("\nServiços ordenados por faturamento (maior para menor):")
            for i, (service_name, service_data) in enumerate(stats['service_breakdown_sorted'][:10], 1):
                print(f"{i:2d}. {service_name}")
                print(f"     Total: {service_data['total_count']} OS | Valor: R$ {service_data['total_value']:,.2f}")
                print(f"     Faturada: {service_data['faturada']['count']} | Pendente: {service_data['pendente']['count']} | Etapa 00: {service_data['etapa_00']['count']}")
                print()
        else:
            print("❌ service_breakdown_sorted não encontrado")
        
        # Calcular totais para verificar o container de totais
        print("\nTotais consolidados (para o container):")
        total_all = sum(data['total_count'] for data in stats['service_breakdown'].values())
        total_faturada = sum(data['faturada']['count'] for data in stats['service_breakdown'].values())
        total_pendente = sum(data['pendente']['count'] for data in stats['service_breakdown'].values())
        total_etapa00 = sum(data['etapa_00']['count'] for data in stats['service_breakdown'].values())
        
        valor_total_all = sum(data['total_value'] for data in stats['service_breakdown'].values())
        valor_faturada = sum(data['faturada']['value'] for data in stats['service_breakdown'].values())
        valor_pendente = sum(data['pendente']['value'] for data in stats['service_breakdown'].values())
        valor_etapa00 = sum(data['etapa_00']['value'] for data in stats['service_breakdown'].values())
        
        print(f"Total de OS: {total_all} | Valor: R$ {valor_total_all:,.2f}")
        print(f"Faturadas: {total_faturada} | Valor: R$ {valor_faturada:,.2f}")
        print(f"Pendentes: {total_pendente} | Valor: R$ {valor_pendente:,.2f}")
        print(f"Etapa 00: {total_etapa00} | Valor: R$ {valor_etapa00:,.2f}")
        
        # Verificar percentuais
        if total_all > 0:
            print(f"\nPercentuais:")
            print(f"Faturadas: {(total_faturada/total_all*100):.1f}%")
            print(f"Pendentes: {(total_pendente/total_all*100):.1f}%")
            print(f"Etapa 00: {(total_etapa00/total_all*100):.1f}%")
        
    except Exception as e:
        print(f"Erro ao testar estatísticas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_breakdown_improvements()