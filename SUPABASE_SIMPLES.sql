-- =====================================================
-- CONFIGURAÇÃO SIMPLES DO SUPABASE
-- Financeira Autêntica - Versão Básica
-- =====================================================
--
-- INSTRUÇÕES:
-- 1. Acesse seu projeto no Supabase
-- 2. Vá em "SQL Editor" 
-- 3. Cole e execute este script
--
-- =====================================================

-- Criar tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Criar índices básicos
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

-- Função para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

-- Trigger para updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Inserir usuário administrador
-- Email: admin@financeira.com
-- Senha: admin123
INSERT INTO users (email, password_hash, name) 
VALUES (
    'admin@financeira.com', 
    '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 
    'Administrador'
) ON CONFLICT (email) DO NOTHING;

-- Verificar se funcionou
SELECT 
    'Tabela criada com sucesso!' as status,
    COUNT(*) as total_usuarios
FROM users;

-- =====================================================
-- CREDENCIAIS DE ACESSO:
-- Email: admin@financeira.com
-- Senha: admin123
-- 
-- ⚠️ ALTERE A SENHA EM PRODUÇÃO!
-- =====================================================