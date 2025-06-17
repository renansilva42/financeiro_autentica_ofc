from functools import wraps
from flask import session, redirect, url_for, request, flash
import os

def login_required(f):
    """
    Decorador que exige que o usuário esteja logado para acessar a rota
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Se não há configuração do Supabase, pular autenticação
        if not os.getenv('SUPABASE_URL') or os.getenv('SUPABASE_URL') == 'your_supabase_url_here':
            print("⚠️  Aviso: Autenticação desabilitada - Supabase não configurado")
            return f(*args, **kwargs)
        
        if 'user_id' not in session or not session.get('user_id'):
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            # Salva a URL que o usuário tentou acessar para redirecionar após login
            session['next_url'] = request.url
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def logout_required(f):
    """
    Decorador que redireciona usuários já logados (para páginas como login)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Se não há configuração do Supabase, pular verificação
        if not os.getenv('SUPABASE_URL') or os.getenv('SUPABASE_URL') == 'your_supabase_url_here':
            return f(*args, **kwargs)
            
        if 'user_id' in session and session.get('user_id'):
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function