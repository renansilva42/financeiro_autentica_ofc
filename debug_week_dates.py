#!/usr/bin/env python3
"""
Script para debugar as datas das ordens de serviço e verificar quais semanas deveriam estar disponíveis
"""

import sys
import os
from datetime import datetime, timedelta
from collections import Counter

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.omie_service import OmieService

def debug_service_order_dates():
    """Debug das datas das ordens de serviço"""
    print("🔍 Debugando datas das ordens de serviço...")
    
    try:
        omie_service = OmieService()
        
        # Buscar todas as ordens
        print("Carregando ordens de serviço...")
        orders = omie_service.get_all_service_orders()
        print(f"Total de ordens carregadas: {len(orders)}")
        
        # Analisar datas
        dates_found = []
        invalid_dates = []
        
        for i, order in enumerate(orders):
            cabecalho = order.get("Cabecalho", {})
            date_str = cabecalho.get("dDtPrevisao", "")
            
            if date_str:
                try:
                    # Converter data dd/mm/yyyy para datetime
                    parts = date_str.split("/")
                    if len(parts) == 3:
                        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                        
                        # Validar se a data é válida
                        if 1 <= day <= 31 and 1 <= month <= 12 and year >= 2000:
                            date_obj = datetime(year, month, day)
                            dates_found.append(date_obj)
                        else:
                            invalid_dates.append(date_str)
                except Exception as e:
                    invalid_dates.append(f"{date_str} (erro: {e})")
        
        print(f"Datas válidas encontradas: {len(dates_found)}")
        print(f"Datas inválidas: {len(invalid_dates)}")
        
        if invalid_dates:
            print("Primeiras 10 datas inválidas:")
            for date in invalid_dates[:10]:
                print(f"  - {date}")
        
        # Analisar período das datas
        if dates_found:
            dates_found.sort()
            min_date = dates_found[0]
            max_date = dates_found[-1]
            
            print(f"\nPeríodo das ordens:")
            print(f"  Data mais antiga: {min_date.strftime('%d/%m/%Y')}")
            print(f"  Data mais recente: {max_date.strftime('%d/%m/%Y')}")
            
            # Focar no período de junho de 2025
            june_2025_dates = [d for d in dates_found if d.year == 2025 and d.month == 6]
            
            if june_2025_dates:
                print(f"\nDatas em junho de 2025: {len(june_2025_dates)}")
                june_2025_dates.sort()
                
                print("Todas as datas de junho de 2025:")
                for date in june_2025_dates:
                    # Calcular semana
                    start_of_week = date - timedelta(days=date.weekday())
                    end_of_week = start_of_week + timedelta(days=6)
                    week_label = f"{start_of_week.strftime('%d/%m')} a {end_of_week.strftime('%d/%m/%Y')}"
                    
                    print(f"  {date.strftime('%d/%m/%Y')} -> Semana: {week_label}")
                
                # Contar por semana
                week_counts = Counter()
                for date in june_2025_dates:
                    start_of_week = date - timedelta(days=date.weekday())
                    end_of_week = start_of_week + timedelta(days=6)
                    week_key = f"{start_of_week.strftime('%Y-%m-%d')}_{end_of_week.strftime('%Y-%m-%d')}"
                    week_counts[week_key] += 1
                
                print(f"\nContagem por semana em junho de 2025:")
                for week_key, count in sorted(week_counts.items()):
                    start_date_str, end_date_str = week_key.split("_")
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    week_label = f"{start_date.strftime('%d/%m')} a {end_date.strftime('%d/%m/%Y')}"
                    print(f"  {week_label}: {count} ordens")
            else:
                print("\nNenhuma data encontrada em junho de 2025")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_service_order_dates()