#!/usr/bin/env python3
"""
Script automatizado para deploy da Financeira Autêntica
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(command, check=True):
    """Executa comando no terminal"""
    print(f"🔄 Executando: {command}")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro: {e}")
        if e.stderr:
            print(e.stderr)
        return None

def check_requirements():
    """Verifica se todos os requisitos estão atendidos"""
    print("🔍 Verificando requisitos...")
    
    # Verificar arquivos necessários
    required_files = [
        'Procfile',
        'requirements.txt',
        'src/app.py',
        '.env'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Arquivos obrigatórios não encontrados: {missing_files}")
        return False
    
    # Verificar variáveis de ambiente
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'SECRET_KEY',
        'OMIE_APP_KEY',
        'OMIE_APP_SECRET',
        'SUPABASE_URL',
        'SUPABASE_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) in ['your-secret-key-here', 'your_supabase_url_here', 'your_supabase_anon_key_here']:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variáveis de ambiente não configuradas: {missing_vars}")
        return False
    
    print("✅ Todos os requisitos atendidos!")
    return True

def deploy_heroku():
    """Deploy no Heroku"""
    print("\n🚀 DEPLOY NO HEROKU")
    print("-" * 30)
    
    # Verificar se Heroku CLI está instalado
    result = run_command("heroku --version", check=False)
    if not result or result.returncode != 0:
        print("❌ Heroku CLI não está instalado!")
        print("   Instale em: https://devcenter.heroku.com/articles/heroku-cli")
        return False
    
    # Verificar se está logado
    result = run_command("heroku auth:whoami", check=False)
    if not result or result.returncode != 0:
        print("❌ Não está logado no Heroku!")
        print("   Execute: heroku login")
        return False
    
    # Obter nome do app
    app_name = input("Digite o nome do app Heroku (ou Enter para criar novo): ").strip()
    
    if not app_name:
        app_name = input("Digite o nome para o novo app: ").strip()
        if not app_name:
            print("❌ Nome do app é obrigatório!")
            return False
        
        # Criar app
        result = run_command(f"heroku create {app_name}")
        if not result:
            return False
    
    # Configurar variáveis de ambiente
    print("🔧 Configurando variáveis de ambiente...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    env_vars = {
        'SECRET_KEY': os.getenv('SECRET_KEY'),
        'FLASK_ENV': 'production',
        'OMIE_APP_KEY': os.getenv('OMIE_APP_KEY'),
        'OMIE_APP_SECRET': os.getenv('OMIE_APP_SECRET'),
        'BASE_URL': os.getenv('BASE_URL', 'https://app.omie.com.br/api/v1/'),
        'SUPABASE_URL': os.getenv('SUPABASE_URL'),
        'SUPABASE_KEY': os.getenv('SUPABASE_KEY')
    }
    
    for key, value in env_vars.items():
        if value:
            result = run_command(f'heroku config:set {key}="{value}" --app {app_name}')
            if not result:
                return False
    
    # Deploy
    print("📦 Fazendo deploy...")
    result = run_command(f"git push heroku main")
    if not result:
        print("⚠️  Se o erro for de remote, adicione o remote:")
        print(f"   git remote add heroku https://git.heroku.com/{app_name}.git")
        return False
    
    # Abrir app
    run_command(f"heroku open --app {app_name}")
    
    print(f"✅ Deploy concluído! App: https://{app_name}.herokuapp.com")
    return True

def deploy_vercel():
    """Deploy no Vercel"""
    print("\n⚡ DEPLOY NO VERCEL")
    print("-" * 30)
    
    # Verificar se Vercel CLI está instalado
    result = run_command("vercel --version", check=False)
    if not result or result.returncode != 0:
        print("❌ Vercel CLI não está instalado!")
        print("   Execute: npm i -g vercel")
        return False
    
    # Login se necessário
    result = run_command("vercel whoami", check=False)
    if not result or result.returncode != 0:
        print("🔑 Fazendo login no Vercel...")
        result = run_command("vercel login")
        if not result:
            return False
    
    # Deploy
    print("📦 Fazendo deploy...")
    result = run_command("vercel --prod")
    if not result:
        return False
    
    print("✅ Deploy concluído!")
    print("⚠️  Configure as variáveis de ambiente no dashboard do Vercel")
    return True

def deploy_railway():
    """Deploy no Railway"""
    print("\n🚂 DEPLOY NO RAILWAY")
    print("-" * 30)
    
    # Verificar se Railway CLI está instalado
    result = run_command("railway --version", check=False)
    if not result or result.returncode != 0:
        print("❌ Railway CLI não está instalado!")
        print("   Execute: npm install -g @railway/cli")
        return False
    
    # Login se necessário
    result = run_command("railway whoami", check=False)
    if not result or result.returncode != 0:
        print("🔑 Fazendo login no Railway...")
        result = run_command("railway login")
        if not result:
            return False
    
    # Inicializar projeto se necessário
    if not Path("railway.toml").exists():
        result = run_command("railway init")
        if not result:
            return False
    
    # Deploy
    print("📦 Fazendo deploy...")
    result = run_command("railway up")
    if not result:
        return False
    
    print("✅ Deploy concluído!")
    print("⚠️  Configure as variáveis de ambiente no dashboard do Railway")
    return True

def deploy_docker():
    """Deploy com Docker"""
    print("\n🐳 DEPLOY COM DOCKER")
    print("-" * 30)
    
    # Verificar se Docker está instalado
    result = run_command("docker --version", check=False)
    if not result or result.returncode != 0:
        print("❌ Docker não está instalado!")
        return False
    
    # Build da imagem
    print("🔨 Construindo imagem Docker...")
    result = run_command("docker build -t financeira-autentica .")
    if not result:
        return False
    
    # Executar container
    print("🚀 Executando container...")
    result = run_command("docker run -d -p 8000:8000 --env-file .env --name financeira-app financeira-autentica")
    if not result:
        return False
    
    print("✅ Container executando!")
    print("   Acesse: http://localhost:8000")
    print("   Parar: docker stop financeira-app")
    print("   Logs: docker logs financeira-app")
    return True

def main():
    """Função principal"""
    print("🚀 DEPLOY AUTOMATIZADO - FINANCEIRA AUTÊNTICA")
    print("=" * 50)
    
    # Verificar requisitos
    if not check_requirements():
        print("\n❌ Corrija os problemas acima antes de continuar.")
        sys.exit(1)
    
    # Menu de opções
    print("\n📋 OPÇÕES DE DEPLOY:")
    print("1. Heroku")
    print("2. Vercel")
    print("3. Railway")
    print("4. Docker (local)")
    print("5. Sair")
    
    while True:
        choice = input("\nEscolha uma opção (1-5): ").strip()
        
        if choice == '1':
            deploy_heroku()
            break
        elif choice == '2':
            deploy_vercel()
            break
        elif choice == '3':
            deploy_railway()
            break
        elif choice == '4':
            deploy_docker()
            break
        elif choice == '5':
            print("👋 Saindo...")
            break
        else:
            print("❌ Opção inválida! Digite 1-5.")

if __name__ == "__main__":
    main()