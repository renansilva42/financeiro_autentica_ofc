#!/usr/bin/env python3
"""
Script de diagnóstico para verificar a configuração do Supabase
"""

import os
import sys
from dotenv import load_dotenv

def verificar_configuracao():
    """Verifica se a configuração do Supabase está correta"""
    
    print("🔍 DIAGNÓSTICO DA CONFIGURAÇÃO DO SUPABASE")
    print("=" * 50)
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Verificar arquivo .env
    env_path = '.env'
    if os.path.exists(env_path):
        print(f"✅ Arquivo {env_path} encontrado")
    else:
        print(f"❌ Arquivo {env_path} não encontrado!")
        return False
    
    # Verificar variáveis do Supabase
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    print(f"\n📋 VARIÁVEIS DE AMBIENTE:")
    print(f"   SUPABASE_URL: {supabase_url}")
    print(f"   SUPABASE_KEY: {'*' * 20 if supabase_key else 'Não definida'}")
    
    # Verificar se as variáveis estão definidas
    if not supabase_url:
        print("❌ SUPABASE_URL não está definida!")
        return False
    
    if not supabase_key:
        print("❌ SUPABASE_KEY não está definida!")
        return False
    
    # Verificar se as variáveis não são os valores padrão
    if supabase_url == 'your_supabase_url_here':
        print("❌ SUPABASE_URL ainda tem o valor padrão!")
        print("   Configure com a URL real do seu projeto Supabase")
        return False
    
    if supabase_key == 'your_supabase_anon_key_here':
        print("❌ SUPABASE_KEY ainda tem o valor padrão!")
        print("   Configure com a chave anon/public do seu projeto Supabase")
        return False
    
    # Verificar formato da URL
    if not supabase_url.startswith('https://'):
        print("❌ SUPABASE_URL deve começar com 'https://'")
        return False
    
    if not '.supabase.co' in supabase_url:
        print("❌ SUPABASE_URL deve conter '.supabase.co'")
        return False
    
    print("✅ Variáveis de ambiente configuradas corretamente")
    
    # Testar conexão com Supabase
    print(f"\n🔗 TESTANDO CONEXÃO COM SUPABASE:")
    try:
        from supabase import create_client
        client = create_client(supabase_url, supabase_key)
        print("✅ Cliente Supabase criado com sucesso")
        
        # Testar uma consulta simples
        try:
            # Tentar listar tabelas (isso pode falhar se não houver tabelas)
            response = client.table('users').select('count').execute()
            print("✅ Conexão com Supabase funcionando")
            print(f"   Tabela 'users' encontrada")
        except Exception as e:
            if 'relation "public.users" does not exist' in str(e):
                print("⚠️  Tabela 'users' não existe ainda")
                print("   Execute o script SQL para criar a tabela")
            else:
                print(f"⚠️  Erro ao consultar tabela: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar com Supabase: {e}")
        return False

def mostrar_solucoes():
    """Mostra soluções para problemas comuns"""
    
    print(f"\n🛠️  SOLUÇÕES PARA PROBLEMAS COMUNS:")
    print("-" * 40)
    
    print("1️⃣  Se SUPABASE_URL ou SUPABASE_KEY não estão configuradas:")
    print("   - Acesse https://supabase.com")
    print("   - Faça login e acesse seu projeto")
    print("   - Vá em Settings > API")
    print("   - Copie a URL e a anon/public key")
    print("   - Atualize o arquivo .env")
    print()
    
    print("2️⃣  Se a tabela 'users' não existe:")
    print("   - Execute o arquivo SUPABASE_SETUP.sql ou SUPABASE_SIMPLES.sql")
    print("   - No Supabase Dashboard > SQL Editor")
    print("   - Cole o conteúdo do arquivo e execute")
    print()
    
    print("3️⃣  Se há erro de URL inválida:")
    print("   - Verifique se a URL está no formato:")
    print("   - https://seu-projeto.supabase.co")
    print("   - Sem barras extras no final")
    print()
    
    print("4️⃣  Se há erro de autenticação:")
    print("   - Verifique se a chave é a 'anon/public' key")
    print("   - Não use a 'service_role' key para o frontend")
    print()

def main():
    """Função principal"""
    
    sucesso = verificar_configuracao()
    
    if sucesso:
        print(f"\n🎉 CONFIGURAÇÃO OK!")
        print("   Sua aplicação deve funcionar corretamente")
        print("   Execute: python src/app.py")
    else:
        print(f"\n❌ PROBLEMAS ENCONTRADOS!")
        mostrar_solucoes()
    
    print(f"\n" + "=" * 50)

if __name__ == "__main__":
    main()