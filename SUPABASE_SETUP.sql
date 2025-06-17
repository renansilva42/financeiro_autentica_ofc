-- =====================================================
-- SCRIPT SQL PARA CONFIGURAÇÃO COMPLETA DO SUPABASE
-- Financeira Autêntica - Sistema de Autenticação
-- =====================================================
-- 
-- INSTRUÇÕES:
-- 1. Acesse seu projeto no Supabase
-- 2. Vá em "SQL Editor"
-- 3. Cole e execute este script completo
-- 4. Verifique se todas as tabelas foram criadas
--
-- =====================================================

-- =====================================================
-- 1. CRIAR TABELA DE USUÁRIOS
-- =====================================================

-- Remover tabela se existir (apenas para desenvolvimento)
-- DROP TABLE IF EXISTS users CASCADE;

-- Criar tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 2. CRIAR ÍNDICES PARA PERFORMANCE
-- =====================================================

-- Índice único no email (principal campo de busca)
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_unique ON users(email);

-- Índice no status ativo
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

-- Índice composto para consultas de login
CREATE INDEX IF NOT EXISTS idx_users_login ON users(email, is_active) WHERE is_active = true;

-- Índice na data de criação
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- =====================================================
-- 3. CRIAR FUNÇÕES AUXILIARES
-- =====================================================

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

-- Função para validar email
CREATE OR REPLACE FUNCTION validate_email(email_input TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN email_input ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';
END;
$$ LANGUAGE 'plpgsql';

-- =====================================================
-- 4. CRIAR TRIGGERS
-- =====================================================

-- Trigger para atualizar updated_at automaticamente
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger para validar email antes de inserir/atualizar
CREATE OR REPLACE FUNCTION validate_user_email()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT validate_email(NEW.email) THEN
        RAISE EXCEPTION 'Email inválido: %', NEW.email;
    END IF;
    
    -- Converter email para lowercase
    NEW.email = LOWER(NEW.email);
    
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

DROP TRIGGER IF EXISTS validate_user_email_trigger ON users;
CREATE TRIGGER validate_user_email_trigger
    BEFORE INSERT OR UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION validate_user_email();

-- =====================================================
-- 5. CONFIGURAR ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Habilitar RLS na tabela users
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Política para permitir leitura apenas para usuários autenticados
CREATE POLICY "Users can view their own data" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

-- Política para permitir inserção de novos usuários (registro)
CREATE POLICY "Enable insert for service role" ON users
    FOR INSERT WITH CHECK (true);

-- Política para permitir atualização apenas do próprio perfil
CREATE POLICY "Users can update their own data" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

-- =====================================================
-- 6. INSERIR DADOS INICIAIS
-- =====================================================

-- Inserir usuário administrador padrão
-- IMPORTANTE: Altere email e senha em produção!
-- Senha: admin123 (hash SHA-256)
INSERT INTO users (email, password_hash, name, is_active) 
VALUES (
    'admin@financeira.com', 
    'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 
    'Administrador do Sistema',
    true
) ON CONFLICT (email) DO UPDATE SET
    password_hash = EXCLUDED.password_hash,
    name = EXCLUDED.name,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- Inserir usuário de teste (opcional)
INSERT INTO users (email, password_hash, name, is_active) 
VALUES (
    'teste@financeira.com', 
    'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 
    'Usuário de Teste',
    true
) ON CONFLICT (email) DO NOTHING;

-- =====================================================
-- 7. CRIAR VIEWS ÚTEIS
-- =====================================================

-- View para estatísticas de usuários
CREATE OR REPLACE VIEW user_stats AS
SELECT 
    COUNT(*) as total_users,
    COUNT(*) FILTER (WHERE is_active = true) as active_users,
    COUNT(*) FILTER (WHERE is_active = false) as inactive_users,
    COUNT(*) FILTER (WHERE last_login IS NOT NULL) as users_with_login,
    COUNT(*) FILTER (WHERE last_login > NOW() - INTERVAL '30 days') as active_last_30_days,
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '7 days') as new_users_last_week
FROM users;

-- View para usuários ativos (sem dados sensíveis)
CREATE OR REPLACE VIEW active_users AS
SELECT 
    id,
    email,
    name,
    last_login,
    created_at,
    updated_at
FROM users 
WHERE is_active = true;

-- =====================================================
-- 8. CRIAR FUNÇÕES DE UTILIDADE
-- =====================================================

-- Função para contar tentativas de login
CREATE OR REPLACE FUNCTION increment_login_attempts(user_email TEXT)
RETURNS VOID AS $$
BEGIN
    UPDATE users 
    SET 
        login_attempts = login_attempts + 1,
        locked_until = CASE 
            WHEN login_attempts >= 4 THEN NOW() + INTERVAL '15 minutes'
            ELSE locked_until
        END,
        updated_at = NOW()
    WHERE email = LOWER(user_email);
