#!/usr/bin/env python3
"""
Script para testar a sequência de semanas corrigida
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.omie_service import OmieService

def test_fixed_weeks():
    """Testa a sequência de semanas corrigida"""
    print("🧪 Testando sequência de semanas corrigida...")
    
    try:
        omie_service = OmieService()
        
        # Limpar cache primeiro
        print("Limpando cache de semanas...")
        omie_service.clear_weeks_cache()
        
        # Testar com preenchimento de lacunas ativado
        print("\n📅 Testando com preenchimento de lacunas (fill_gaps=True):")
        weeks_with_gaps = omie_service.get_available_weeks_for_services(fill_gaps=True)
        
        print(f"Total de semanas: {len(weeks_with_gaps)}")
        
        # Focar nas semanas de junho de 2025
        june_weeks = [w for w in weeks_with_gaps if '2025-06' in w['value']]
        
        print(f"\nSemanas de junho de 2025 ({len(june_weeks)}):")
        for i, week in enumerate(june_weeks):
            orders_indicator = "✓" if week.get('has_orders', True) else "○"
            print(f"  {i+1}. {orders_indicator} {week['label']} ({week['value']})")
        
        # Verificar se a sequência está correta
        print(f"\n✅ Verificação da sequência de junho:")
        expected_sequence = [
            "23/06 a 29/06/2025",
            "16/06 a 22/06/2025", 
            "09/06 a 15/06/2025",
            "02/06 a 08/06/2025"
        ]
        
        actual_sequence = [w['label'].split(' (')[0] for w in june_weeks]  # Remove "(sem ordens)" se presente
        
        print("Sequência esperada:")
        for i, week in enumerate(expected_sequence):
            print(f"  {i+1}. {week}")
        
        print("Sequência atual:")
        for i, week in enumerate(actual_sequence):
            print(f"  {i+1}. {week}")
        
        # Verificar se a semana 16/06 a 22/06/2025 está presente
        missing_week = "16/06 a 22/06/2025"
        week_found = any(missing_week in w['label'] for w in june_weeks)
        
        if week_found:
            print(f"✅ Semana {missing_week} encontrada na sequência!")
        else:
            print(f"❌ Semana {missing_week} ainda não encontrada na sequência!")
        
        # Testar sem preenchimento de lacunas
        print("\n📅 Testando sem preenchimento de lacunas (fill_gaps=False):")
        weeks_no_gaps = omie_service.get_available_weeks_for_services(fill_gaps=False)
        
        june_weeks_no_gaps = [w for w in weeks_no_gaps if '2025-06' in w['value']]
        print(f"Semanas de junho sem preenchimento ({len(june_weeks_no_gaps)}):")
        for i, week in enumerate(june_weeks_no_gaps):
            print(f"  {i+1}. {week['label']} ({week['value']})")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_weeks()