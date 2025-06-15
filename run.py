#!/usr/bin/env python3
"""
Script de inicialização rápida para a aplicação Financeira Autêntica
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Função principal para iniciar a aplicação"""
    
    # Verificar se estamos no diretório correto
    current_dir = Path.cwd()
    src_dir = current_dir / "src"
    
    if not src_dir.exists():
        print("❌ Erro: Diretório 'src' não encontrado!")
        print("Execute este script a partir do diretório raiz do projeto.")
        sys.exit(1)
    
    # Verificar se o arquivo .env existe
    env_file = current_dir / ".env"
    if not env_file.exists():
        print("❌ Erro: Arquivo '.env' não encontrado!")
        print("Crie o arquivo .env com suas credenciais da API Omie.")
        sys.exit(1)
    
    # Verificar se as dependências estão instaladas
    try:
        import flask
        import requests
        from pydantic_settings import BaseSettings
    except ImportError as e:
        print(f"❌ Erro: Dependência não encontrada: {e}")
        print("Execute: pip install -r requirements.txt")
        sys.exit(1)
    
    print("🚀 Iniciando Financeira Autêntica...")
    print("📊 Sistema de Gestão de Clientes")
    print("-" * 50)
    
    # Mudar para o diretório src
    os.chdir(src_dir)
    
    # Executar a aplicação
    try:
        print("🌐 Servidor iniciando em http://localhost:8000")
        print("📱 Acesse pelo navegador para usar a interface web")
        print("⏹️  Pressione Ctrl+C para parar o servidor")
        print("-" * 50)
        
        subprocess.run([sys.executable, "app.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n👋 Servidor parado pelo usuário")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar a aplicação: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()