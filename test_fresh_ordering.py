#!/usr/bin/env python3
"""
Teste com cache limpo para verificar ordenação
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.omie_service import OmieService

def test_fresh_ordering():
    print("=== TESTE COM CACHE LIMPO ===")
    
    # Inicializar serviço
    omie_service = OmieService()
    
    # Limpar cache completamente
    omie_service.clear_cache()
    print("✅ Cache limpo")
    
    # Buscar estatísticas frescas
    print("\n🔄 Carregando dados frescos...")
    stats = omie_service.get_service_orders_stats()
    
    print(f"\n📊 TOP 10 SERVIÇOS POR FATURAMENTO (dados frescos):")
    print("=" * 80)
    
    for i, (service_name, service_data) in enumerate(stats['service_breakdown_sorted'][:10], 1):
        total_value = service_data['total_value']
        total_count = service_data['total_count']
        faturada_value = service_data['faturada']['value']
        pendente_value = service_data['pendente']['value']
        etapa00_value = service_data['etapa_00']['value']
        
        # Destacar os serviços em questão
        if service_name in ["Serviços de produção de vídeos", "Be Master Parcial"]:
            print(f"🔍 {i:2d}. {service_name}")
        else:
            print(f"   {i:2d}. {service_name}")
        
        print(f"       💰 TOTAL: R$ {total_value:,.2f} ({total_count} OS)")
        print(f"       🟢 Faturado: R$ {faturada_value:,.2f}")
        print(f"       🟡 Pendente: R$ {pendente_value:,.2f}")
        print(f"       🔘 Etapa 00: R$ {etapa00_value:,.2f}")
        print()
    
    # Verificação específica dos dois serviços
    print("🔍 ANÁLISE DETALHADA DOS SERVIÇOS EM QUESTÃO:")
    print("=" * 50)
    
    for service_name, service_data in stats['service_breakdown_sorted']:
        if service_name in ["Serviços de produção de vídeos", "Be Master Parcial"]:
            position = next(i for i, (name, _) in enumerate(stats['service_breakdown_sorted'], 1) if name == service_name)
            
            print(f"\n📍 POSIÇÃO {position}: {service_name}")
            print(f"   💰 Valor Total: R$ {service_data['total_value']:,.2f}")
            print(f"   📊 Composição:")
            print(f"      🟢 Faturado: R$ {service_data['faturada']['value']:,.2f} ({service_data['faturada']['count']} OS)")
            print(f"      🟡 Pendente: R$ {service_data['pendente']['value']:,.2f} ({service_data['pendente']['count']} OS)")
            print(f"      🔘 Etapa 00: R$ {service_data['etapa_00']['value']:,.2f} ({service_data['etapa_00']['count']} OS)")
    
    print("\n✅ CONCLUSÃO:")
    servicos_pos = next(i for i, (name, _) in enumerate(stats['service_breakdown_sorted'], 1) if name == "Serviços de produção de vídeos")
    bemaster_pos = next(i for i, (name, _) in enumerate(stats['service_breakdown_sorted'], 1) if name == "Be Master Parcial")
    
    if servicos_pos < bemaster_pos:
        print(f"   ✅ Ordenação CORRETA: Serviços de produção de vídeos ({servicos_pos}º) > Be Master Parcial ({bemaster_pos}º)")
    else:
        print(f"   ❌ Ordenação INCORRETA: Be Master Parcial ({bemaster_pos}º) deveria estar antes de Serviços de produção de vídeos ({servicos_pos}º)")
    
    print(f"\n💡 NOTA IMPORTANTE:")
    print(f"   A ordenação é feita pelo VALOR TOTAL (faturado + pendente + etapa 00)")
    print(f"   Se você está vendo apenas o valor faturado, pode parecer incorreto")

if __name__ == "__main__":
    test_fresh_ordering()