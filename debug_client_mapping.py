#!/usr/bin/env python3
"""
Script para debugar o problema de mapeamento de clientes no Dashboard de Serviços
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.omie_service import OmieService

def debug_client_mapping():
    """Debug do mapeamento de clientes"""
    print("🔍 Iniciando debug do mapeamento de clientes...")
    
    # Inicializar serviço
    omie_service = OmieService()
    
    # 1. Buscar algumas ordens de serviço para análise
    print("\n📋 Buscando ordens de serviço...")
    try:
        orders = omie_service.get_all_service_orders()
        print(f"✅ Encontradas {len(orders)} ordens de serviço")
        
        if not orders:
            print("❌ Nenhuma ordem encontrada para análise")
            return
        
        # Analisar os primeiros 5 registros
        print("\n🔍 Analisando primeiras 5 ordens:")
        for i, order in enumerate(orders[:5]):
            cabecalho = order.get('Cabecalho', {})
            client_code = cabecalho.get('nCodCli')
            
            print(f"\n  Ordem {i+1}:")
            print(f"    nCodOS: {cabecalho.get('nCodOS')}")
            print(f"    nCodCli: {client_code} (tipo: {type(client_code)})")
            print(f"    cNumOS: {cabecalho.get('cNumOS')}")
            
    except Exception as e:
        print(f"❌ Erro ao buscar ordens: {e}")
        return
    
    # 2. Buscar mapeamento de clientes
    print("\n🗂️  Buscando mapeamento de clientes...")
    try:
        client_mapping = omie_service.get_client_name_mapping()
        print(f"✅ Mapeamento carregado com {len(client_mapping)} clientes")
        
        # Mostrar alguns exemplos do mapeamento
        print("\n🔍 Primeiros 10 itens do mapeamento:")
        for i, (code, name) in enumerate(list(client_mapping.items())[:10]):
            print(f"  {code} (tipo: {type(code)}) -> {name}")
            
    except Exception as e:
        print(f"❌ Erro ao buscar mapeamento: {e}")
        return
    
    # 3. Testar correspondências
    print("\n🔗 Testando correspondências...")
    
    # Pegar códigos de cliente das primeiras 10 ordens
    test_codes = []
    for order in orders[:10]:
        cabecalho = order.get('Cabecalho', {})
        client_code = cabecalho.get('nCodCli')
        if client_code is not None:
            test_codes.append(client_code)
    
    print(f"Testando {len(test_codes)} códigos de cliente...")
    
    matches = 0
    mismatches = 0
    
    for client_code in test_codes:
        # Testar diferentes formas de busca
        direct_match = client_mapping.get(client_code)
        str_match = client_mapping.get(str(client_code))
        int_match = None
        
        try:
            int_match = client_mapping.get(int(client_code))
        except (ValueError, TypeError):
            pass
        
        found_name = direct_match or str_match or int_match
        
        if found_name:
            matches += 1
            print(f"  ✅ {client_code} -> {found_name}")
        else:
            mismatches += 1
            print(f"  ❌ {client_code} (tipo: {type(client_code)}) -> NÃO ENCONTRADO")
            
            # Debug: mostrar chaves similares
            similar_keys = [k for k in client_mapping.keys() if str(k) == str(client_code)]
            if similar_keys:
                print(f"      Chaves similares encontradas: {similar_keys}")
    
    print(f"\n📊 Resultado:")
    print(f"  ✅ Correspondências encontradas: {matches}")
    print(f"  ❌ Correspondências perdidas: {mismatches}")
    print(f"  📈 Taxa de sucesso: {(matches/(matches+mismatches)*100):.1f}%" if (matches+mismatches) > 0 else "N/A")
    
    # 4. Análise de tipos de dados
    print("\n🔍 Análise de tipos de dados:")
    
    # Tipos de códigos nas ordens
    order_code_types = set()
    for order in orders[:20]:
        cabecalho = order.get('Cabecalho', {})
        client_code = cabecalho.get('nCodCli')
        if client_code is not None:
            order_code_types.add(type(client_code))
    
    print(f"  Tipos de nCodCli nas ordens: {order_code_types}")
    
    # Tipos de chaves no mapeamento
    mapping_key_types = set()
    for key in list(client_mapping.keys())[:20]:
        mapping_key_types.add(type(key))
    
    print(f"  Tipos de chaves no mapeamento: {mapping_key_types}")
    
    # 5. Sugestão de correção
    print("\n💡 Análise e sugestões:")
    
    if mismatches > 0:
        print("  🔧 Problema detectado: Há códigos de cliente que não estão sendo encontrados no mapeamento")
        print("  📝 Possíveis causas:")
        print("     - Incompatibilidade de tipos de dados (int vs str)")
        print("     - Códigos de cliente não cadastrados no sistema")
        print("     - Cache desatualizado")
        
        print("\n  🛠️  Soluções recomendadas:")
        print("     1. Verificar se o mapeamento está sendo criado corretamente")
        print("     2. Garantir que tanto chaves int quanto str sejam suportadas")
        print("     3. Limpar cache e recarregar dados")
        print("     4. Verificar se há clientes novos não sincronizados")
    else:
        print("  ✅ Mapeamento funcionando corretamente!")

if __name__ == "__main__":
    debug_client_mapping()