END;
$$ LANGUAGE 'plpgsql';

-- Função para resetar tentativas de login
CREATE OR REPLACE FUNCTION reset_login_attempts(user_email TEXT)
RETURNS VOID AS $$
BEGIN
    UPDATE users 
    SET 
        login_attempts = 0,
        locked_until = NULL,
        last_login = NOW(),
        updated_at = NOW()
    WHERE email = LOWER(user_email);
END;
$$ LANGUAGE 'plpgsql';

-- Função para verificar se usuário está bloqueado
CREATE OR REPLACE FUNCTION is_user_locked(user_email TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    user_locked_until TIMESTAMP WITH TIME ZONE;
BEGIN
    SELECT locked_until INTO user_locked_until
    FROM users 
    WHERE email = LOWER(user_email);
    
    RETURN user_locked_until IS NOT NULL AND user_locked_until > NOW();
END;
$$ LANGUAGE 'plpgsql';

-- =====================================================
-- 9. INSERIR DADOS DE EXEMPLO ADICIONAIS (OPCIONAL)
-- =====================================================

-- Usuários de exemplo para desenvolvimento/teste
-- Remova esta seção em produção!

INSERT INTO users (email, password_hash, name, is_active) VALUES
    ('gerente@financeira.com', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'Gerente Financeiro', true),
    ('analista@financeira.com', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'Analista Financeiro', true),
    ('contador@financeira.com', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'Contador', true)
ON CONFLICT (email) DO NOTHING;

-- =====================================================
-- 10. VERIFICAÇÕES FINAIS
-- =====================================================

-- Verificar se a tabela foi criada corretamente
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users') THEN
        RAISE NOTICE '✅ Tabela users criada com sucesso!';
    ELSE
        RAISE EXCEPTION '❌ Erro: Tabela users não foi criada!';
    END IF;
END $$;

-- Verificar se os índices foram criados
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_indexes WHERE tablename = 'users' AND indexname = 'idx_users_email_unique') THEN
        RAISE NOTICE '✅ Índices criados com sucesso!';
    ELSE
        RAISE NOTICE '⚠️  Alguns índices podem não ter sido criados corretamente';
    END IF;
END $$;

-- Verificar se há usuários na tabela
DO $$
DECLARE
    user_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO user_count FROM users;
    RAISE NOTICE '📊 Total de usuários criados: %', user_count;
    
    IF user_count > 0 THEN
        RAISE NOTICE '✅ Usuários de exemplo inseridos com sucesso!';
    ELSE
        RAISE NOTICE '⚠️  Nenhum usuário foi inserido';
    END IF;
END $$;

-- =====================================================
-- INFORMAÇÕES IMPORTANTES
-- =====================================================

/*
🔐 CREDENCIAIS DE ACESSO PADRÃO:

1. Administrador:
   Email: admin@financeira.com
   Senha: admin123

2. Usuário de Teste:
   Email: teste@financeira.com  
   Senha: senha123

3. Outros usuários (todos com senha: admin123):
   - gerente@financeira.com
   - analista@financeira.com
   - contador@financeira.com

⚠️  IMPORTANTE PARA PRODUÇÃO:
- Altere todas as senhas padrão
- Remova usuários de exemplo
- Configure backups automáticos
- Monitore tentativas de login
- Configure alertas de segurança

📋 ESTRUTURA DA TABELA USERS:
- id: Chave primária (BIGSERIAL)
- email: Email único (VARCHAR 255)
- password_hash: Hash SHA-256 da senha
- name: Nome completo (opcional)
- is_active: Status ativo/inativo
- last_login: Último login realizado
- login_attempts: Contador de tentativas
- locked_until: Bloqueio temporário
- created_at: Data de criação
- updated_at: Data de atualização

🛡️  RECURSOS DE SEGURANÇA:
- Row Level Security (RLS) habilitado
- Validação automática de email
- Bloqueio após 5 tentativas de login
- Triggers para auditoria
- Índices otimizados para performance

📊 VIEWS DISPONÍVEIS:
- user_stats: Estatísticas gerais
- active_users: Usuários ativos (sem dados sensíveis)

🔧 FUNÇÕES UTILITÁRIAS:
- increment_login_attempts()
- reset_login_attempts()  
- is_user_locked()
- validate_email()
*/

-- =====================================================
-- FIM DO SCRIPT
-- =====================================================

SELECT '🎉 CONFIGURAÇÃO DO SUPABASE CONCLUÍDA COM SUCESSO!' as status;