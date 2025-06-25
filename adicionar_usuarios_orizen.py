#!/usr/bin/env python3
"""
Script para adicionar credenciais de acesso para os emails da Orizen
- vivianitech@orizen.io
- financeiro@orizen.io
"""

import os
import hashlib
from dotenv import load_dotenv
from supabase import create_client

def hash_password(password: str) -> str:
    """Gera hash SHA-256 da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def adicionar_usuarios_orizen():
    """Adiciona os usuários da Orizen ao sistema"""
    
    print("🔧 ADICIONANDO USUÁRIOS ORIZEN")
    print("=" * 50)
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Variáveis SUPABASE_URL ou SUPABASE_KEY não configuradas!")
        return
    
    try:
        # Conectar ao Supabase
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Conectado ao Supabase")
        
        # Definir usuários a serem criados
        usuarios = [
            {
                'email': 'vivianitech@orizen.io',
                'password': 'orizen2025',  # Senha padrão - deve ser alterada no primeiro login
                'name': 'Viviani Tech - Orizen',
                'is_active': True
            },
            {
                'email': 'financeiro@orizen.io', 
                'password': 'orizen2025',  # Senha padrão - deve ser alterada no primeiro login
                'name': 'Financeiro - Orizen',
                'is_active': True
            }
        ]
        
        print(f"\n👥 Adicionando {len(usuarios)} usuários:")
        
        for usuario in usuarios:
            email = usuario['email']
            password = usuario['password']
            name = usuario['name']
            is_active = usuario['is_active']
            
            print(f"\n🔄 Processando: {email}")
            
            # Gerar hash da senha
            password_hash = hash_password(password)
            
            # Verificar se o usuário já existe
            response = supabase.table('users').select('id, email').eq('email', email).execute()
            
            if response.data:
                # Usuário já existe, atualizar
                user_id = response.data[0]['id']
                user_data = {
                    'password_hash': password_hash,
                    'name': name,
                    'is_active': is_active
                }
                
                response = supabase.table('users').update(user_data).eq('id', user_id).execute()
                print(f"✅ Usuário {email} atualizado!")
                
            else:
                # Usuário não existe, criar
                user_data = {
                    'email': email,
                    'password_hash': password_hash,
                    'name': name,
                    'is_active': is_active
                }
                
                response = supabase.table('users').insert(user_data).execute()
                print(f"✅ Usuário {email} criado!")
            
            print(f"   Nome: {name}")
            print(f"   Senha: {password}")
            print(f"   Status: {'Ativo' if is_active else 'Inativo'}")
        
        print(f"\n🎉 PROCESSO CONCLUÍDO!")
        print(f"✅ Todos os usuários da Orizen foram adicionados com sucesso!")
        
        print(f"\n📋 CREDENCIAIS DE ACESSO:")
        print(f"=" * 50)
        for usuario in usuarios:
            print(f"Email: {usuario['email']}")
            print(f"Senha: {usuario['password']}")
            print(f"Nome: {usuario['name']}")
            print("-" * 30)
        
        print(f"\n⚠️  IMPORTANTE:")
        print(f"- As senhas padrão são temporárias")
        print(f"- Recomenda-se alterar as senhas no primeiro login")
        print(f"- Todos os usuários estão ativos e podem fazer login")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def verificar_usuarios_orizen():
    """Verifica se os usuários da Orizen foram criados corretamente"""
    
    print("\n🔍 VERIFICANDO USUÁRIOS ORIZEN")
    print("=" * 50)
    
    load_dotenv()
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    try:
        supabase = create_client(supabase_url, supabase_key)
        
        emails_orizen = ['vivianitech@orizen.io', 'financeiro@orizen.io']
        
        for email in emails_orizen:
            print(f"\n🔍 Verificando: {email}")
            
            response = supabase.table('users').select('*').eq('email', email).execute()
            
            if response.data:
                user = response.data[0]
                print(f"✅ Usuário encontrado!")
                print(f"   ID: {user.get('id')}")
                print(f"   Nome: {user.get('name')}")
                print(f"   Ativo: {user.get('is_active')}")
                print(f"   Criado em: {user.get('created_at')}")
            else:
                print(f"❌ Usuário não encontrado!")
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")

def main():
    """Função principal"""
    
    print("SISTEMA DE GERENCIAMENTO DE USUÁRIOS - ORIZEN")
    print("=" * 60)
    print("Este script irá adicionar credenciais para:")
    print("• vivianitech@orizen.io")
    print("• financeiro@orizen.io")
    print("=" * 60)
    
    resposta = input("\nDeseja prosseguir com a criação dos usuários? (s/n): ").lower().strip()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        adicionar_usuarios_orizen()
        
        print("\n" + "=" * 50)
        resposta2 = input("Deseja verificar se os usuários foram criados? (s/n): ").lower().strip()
        
        if resposta2 in ['s', 'sim', 'y', 'yes']:
            verificar_usuarios_orizen()
    else:
        print("👋 Operação cancelada!")

if __name__ == "__main__":
    main()