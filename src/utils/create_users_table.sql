-- Script SQL para criar a tabela de usuários no Supabase
-- Execute este script no SQL Editor do Supabase

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Criar índice no email para melhor performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Criar índice no status ativo
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

-- Função para atualizar o campo updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para atualizar updated_at automaticamente
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Inserir um usuário de exemplo (opcional)
-- IMPORTANTE: Altere o email e senha antes de usar em produção
-- A senha 'admin123' será hasheada como: a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3
INSERT INTO users (email, password_hash, name) 
VALUES (
    'admin@financeira.com', 
    'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 
    'Administrador'
) ON CONFLICT (email) DO NOTHING;

-- Comentários sobre a estrutura:
-- id: Chave primária auto-incrementável
-- email: Email único do usuário (usado para login)
-- password_hash: Hash SHA-256 da senha
-- name: Nome completo do usuário (opcional)
-- is_active: Flag para ativar/desativar usuário
-- created_at: Data de criação do registro
-- updated_at: Data da última atualização (atualizada automaticamente)