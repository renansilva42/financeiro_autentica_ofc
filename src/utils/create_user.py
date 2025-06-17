#!/usr/bin/env python3
"""
Script para criar usuários no sistema
Execute este script para criar novos usuários ou gerar hashes de senha
"""

import sys
import os
import hashlib
from dotenv import load_dotenv

# Adicionar o diretório src ao path para importar os serviços
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.auth_service import AuthService

def hash_password(password: str) -> str:
    """Gera hash SHA-256 da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user_interactive():
    """Cria um usuário de forma interativa"""
    print("=== Criador de Usuários - Financeira Autêntica ===\n")
    
    try:
        # Carregar variáveis de ambiente
        load_dotenv()
        
        # Verificar se as variáveis do Supabase estão configuradas
        if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_KEY'):
            print("❌ Erro: Variáveis SUPABASE_URL e SUPABASE_KEY não estão configuradas no arquivo .env")
            print("Por favor, configure essas vari��veis antes de continuar.")
            return
        
        if os.getenv('SUPABASE_URL') == 'your_supabase_url_here':
            print("❌ Erro: Por favor, configure a SUPABASE_URL real no arquivo .env")
            return
            
        if os.getenv('SUPABASE_KEY') == 'your_supabase_anon_key_here':
            print("❌ Erro: Por favor, configure a SUPABASE_KEY real no arquivo .env")
            return
        
        # Inicializar o serviço de autenticação
        auth_service = AuthService()
        
        # Coletar dados do usuário
        email = input("Email do usuário: ").strip()
        if not email:
            print("❌ Email é obrigatório!")
            return
        
        if not auth_service.validate_email(email):
            print("❌ Formato de email inválido!")
            return
        
        name = input("Nome completo (opcional): ").strip()
        if not name:
            name = None
        
        password = input("Senha: ").strip()
        if not password:
            print("❌ Senha é obrigatória!")
            return
        
        if len(password) < 6:
            print("❌ Senha deve ter pelo menos 6 caracteres!")
            return
        
        # Confirmar senha
        password_confirm = input("Confirme a senha: ").strip()
        if password != password_confirm:
            print("❌ Senhas não coincidem!")
            return
        
        # Criar o usuário
        print("\n🔄 Criando usuário...")
        user = auth_service.create_user(email, password, name)
        
        if user:
            print(f"✅ Usuário criado com sucesso!")
            print(f"   ID: {user['id']}")
            print(f"   Email: {user['email']}")
            print(f"   Nome: {user.get('name', 'Não informado')}")
            print(f"   Criado em: {user.get('created_at', 'N/A')}")
        else:
            print("❌ Erro ao criar usuário. Verifique se o email já não está em uso.")
    
    except Exception as e:
        print(f"❌ Erro: {e}")

def generate_password_hash():
    """Gera hash de uma senha para uso manual"""
    print("=== Gerador de Hash de Senha ===\n")
    
    password = input("Digite a senha para gerar o hash: ").strip()
    if not password:
        print("❌ Senha é obrigatória!")
        return
    
    password_hash = hash_password(password)
    print(f"\n📋 Hash SHA-256 da senha:")
    print(f"   {password_hash}")
    print(f"\n💡 Use este hash na coluna 'password_hash' da tabela 'users'")

def main():
    """Função principal"""
    print("Escolha uma opção:")
    print("1. Criar usuário via API")
    print("2. Gerar hash de senha")
    print("3. Sair")
    
    choice = input("\nOpção (1-3): ").strip()
    
    if choice == '1':
        create_user_interactive()
    elif choice == '2':
        generate_password_hash()
    elif choice == '3':
        print("👋 Até logo!")
    else:
        print("❌ Opção inválida!")

if __name__ == "__main__":
    main()