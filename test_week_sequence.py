#!/usr/bin/env python3
"""
Script para testar a sequência de semanas e verificar se está correta
"""

import sys
import os
from datetime import datetime, timedelta

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.omie_service import OmieService

def test_week_calculation():
    """Testa o cálculo de semanas para verificar se está correto"""
    print("🧪 Testando cálculo de semanas...")
    
    # Datas de teste
    test_dates = [
        "02/06/2025",  # Segunda-feira
        "08/06/2025",  # Domingo
        "09/06/2025",  # Segunda-feira da semana seguinte
        "15/06/2025",  # Domingo da semana seguinte
        "16/06/2025",  # Segunda-feira da próxima semana
        "22/06/2025",  # Domingo da próxima semana
        "23/06/2025",  # Segunda-feira da próxima semana
        "29/06/2025",  # Domingo da próxima semana
    ]
    
    weeks_set = set()
    
    for date_str in test_dates:
        try:
            # Converter data dd/mm/yyyy para datetime
            parts = date_str.split("/")
            if len(parts) == 3:
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                date_obj = datetime(year, month, day)
                
                # Calcular início da semana (segunda-feira)
                start_of_week = date_obj - timedelta(days=date_obj.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                
                # Formato da semana: "YYYY-MM-DD_YYYY-MM-DD" (início_fim)
                week_key = f"{start_of_week.strftime('%Y-%m-%d')}_{end_of_week.strftime('%Y-%m-%d')}"
                weeks_set.add(week_key)
                
                print(f"Data: {date_str} -> Semana: {start_of_week.strftime('%d/%m')} a {end_of_week.strftime('%d/%m/%Y')} ({week_key})")
        
        except Exception as e:
            print(f"Erro ao processar {date_str}: {e}")
    
    # Ordenar semanas cronologicamente (mais recentes primeiro)
    def sort_week_key(week_key):
        try:
            start_date_str = week_key.split("_")[0]
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            return start_date
        except:
            return datetime.min
    
    sorted_weeks = sorted(list(weeks_set), key=sort_week_key, reverse=True)
    
    print(f"\n📅 Semanas únicas encontradas ({len(sorted_weeks)}):")
    for i, week_key in enumerate(sorted_weeks):
        try:
            start_date_str, end_date_str = week_key.split("_")
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            
            # Formato amigável
            if start_date.year == end_date.year and start_date.month == end_date.month:
                label = f"{start_date.strftime('%d/%m')} a {end_date.strftime('%d/%m/%Y')}"
            else:
                label = f"{start_date.strftime('%d/%m')} a {end_date.strftime('%d/%m/%Y')}"
            
            print(f"  {i+1}. {label} ({week_key})")
        except Exception as e:
            print(f"  {i+1}. {week_key} (erro na formatação: {e})")
    
    # Verificar se a sequência está correta
    print(f"\n✅ Verificação da sequência:")
    if len(sorted_weeks) >= 2:
        for i in range(len(sorted_weeks) - 1):
            current_week = sorted_weeks[i]
            next_week = sorted_weeks[i + 1]
            
            try:
                current_start = datetime.strptime(current_week.split("_")[0], '%Y-%m-%d')
                next_start = datetime.strptime(next_week.split("_")[0], '%Y-%m-%d')
                
                # Diferença deve ser exatamente 7 dias (1 semana)
                diff = current_start - next_start
                if diff.days == 7:
                    print(f"  ✅ Semana {i+1} -> {i+2}: Sequência correta (diferença: {diff.days} dias)")
                else:
                    print(f"  ❌ Semana {i+1} -> {i+2}: Sequência incorreta (diferença: {diff.days} dias)")
            except Exception as e:
                print(f"  ❌ Erro ao verificar semanas {i+1} -> {i+2}: {e}")

def test_omie_service_weeks():
    """Testa o serviço Omie para verificar as semanas disponíveis"""
    print("\n🔧 Testando serviço Omie...")
    
    try:
        omie_service = OmieService()
        
        # Limpar cache de semanas primeiro
        print("Limpando cache de semanas...")
        omie_service.clear_weeks_cache()
        
        # Buscar semanas disponíveis
        print("Buscando semanas disponíveis...")
        available_weeks = omie_service.get_available_weeks_for_services()
        
        print(f"\n📊 Resultado do serviço: {len(available_weeks)} semanas encontradas")
        
        if available_weeks:
            print("\nPrimeiras 10 semanas:")
            for i, week in enumerate(available_weeks[:10]):
                print(f"  {i+1}. {week['label']} ({week['value']})")
        
    except Exception as e:
        print(f"❌ Erro ao testar serviço Omie: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando teste de sequência de semanas...\n")
    
    # Teste 1: Cálculo manual de semanas
    test_week_calculation()
    
    # Teste 2: Serviço Omie
    test_omie_service_weeks()
    
    print("\n✅ Teste concluído!")