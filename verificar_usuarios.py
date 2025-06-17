#!/usr/bin/env python3
"""
Script para verificar usuários na tabela do Supabase
"""

import os
import hashlib
from dotenv import load_dotenv
from supabase import create_client

def hash_password(password: str) -> str:
    """Gera hash SHA-256 da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_usuarios():
    """Verifica usuários na tabela"""
    
    print("🔍 VERIFICANDO USUÁRIOS NO SUPABASE")
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
        
        # Verificar se a tabela users existe
        try:
            response = supabase.table('users').select('*').execute()
            print(f"✅ Tabela 'users' encontrada")
            
            users = response.data
            print(f"📊 Total de usuários: {len(users)}")
            
            if users:
                print("\n👥 USUÁRIOS ENCONTRADOS:")
                for i, user in enumerate(users, 1):
                    print(f"   {i}. ID: {user.get('id')}")
                    print(f"      Email: {user.get('email')}")
                    print(f"      Nome: {user.get('name', 'Não informado')}")
                    print(f"      Ativo: {user.get('is_active', False)}")
                    print(f"      Hash da senha: {user.get('password_hash', 'N/A')[:20]}...")
                    print(f"      Criado em: {user.get('created_at', 'N/A')}")
                    print()
            else:
                print("⚠️  Nenhum usuário encontrado na tabela!")
                
        except Exception as e:
            if 'relation "public.users" does not exist' in str(e):
                print("❌ Tabela 'users' não existe!")
                print("   Execute o script SQL para criar a tabela")
                return
            else:
                raise e
        
        # Verificar usuário admin específico
        print("🔍 VERIFICANDO USUÁRIO ADMIN:")
        admin_email = 'admin@financeira.com'
        admin_password = 'admin123'
        admin_hash = hash_password(admin_password)
        
        print(f"   Email procurado: {admin_email}")
        print(f"   Senha: {admin_password}")
        print(f"   Hash esperado: {admin_hash}")
        
        # Buscar usuário admin
        response = supabase.table('users').select('*').eq('email', admin_email).execute()
        
        if response.data:
            admin_user = response.data[0]
            print(f"✅ Usuário admin encontrado!")
            print(f"   Hash no banco: {admin_user.get('password_hash')}")
            
            if admin_user.get('password_hash') == admin_hash:
                print("✅ Hash da senha está correto!")
            else:
                print("❌ Hash da senha está incorreto!")
                print("   Será necessário atualizar a senha")
                
            if admin_user.get('is_active'):
                print("✅ Usuário está ativo")
            else:
                print("❌ Usuário está inativo")
                
        else:
            print("❌ Usuário admin não encontrado!")
            print("   Será necessário criar o usuário")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def criar_usuario_admin():
    """Cria ou atualiza o usuário admin"""
    
    print("\n🔧 CRIANDO/ATUALIZANDO USUÁRIO ADMIN")
    print("-" * 40)
    
    load_dotenv()
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    try:
        supabase = create_client(supabase_url, supabase_key)
        
        admin_email = 'admin@financeira.com'
        admin_password = 'admin123'
        admin_hash = hash_password(admin_password)
        
        # Tentar inserir ou atualizar
        user_data = {
            'email': admin_email,
            'password_hash': admin_hash,
            'name': 'Administrador',
            'is_active': True
        }
        
        # Primeiro, tentar atualizar se existir
        response = supabase.table('users').select('id').eq('email', admin_email).execute()
        
        if response.data:
            # Usuário existe, atualizar
            user_id = response.data[0]['id']
            response = supabase.table('users').update(user_data).eq('id', user_id).execute()
            print(f"✅ Usuário admin atualizado!")
        else:
            # Usuário não existe, criar
            response = supabase.table('users').insert(user_data).execute()
            print(f"✅ Usuário admin criado!")
            
        print(f"   Email: {admin_email}")
        print(f"   Senha: {admin_password}")
        print(f"   Hash: {admin_hash}")
        
    except Exception as e:
        print(f"❌ Erro ao criar/atualizar usuário: {e}")

def testar_autenticacao():
    """Testa a autenticação do usuário admin"""
    
    print("\n🧪 TESTANDO AUTENTICAÇÃO")
    print("-" * 30)
    
    try:
        # Importar o serviço de autenticação
        import sys
        sys.path.append('src')
        from services.auth_service import AuthService
        
        auth_service = AuthService()
        
        admin_email = 'admin@financeira.com'
        admin_password = 'admin123'
        
        print(f"Testando login com:")
        print(f"   Email: {admin_email}")
        print(f"   Senha: {admin_password}")
        
        user = auth_service.authenticate_user(admin_email, admin_password)
        
        if user:
            print("✅ Autenticação bem-sucedida!")
            print(f"   Usuário: {user}")
        else:
            print("❌ Falha na autenticação!")
            
    except Exception as e:
        print(f"❌ Erro no teste de autenticação: {e}")

def main():
    """Função principal"""
    
    verificar_usuarios()
    
    print("\n" + "=" * 50)
    resposta = input("Deseja criar/atualizar o usuário admin? (s/n): ").lower().strip()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        criar_usuario_admin()
        
        print("\n" + "=" * 50)
        resposta2 = input("Deseja testar a autenticação? (s/n): ").lower().strip()
        
        if resposta2 in ['s', 'sim', 'y', 'yes']:
            testar_autenticacao()

if __name__ == "__main__":
    main()