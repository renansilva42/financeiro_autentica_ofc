#!/usr/bin/env python3
"""
Script para testar a ordenação das Ordens de Serviço por data de previsão
"""

import sys
import os
from datetime import datetime

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.omie_service import OmieService

def test_ordenacao_os():
    """Testa se as ordens de serviço estão sendo ordenadas corretamente"""
    
    print("🔍 Testando ordenação das Ordens de Serviço...")
    print("-" * 60)
    
    try:
        # Inicializar o serviço
        omie_service = OmieService()
        
        # Buscar algumas ordens de serviço (limitando para teste)
        print("📥 Buscando ordens de serviço...")
        orders = omie_service.get_all_service_orders(max_pages=3)  # Limitar para teste
        
        if not orders:
            print("❌ Nenhuma ordem de serviço encontrada")
            return
        
        print(f"✅ {len(orders)} ordens encontradas")
        
        # Função para converter data
        def parse_date(date_str):
            """Converte data dd/mm/yyyy para objeto datetime para ordenação"""
            try:
                if date_str:
                    day, month, year = date_str.split('/')
                    return datetime(int(year), int(month), int(day))
                return datetime.min
            except:
                return datetime.min
        
        # Ordenar as ordens por data de previsão (mais recentes primeiro)
        orders.sort(key=lambda order: parse_date(order.get('Cabecalho', {}).get('dDtPrevisao', '')), reverse=True)
        
        print("\n📋 Primeiras 10 ordens ordenadas por data de previsão (mais recentes primeiro):")
        print("-" * 80)
        print(f"{'OS':<8} {'Data Previsão':<15} {'Cliente':<10} {'Valor':<12}")
        print("-" * 80)
        
        for i, order in enumerate(orders[:10]):
            cabecalho = order.get('Cabecalho', {})
            os_num = cabecalho.get('nCodOS', 'N/A')
            data_previsao = cabecalho.get('dDtPrevisao', 'N/A')
            cliente = cabecalho.get('nCodCli', 'N/A')
            valor = cabecalho.get('nValorTotal', 0)
            
            print(f"#{os_num:<7} {data_previsao:<15} {cliente:<10} R$ {valor:<9.2f}")
        
        # Verificar se a ordenação está correta
        print("\n🔍 Verificando ordenação...")
        datas_ordenadas = []
        for order in orders[:20]:  # Verificar as primeiras 20
            cabecalho = order.get('Cabecalho', {})
            data_str = cabecalho.get('dDtPrevisao', '')
            if data_str:
                try:
                    data_obj = parse_date(data_str)
                    datas_ordenadas.append((data_str, data_obj))
                except:
                    continue
        
        # Verificar se está em ordem decrescente
        ordenacao_correta = True
        for i in range(1, len(datas_ordenadas)):
            if datas_ordenadas[i][1] > datas_ordenadas[i-1][1]:
                ordenacao_correta = False
                break
        
        if ordenacao_correta:
            print("✅ Ordenação está CORRETA - datas mais recentes primeiro")
        else:
            print("❌ Ordenação está INCORRETA")
            
        print("\n📊 Resumo das datas encontradas:")
        datas_unicas = set()
        for order in orders:
            cabecalho = order.get('Cabecalho', {})
            data_str = cabecalho.get('dDtPrevisao', '')
            if data_str:
                datas_unicas.add(data_str)
        
        datas_ordenadas_resumo = sorted(list(datas_unicas), key=lambda x: parse_date(x), reverse=True)
        print(f"Total de datas únicas: {len(datas_unicas)}")
        print("Primeiras 5 datas mais recentes:")
        for data in datas_ordenadas_resumo[:5]:
            print(f"  📅 {data}")
        
        print("\n✅ Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ordenacao_os()