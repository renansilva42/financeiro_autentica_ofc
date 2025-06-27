#!/usr/bin/env python3
"""
Script para testar o mapeamento de serviços e identificar o problema
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.omie_service import OmieService

def test_service_mapping():
    print("=== TESTE DE MAPEAMENTO DE SERVIÇOS ===")
    
    # Inicializar serviço
    omie_service = OmieService()
    
    # Limpar cache para garantir dados frescos
    omie_service.clear_cache()
    print("Cache limpo")
    
    # 1. Testar busca de serviços cadastrados
    print("\n1. Buscando serviços cadastrados...")
    try:
        services = omie_service.get_all_services()
        print(f"Total de serviços encontrados: {len(services)}")
        
        if services:
            print("\nPrimeiros 3 serviços (estrutura completa):")
            for i, service in enumerate(services[:3]):
                print(f"\nServiço {i+1}:")
                print(f"  Estrutura completa: {service}")
                
                # Tentar extrair código e nome
                service_code = None
                service_name = ""
                
                if "intListar" in service and "nCodServ" in service["intListar"]:
                    service_code = service["intListar"]["nCodServ"]
                    if "cabecalho" in service and "cDescricao" in service["cabecalho"]:
                        service_name = service["cabecalho"]["cDescricao"]
                elif "nCodServ" in service:
                    service_code = service["nCodServ"]
                    service_name = service.get("cDescricao", "")
                
                print(f"  Código extraído: {service_code}")
                print(f"  Nome extraído: {service_name}")
        
    except Exception as e:
        print(f"Erro ao buscar serviços: {e}")
    
    # 2. Testar mapeamento de serviços
    print("\n2. Testando mapeamento de serviços...")
    try:
        mapping = omie_service.get_service_name_mapping()
        print(f"Total de serviços mapeados: {len(mapping)}")
        
        if mapping:
            print("\nPrimeiros 5 mapeamentos:")
            for i, (code, name) in enumerate(list(mapping.items())[:5]):
                print(f"  {code}: {name}")
    
    except Exception as e:
        print(f"Erro ao criar mapeamento: {e}")
    
    # 3. Testar uma ordem de serviço específica
    print("\n3. Buscando ordens de serviço para teste...")
    try:
        orders = omie_service.get_all_service_orders()
        print(f"Total de ordens encontradas: {len(orders)}")
        
        if orders:
            # Procurar por uma ordem específica mencionada pelo usuário
            target_order = None
            for order in orders:
                cabecalho = order.get("Cabecalho", {})
                if str(cabecalho.get("nCodOS", "")) == "9797752609":
                    target_order = order
                    break
            
            if target_order:
                print(f"\nOrdem específica encontrada: #{target_order['Cabecalho']['nCodOS']}")
                print(f"Status: {target_order['Cabecalho'].get('cEtapa', 'N/A')}")
                
                servicos = target_order.get("ServicosPrestados", [])
                print(f"Serviços na ordem: {len(servicos)}")
                
                for i, servico in enumerate(servicos):
                    service_code = servico.get("nCodServico", "")
                    service_desc = servico.get("cDescServ", "")
                    print(f"  Serviço {i+1}:")
                    print(f"    Código (nCodServico): {service_code}")
                    print(f"    Descrição (cDescServ): {service_desc}")
                    
                    # Verificar se está no mapeamento
                    if service_code in mapping:
                        print(f"    Mapeado como: {mapping[service_code]}")
                    else:
                        print(f"    NÃO ENCONTRADO no mapeamento!")
            else:
                print("\nOrdem específica #9797752609 não encontrada")
                print("Mostrando primeira ordem como exemplo:")
                first_order = orders[0]
                cabecalho = first_order.get("Cabecalho", {})
                print(f"Ordem: #{cabecalho.get('nCodOS', 'N/A')}")
                print(f"Status: {cabecalho.get('cEtapa', 'N/A')}")
                
                servicos = first_order.get("ServicosPrestados", [])
                print(f"Serviços: {len(servicos)}")
                
                for i, servico in enumerate(servicos[:2]):  # Apenas os primeiros 2
                    service_code = servico.get("nCodServico", "")
                    service_desc = servico.get("cDescServ", "")
                    print(f"  Serviço {i+1}:")
                    print(f"    Código: {service_code}")
                    print(f"    Descrição: {service_desc}")
    
    except Exception as e:
        print(f"Erro ao buscar ordens: {e}")

if __name__ == "__main__":
    test_service_mapping()