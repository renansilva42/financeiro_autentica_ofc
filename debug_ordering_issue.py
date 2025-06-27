#!/usr/bin/env python3
"""
Script para investigar o problema de ordenação no breakdown de serviços
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.omie_service import OmieService

def debug_ordering_issue():
    print("=== INVESTIGAÇÃO DO PROBLEMA DE ORDENAÇÃO ===")
    
    # Inicializar serviço
    omie_service = OmieService()
    
    # Limpar cache
    omie_service.clear_cache()
    
    # Buscar estatísticas
    stats = omie_service.get_service_orders_stats()
    
    print("\n1. VERIFICAÇÃO DOS VALORES BRUTOS:")
    print("   Serviços de produção de vídeos vs Be Master Parcial")
    
    # Buscar os dois serviços específicos
    servicos_producao = None
    be_master_parcial = None
    
    for service_name, service_data in stats['service_breakdown'].items():
        if service_name == "Serviços de produção de vídeos":
            servicos_producao = service_data
        elif service_name == "Be Master Parcial":
            be_master_parcial = service_data
    
    if servicos_producao and be_master_parcial:
        print(f"\n   Serviços de produção de vídeos:")
        print(f"     Total Value: R$ {servicos_producao['total_value']:,.2f}")
        print(f"     Total Count: {servicos_producao['total_count']}")
        print(f"     Faturada: {servicos_producao['faturada']['count']} | R$ {servicos_producao['faturada']['value']:,.2f}")
        print(f"     Pendente: {servicos_producao['pendente']['count']} | R$ {servicos_producao['pendente']['value']:,.2f}")
        print(f"     Etapa 00: {servicos_producao['etapa_00']['count']} | R$ {servicos_producao['etapa_00']['value']:,.2f}")
        
        print(f"\n   Be Master Parcial:")
        print(f"     Total Value: R$ {be_master_parcial['total_value']:,.2f}")
        print(f"     Total Count: {be_master_parcial['total_count']}")
        print(f"     Faturada: {be_master_parcial['faturada']['count']} | R$ {be_master_parcial['faturada']['value']:,.2f}")
        print(f"     Pendente: {be_master_parcial['pendente']['count']} | R$ {be_master_parcial['pendente']['value']:,.2f}")
        print(f"     Etapa 00: {be_master_parcial['etapa_00']['count']} | R$ {be_master_parcial['etapa_00']['value']:,.2f}")
        
        print(f"\n   COMPARAÇÃO:")
        if servicos_producao['total_value'] > be_master_parcial['total_value']:
            print(f"   ✅ Serviços de produção de vídeos (R$ {servicos_producao['total_value']:,.2f}) > Be Master Parcial (R$ {be_master_parcial['total_value']:,.2f})")
            print(f"   ✅ Ordenação está CORRETA")
        else:
            print(f"   ❌ Be Master Parcial (R$ {be_master_parcial['total_value']:,.2f}) > Serviços de produção de vídeos (R$ {servicos_producao['total_value']:,.2f})")
            print(f"   ❌ Ordenação está INCORRETA")
    
    print("\n2. VERIFICAÇÃO DA LISTA ORDENADA:")
    print("   Top 10 serviços por faturamento:")
    
    for i, (service_name, service_data) in enumerate(stats['service_breakdown_sorted'][:10], 1):
        total_value = service_data['total_value']
        total_count = service_data['total_count']
        
        # Destacar os serviços em questão
        if service_name in ["Serviços de produção de vídeos", "Be Master Parcial"]:
            marker = "🔍"
        else:
            marker = "  "
        
        print(f"   {marker} {i:2d}. {service_name}")
        print(f"        R$ {total_value:,.2f} ({total_count} OS)")
    
    print("\n3. VERIFICAÇÃO MANUAL DA ORDENA��ÃO:")
    # Criar lista manual para verificar
    manual_sort = []
    for service_name, service_data in stats['service_breakdown'].items():
        if service_name in stats['service_breakdown_sorted'][0][1].__class__.__bases__[0].__dict__ if hasattr(stats['service_breakdown_sorted'][0][1], '__class__') else True:
            manual_sort.append((service_name, service_data['total_value']))
    
    # Ordenar manualmente
    manual_sort.sort(key=lambda x: x[1], reverse=True)
    
    print("   Ordenação manual (top 10):")
    for i, (service_name, total_value) in enumerate(manual_sort[:10], 1):
        if service_name in ["Serviços de produção de vídeos", "Be Master Parcial"]:
            marker = "🔍"
        else:
            marker = "  "
        print(f"   {marker} {i:2d}. {service_name}: R$ {total_value:,.2f}")
    
    print("\n4. COMPARAÇÃO ENTRE ORDENAÇÕES:")
    print("   Sistema vs Manual:")
    
    system_order = [(name, data['total_value']) for name, data in stats['service_breakdown_sorted'][:10]]
    manual_order = manual_sort[:10]
    
    for i in range(min(len(system_order), len(manual_order))):
        sys_name, sys_value = system_order[i]
        man_name, man_value = manual_order[i]
        
        if sys_name == man_name and abs(sys_value - man_value) < 0.01:
            status = "✅"
        else:
            status = "❌"
        
        print(f"   {status} Posição {i+1}:")
        print(f"      Sistema: {sys_name} (R$ {sys_value:,.2f})")
        print(f"      Manual:  {man_name} (R$ {man_value:,.2f})")

if __name__ == "__main__":
    debug_ordering_issue()