#!/usr/bin/env python3
"""
Script para investigar a discrepância entre serviços cadastrados e serviços no breakdown
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.omie_service import OmieService

def debug_service_mismatch():
    print("=== INVESTIGAÇÃO DA DISCREPÂNCIA DE SERVIÇOS ===")
    
    # Inicializar serviço
    omie_service = OmieService()
    
    # 1. Buscar serviços cadastrados
    print("\n1. SERVIÇOS CADASTRADOS (16):")
    service_mapping = omie_service.get_service_name_mapping()
    print(f"Total: {len(service_mapping)}")
    for code, name in service_mapping.items():
        print(f"  {code}: {name}")
    
    # 2. Buscar todas as descrições únicas de serviços nas ordens
    print("\n2. DESCRIÇÕES DE SERVIÇOS NAS ORDENS:")
    orders = omie_service.get_all_service_orders()
    service_descriptions = set()
    service_codes_found = set()
    
    for order in orders:
        servicos = order.get("ServicosPrestados", [])
        for servico in servicos:
            service_code = servico.get("nCodServico", "")
            service_desc = servico.get("cDescServ", "").strip()
            
            if service_desc:
                service_descriptions.add(service_desc)
            if service_code and service_code != 0:
                service_codes_found.add(service_code)
    
    print(f"Descrições únicas encontradas: {len(service_descriptions)}")
    for desc in sorted(service_descriptions):
        print(f"  '{desc}'")
    
    print(f"\nCódigos de serviço encontrados nas ordens: {len(service_codes_found)}")
    for code in sorted(service_codes_found):
        mapped_name = service_mapping.get(code, "NÃO MAPEADO")
        print(f"  {code}: {mapped_name}")
    
    # 3. Comparar descrições com nomes cadastrados
    print("\n3. ANÁLISE DE CORRESPONDÊNCIA:")
    registered_names = set(service_mapping.values())
    
    print("\nDescrições que NÃO correspondem a serviços cadastrados:")
    for desc in service_descriptions:
        if desc not in registered_names:
            # Verificar se há correspondência case-insensitive
            found_match = False
            for reg_name in registered_names:
                if reg_name.lower() == desc.lower():
                    print(f"  '{desc}' -> MATCH case-insensitive com '{reg_name}'")
                    found_match = True
                    break
            
            if not found_match:
                print(f"  '{desc}' -> SEM CORRESPONDÊNCIA")
    
    print("\nServiços cadastrados que NÃO aparecem nas ordens:")
    for reg_name in registered_names:
        if reg_name not in service_descriptions:
            # Verificar se há correspondência case-insensitive
            found_match = False
            for desc in service_descriptions:
                if desc.lower() == reg_name.lower():
                    found_match = True
                    break
            
            if not found_match:
                print(f"  '{reg_name}' -> Não usado em nenhuma ordem")
    
    # 4. Simular o breakdown atual
    print("\n4. SIMULAÇÃO DO BREAKDOWN ATUAL:")
    service_breakdown = {}
    
    for order in orders:
        servicos = order.get("ServicosPrestados", [])
        for servico in servicos:
            service_code = servico.get("nCodServico", "")
            service_desc = servico.get("cDescServ", "").strip()
            
            if service_code and service_code != 0:
                # Usar código do serviço se disponível
                service_type = service_mapping.get(service_code, f"Serviço {service_code}")
            elif service_desc:
                # Se código não está disponível, usar descrição diretamente
                service_type = service_desc
                for mapped_code, mapped_name in service_mapping.items():
                    if mapped_name.lower() == service_desc.lower():
                        service_type = mapped_name
                        break
            else:
                service_type = "Não informado"
            
            if service_type not in service_breakdown:
                service_breakdown[service_type] = 0
            service_breakdown[service_type] += 1
    
    print(f"Total de tipos no breakdown: {len(service_breakdown)}")
    for service_type, count in sorted(service_breakdown.items()):
        is_registered = service_type in registered_names
        status = "✅ CADASTRADO" if is_registered else "❌ NÃO CADASTRADO"
        print(f"  {service_type}: {count} ordens - {status}")

if __name__ == "__main__":
    debug_service_mismatch()