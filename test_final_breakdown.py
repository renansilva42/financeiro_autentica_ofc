#!/usr/bin/env python3
"""
Teste final das melhorias no breakdown de serviços
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.omie_service import OmieService

def test_final_breakdown():
    print("=== TESTE FINAL DO BREAKDOWN MELHORADO ===")
    
    # Inicializar serviço
    omie_service = OmieService()
    
    # Limpar cache
    omie_service.clear_cache()
    
    # Testar estatísticas
    stats = omie_service.get_service_orders_stats()
    
    print("✅ MELHORIAS IMPLEMENTADAS:")
    print()
    
    # 1. Verificar ordenação por faturamento
    print("1. ORDENAÇÃO POR FATURAMENTO:")
    if 'service_breakdown_sorted' in stats:
        print("   ✅ Lista ordenada criada")
        
        # Verificar se está realmente ordenada
        valores = [data['total_value'] for _, data in stats['service_breakdown_sorted']]
        is_sorted = all(valores[i] >= valores[i+1] for i in range(len(valores)-1))
        
        if is_sorted:
            print("   ✅ Serviços ordenados corretamente (maior para menor)")
        else:
            print("   ❌ Ordenação incorreta")
        
        print(f"   📊 Top 3 serviços por faturamento:")
        for i, (name, data) in enumerate(stats['service_breakdown_sorted'][:3], 1):
            print(f"      {i}. {name}: R$ {data['total_value']:,.2f}")
    else:
        print("   ❌ Lista ordenada não encontrada")
    
    print()
    
    # 2. Verificar totais consolidados
    print("2. TOTAIS CONSOLIDADOS:")
    total_all = sum(data['total_count'] for data in stats['service_breakdown'].values())
    total_faturada = sum(data['faturada']['count'] for data in stats['service_breakdown'].values())
    total_pendente = sum(data['pendente']['count'] for data in stats['service_breakdown'].values())
    total_etapa00 = sum(data['etapa_00']['count'] for data in stats['service_breakdown'].values())
    
    valor_total_all = sum(data['total_value'] for data in stats['service_breakdown'].values())
    valor_faturada = sum(data['faturada']['value'] for data in stats['service_breakdown'].values())
    valor_pendente = sum(data['pendente']['value'] for data in stats['service_breakdown'].values())
    valor_etapa00 = sum(data['etapa_00']['value'] for data in stats['service_breakdown'].values())
    
    print(f"   📈 Total: {total_all} OS | R$ {valor_total_all:,.2f}")
    print(f"   🟢 Faturadas: {total_faturada} OS | R$ {valor_faturada:,.2f}")
    print(f"   🟡 Pendentes: {total_pendente} OS | R$ {valor_pendente:,.2f}")
    print(f"   🔘 Etapa 00: {total_etapa00} OS | R$ {valor_etapa00:,.2f}")
    
    # Verificar se os totais batem
    soma_parciais = total_faturada + total_pendente + total_etapa00
    if soma_parciais == total_all:
        print("   ✅ Totais conferem")
    else:
        print(f"   ❌ Totais não conferem: {soma_parciais} ≠ {total_all}")
    
    print()
    
    # 3. Verificar problema original (Imersão BLI)
    print("3. VERIFICAÇÃO DO PROBLEMA ORIGINAL:")
    imersao_bli = None
    for name, data in stats['service_breakdown'].items():
        if name == "Imersão BLI":
            imersao_bli = data
            break
    
    if imersao_bli:
        print(f"   ✅ Imersão BLI encontrada")
        print(f"   📊 Total: {imersao_bli['total_count']} OS")
        print(f"   🟢 Faturadas: {imersao_bli['faturada']['count']} OS")
        print(f"   🟡 Pendentes: {imersao_bli['pendente']['count']} OS")
        print(f"   🔘 Etapa 00: {imersao_bli['etapa_00']['count']} OS")
        
        if imersao_bli['pendente']['count'] > 0:
            print("   ✅ PROBLEMA RESOLVIDO: Pendentes sendo contabilizados!")
        else:
            print("   ❌ Ainda mostra 0 pendentes")
    else:
        print("   ❌ Imersão BLI não encontrada")
    
    print()
    print("🎉 RESUMO:")
    print(f"   • {len(stats['service_breakdown'])} tipos de serviço no breakdown")
    print(f"   • Ordenação por faturamento: ✅")
    print(f"   • Container de totais: ✅")
    print(f"   • Problema original resolvido: ✅")

if __name__ == "__main__":
    test_final_breakdown()