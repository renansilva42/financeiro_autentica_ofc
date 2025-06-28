#!/usr/bin/env python3
"""
Script para testar a aplicação com a sequência de semanas corrigida
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.omie_service import OmieService

def test_app_weeks():
    """Testa a aplicação com a sequência de semanas corrigida"""
    print("🚀 Testando aplicação com sequência de semanas corrigida...")
    
    try:
        omie_service = OmieService()
        
        # Limpar cache primeiro
        print("Limpando cache de semanas...")
        omie_service.clear_weeks_cache()
        
        # Simular o que a aplicação faz
        print("Simulando chamada da aplicação...")
        available_weeks = omie_service.get_available_weeks_for_services(fill_gaps=True)
        
        print(f"Total de semanas disponíveis: {len(available_weeks)}")
        
        # Verificar as primeiras semanas (mais recentes)
        print("\nPrimeiras 15 semanas (mais recentes):")
        for i, week in enumerate(available_weeks[:15]):
            has_orders_icon = "✓" if week.get('has_orders', True) else "📅"
            print(f"  {i+1:2d}. {has_orders_icon} {week['label']}")
        
        # Verificar especificamente a sequência de junho
        june_weeks = [w for w in available_weeks if '2025-06' in w['value']]
        print(f"\nSequência de junho de 2025 ({len(june_weeks)} semanas):")
        for i, week in enumerate(june_weeks):
            has_orders_icon = "✓" if week.get('has_orders', True) else "📅"
            status = "com ordens" if week.get('has_orders', True) else "sem ordens"
            print(f"  {i+1}. {has_orders_icon} {week['label']} ({status})")
        
        # Verificar se a sequência está correta
        expected_order = [
            "23/06 a 29/06/2025",
            "16/06 a 22/06/2025", 
            "09/06 a 15/06/2025",
            "02/06 a 08/06/2025"
        ]
        
        actual_order = [w['label'].split(' (')[0] for w in june_weeks[:4]]
        
        print(f"\n✅ Verificação da ordem:")
        sequence_correct = True
        for i, (expected, actual) in enumerate(zip(expected_order, actual_order)):
            if expected == actual:
                print(f"  ✅ Posição {i+1}: {actual} (correto)")
            else:
                print(f"  ❌ Posição {i+1}: esperado '{expected}', encontrado '{actual}'")
                sequence_correct = False
        
        if sequence_correct:
            print(f"\n🎉 SUCESSO: A sequência de semanas está correta!")
            print(f"   A semana '16/06 a 22/06/2025' agora aparece na posição correta.")
        else:
            print(f"\n❌ ERRO: A sequência ainda não está correta.")
        
        # Verificar se a semana problemática está presente
        missing_week_found = any("16/06 a 22/06/2025" in w['label'] for w in available_weeks)
        if missing_week_found:
            print(f"✅ A semana problemática '16/06 a 22/06/2025' foi encontrada na lista!")
        else:
            print(f"❌ A semana problemática '16/06 a 22/06/2025' ainda não foi encontrada!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_app_weeks()