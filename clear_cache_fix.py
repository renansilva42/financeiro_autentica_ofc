#!/usr/bin/env python3
"""
Script para limpar cache e testar a correção do mapeamento de clientes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.omie_service import OmieService

def clear_cache_and_test():
    """Limpa cache e testa a correção"""
    print("🧹 Limpando cache e testando correção...")
    
    # Inicializar serviço
    omie_service = OmieService()
    
    # 1. Limpar todo o cache
    print("\n🗑️  Limpando cache...")
    omie_service.clear_cache()
    print("✅ Cache limpo")
    
    # 2. Testar mapeamento de clientes
    print("\n🔍 Testando mapeamento de clientes...")
    try:
        client_mapping = omie_service.get_client_name_mapping()
        print(f"✅ Mapeamento de clientes carregado: {len(client_mapping)} entradas")
        
        # Mostrar alguns exemplos
        print("\n📋 Primeiros 5 exemplos do mapeamento:")
        for i, (code, name) in enumerate(list(client_mapping.items())[:5]):
            print(f"  {code} (tipo: {type(code)}) -> {name}")
            
    except Exception as e:
        print(f"❌ Erro ao carregar mapeamento de clientes: {e}")
        return False
    
    # 3. Testar mapeamento de vendedores
    print("\n🔍 Testando mapeamento de vendedores...")
    try:
        seller_mapping = omie_service.get_seller_name_mapping()
        print(f"✅ Mapeamento de vendedores carregado: {len(seller_mapping)} entradas")
        
        # Mostrar alguns exemplos
        print("\n📋 Primeiros 5 exemplos do mapeamento:")
        for i, (code, name) in enumerate(list(seller_mapping.items())[:5]):
            print(f"  {code} (tipo: {type(code)}) -> {name}")
            
    except Exception as e:
        print(f"❌ Erro ao carregar mapeamento de vendedores: {e}")
        return False
    
    # 4. Testar algumas ordens de serviço
    print("\n🔍 Testando correspondências com ordens de serviço...")
    try:
        orders = omie_service.get_all_service_orders()
        print(f"✅ Ordens carregadas: {len(orders)}")
        
        # Testar primeiras 5 ordens
        matches = 0
        total_tested = 0
        
        for order in orders[:5]:
            cabecalho = order.get('Cabecalho', {})
            client_code = cabecalho.get('nCodCli')
            seller_code = cabecalho.get('nCodVend')
            
            if client_code is not None:
                total_tested += 1
                # Testar múltiplas formas de busca
                client_name = (
                    client_mapping.get(client_code) or 
                    client_mapping.get(str(client_code)) or
                    client_mapping.get(int(client_code)) if str(client_code).isdigit() else None
                )
                
                if client_name:
                    matches += 1
                    print(f"  ✅ Cliente {client_code} -> {client_name}")
                else:
                    print(f"  ❌ Cliente {client_code} -> NÃO ENCONTRADO")
            
            if seller_code is not None:
                seller_name = (
                    seller_mapping.get(seller_code) or 
                    seller_mapping.get(str(seller_code)) or
                    seller_mapping.get(int(seller_code)) if str(seller_code).isdigit() else None
                )
                
                if seller_name:
                    print(f"  ✅ Vendedor {seller_code} -> {seller_name}")
                else:
                    print(f"  ❌ Vendedor {seller_code} -> NÃO ENCONTRADO")
        
        success_rate = (matches / total_tested * 100) if total_tested > 0 else 0
        print(f"\n📊 Taxa de sucesso: {success_rate:.1f}% ({matches}/{total_tested})")
        
        if success_rate >= 90:
            print("✅ Correção aplicada com sucesso!")
            return True
        else:
            print("⚠️  Ainda há problemas no mapeamento")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar ordens: {e}")
        return False

if __name__ == "__main__":
    success = clear_cache_and_test()
    if success:
        print("\n🎉 Correção do bug de regressão concluída com sucesso!")
        print("   Os nomes dos clientes agora devem aparecer corretamente no Dashboard de Serviços.")
    else:
        print("\n❌ Ainda há problemas que precisam ser investigados.")