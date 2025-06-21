#!/usr/bin/env python3

# Script para testar a ordenação dos dados mensais

def test_sorting():
    # Simular dados como podem vir da API
    test_data = {
        "03/2025": 5,
        "04/2024": 3,
        "01/2024": 2,
        "12/2024": 4,
        "02/2025": 1,
        "05/2024": 6,
        "01/2025": 7
    }
    
    print("Dados originais (ordem do dicionário):")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    print("\nOrdenação alfabética (problema atual):")
    alphabetical = sorted(test_data.keys())
    for key in alphabetical:
        print(f"  {key}: {test_data[key]}")
    
    print("\nOrdenação cronológica (solução atual):")
    def sort_month_year(month_year):
        try:
            month, year = month_year.split('/')
            return (int(year), int(month))
        except:
            return (0, 0)
    
    chronological = sorted(test_data.keys(), key=sort_month_year)
    for key in chronological:
        print(f"  {key}: {test_data[key]}")
    
    print("\nVerificando a função de ordenação:")
    for key in test_data.keys():
        month, year = key.split('/')
        sort_key = (int(year), int(month))
        print(f"  {key} -> {sort_key}")

if __name__ == "__main__":
    test_sorting()