#!/usr/bin/env python3
"""
Script para testar se o problema de timeout na rota /services foi resolvido
"""

import sys
import os
import time
import requests
from datetime import datetime

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_services_endpoint():
    """Testa o endpoint /services para verificar se não há mais timeout"""
    
    print("🧪 Testando correção do timeout na rota /services")
    print("=" * 60)
    
    # URL base da aplicação (assumindo que está rodando localmente)
    base_url = "http://localhost:8002"
    
    try:
        print(f"📡 Fazendo requisição para {base_url}/services...")
        start_time = time.time()
        
        # Fazer requisição com timeout de 30 segundos
        response = requests.get(f"{base_url}/services", timeout=30)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  Tempo de resposta: {duration:.2f} segundos")
        
        if response.status_code == 200:
            print("✅ Sucesso! A rota /services respondeu corretamente")
            print(f"📊 Status Code: {response.status_code}")
            print(f"📏 Tamanho da resposta: {len(response.content)} bytes")
            
            # Verificar se contém dados esperados
            if "Dashboard de Serviços" in response.text:
                print("✅ Conteúdo da página carregado corretamente")
            else:
                print("⚠️  Aviso: Conteúdo da página pode estar incompleto")
                
        else:
            print(f"❌ Erro: Status Code {response.status_code}")
            print(f"📄 Resposta: {response.text[:500]}...")
            
    except requests.exceptions.Timeout:
        print("❌ Erro: Timeout na requisição (>30 segundos)")
        print("   O problema de timeout ainda não foi resolvido")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("   Certifique-se de que a aplicação está rodando em http://localhost:8002")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")

def test_omie_service_directly():
    """Testa o OmieService diretamente para verificar as melhorias"""
    
    print("\n🔧 Testando OmieService diretamente...")
    print("=" * 60)
    
    try:
        from services.omie_service import OmieService
        
        print("📦 Inicializando OmieService...")
        omie_service = OmieService()
        
        print("🔍 Testando get_all_service_orders com limite de páginas...")
        start_time = time.time()
        
        # Testar com limite de 2 páginas (100 registros)
        orders = omie_service.get_all_service_orders(max_pages=2)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  Tempo para buscar ordens: {duration:.2f} segundos")
        print(f"📊 Total de ordens encontradas: {len(orders)}")
        
        if len(orders) > 0:
            print("✅ Sucesso! Ordens de serviço carregadas com limite de páginas")
            
            # Testar cache
            print("\n💾 Testando cache...")
            start_time = time.time()
            cached_orders = omie_service.get_all_service_orders(max_pages=2)
            end_time = time.time()
            cache_duration = end_time - start_time
            
            print(f"⏱️  Tempo para buscar do cache: {cache_duration:.2f} segundos")
            
            if cache_duration < 1.0:  # Deve ser muito rápido se vier do cache
                print("✅ Cache funcionando corretamente!")
            else:
                print("⚠️  Cache pode não estar funcionando como esperado")
                
        else:
            print("⚠️  Nenhuma ordem de serviço encontrada")
            
    except Exception as e:
        print(f"❌ Erro ao testar OmieService: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal"""
    print(f"🚀 Teste de Correção de Timeout - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Testar o serviço diretamente primeiro
    test_omie_service_directly()
    
    # Testar o endpoint HTTP
    test_services_endpoint()
    
    print("\n" + "=" * 60)
    print("✨ Teste concluído!")
    print("\n💡 Dicas:")
    print("   - Se ainda houver timeout, considere reduzir ainda mais o max_pages")
    print("   - Verifique os logs da aplicação para mais detalhes")
    print("   - O cache deve melhorar significativamente a performance nas próximas requisições")

if __name__ == "__main__":
    main()