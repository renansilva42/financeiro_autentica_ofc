import os
from supabase import create_client, Client
from typing import Optional, Dict, Any
import hashlib
import secrets

class AuthService:
    def __init__(self):
        """Inicializa o serviço de autenticação com Supabase"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidas no arquivo .env")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica um usuário com email e senha
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            
        Returns:
            Dict com dados do usuário se autenticado, None caso contrário
        """
        try:
            # Hash da senha para comparação (assumindo que as senhas estão hasheadas na base)
            password_hash = self._hash_password(password)
            
            # Busca o usuário na tabela de usuários
            response = self.supabase.table('users').select('*').eq('email', email).execute()
            
            if not response.data:
                return None
            
            user = response.data[0]
            
            # Verifica se a senha está correta
            # Assumindo que você tem uma coluna 'password_hash' na tabela
            if user.get('password_hash') == password_hash or user.get('password') == password:
                # Remove a senha dos dados retornados por segurança
                user_data = {k: v for k, v in user.items() if k not in ['password', 'password_hash']}
                return user_data
            
            return None
            
        except Exception as e:
            print(f"Erro na autenticação: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca um usuário pelo ID
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dict com dados do usuário se encontrado, None caso contrário
        """
        try:
            response = self.supabase.table('users').select('*').eq('id', user_id).execute()
            
            if response.data:
                user = response.data[0]
                # Remove a senha dos dados retornados por segurança
                user_data = {k: v for k, v in user.items() if k not in ['password', 'password_hash']}
                return user_data
            
            return None
            
        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
            return None
    
    def create_user(self, email: str, password: str, name: str = None) -> Optional[Dict[str, Any]]:
        """
        Cria um novo usuário (para uso administrativo)
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            name: Nome do usuário (opcional)
            
        Returns:
            Dict com dados do usuário criado se sucesso, None caso contrário
        """
        try:
            password_hash = self._hash_password(password)
            
            user_data = {
                'email': email,
                'password_hash': password_hash,
                'name': name,
                'created_at': 'now()',
                'is_active': True
            }
            
            response = self.supabase.table('users').insert(user_data).execute()
            
            if response.data:
                user = response.data[0]
                # Remove a senha dos dados retornados por segurança
                user_data = {k: v for k, v in user.items() if k not in ['password', 'password_hash']}
                return user_data
            
            return None
            
        except Exception as e:
            print(f"Erro ao criar usuário: {e}")
            return None
    
    def _hash_password(self, password: str) -> str:
        """
        Gera hash da senha usando SHA-256
        
        Args:
            password: Senha em texto plano
            
        Returns:
            Hash da senha
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_session_token(self) -> str:
        """
        Gera um token de sessão seguro
        
        Returns:
            Token de sessão
        """
        return secrets.token_urlsafe(32)
    
    def validate_email(self, email: str) -> bool:
        """
        Valida formato do email
        
        Args:
            email: Email para validar
            
        Returns:
            True se válido, False caso contrário
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None