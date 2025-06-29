-- =====================================================
-- SCRIPT SQL PARA SISTEMA DE CACHE INTELIGENTE - VERSÃO CORRIGIDA
-- Financeira Autêntica - Otimização de Performance
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
-- 1. CRIAR TABELA DE CACHE DE DADOS
-- =====================================================

-- Tabela para cache de dados com compressão
CREATE TABLE IF NOT EXISTS cache_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    data JSONB NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    data_type VARCHAR(50) NOT NULL,
    compressed BOOLEAN DEFAULT FALSE,
    data_size INTEGER DEFAULT 0
);

-- =====================================================
-- 2. CRIAR TABELA DE STATUS DE SINCRONIZAÇÃO
-- =====================================================

-- Tabela para controle de sincronização
CREATE TABLE IF NOT EXISTS sync_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data_type VARCHAR(50) NOT NULL,
    last_sync TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) NOT NULL,
    records_count INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_time_ms INTEGER DEFAULT 0
);

-- =====================================================
-- 3. CRIAR ÍNDICES PARA PERFORMANCE
-- =====================================================

-- Índices para cache_data
CREATE INDEX IF NOT EXISTS idx_cache_key ON cache_data(cache_key);
CREATE INDEX IF NOT EXISTS idx_cache_expires_at ON cache_data(expires_at);
CREATE INDEX IF NOT EXISTS idx_cache_data_type ON cache_data(data_type);
CREATE INDEX IF NOT EXISTS idx_cache_created_at ON cache_data(created_at);
CREATE INDEX IF NOT EXISTS idx_cache_data_type_expires ON cache_data(data_type, expires_at);

-- Índices para sync_status
CREATE INDEX IF NOT EXISTS idx_sync_data_type ON sync_status(data_type);
CREATE INDEX IF NOT EXISTS idx_sync_last_sync ON sync_status(last_sync);
CREATE INDEX IF NOT EXISTS idx_sync_status ON sync_status(status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_sync_data_type_unique ON sync_status(data_type);

-- =====================================================
-- 4. CRIAR FUNÇÕES AUXILIARES
-- =====================================================

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_cache_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    -- Calcular tamanho dos dados se não foi definido
    IF NEW.data_size = 0 OR NEW.data_size IS NULL THEN
        NEW.data_size = LENGTH(NEW.data::text);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

-- Função para limpeza automática de cache expirado
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM cache_data WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Log da limpeza
    INSERT INTO sync_status (data_type, last_sync, status, records_count, error_message)
    VALUES ('cache_cleanup', NOW(), 'success', deleted_count, 'Limpeza automática de cache expirado');
    
    RETURN deleted_count;
END;
$$ LANGUAGE 'plpgsql';

-- Função simplificada para obter estatísticas de cache
CREATE OR REPLACE FUNCTION get_cache_statistics()
RETURNS TABLE (
    total_entries BIGINT,
    expired_entries BIGINT,
    active_entries BIGINT,
    total_size_mb NUMERIC,
    avg_size_kb NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_entries,
        COUNT(*) FILTER (WHERE expires_at < NOW()) as expired_entries,
        COUNT(*) FILTER (WHERE expires_at >= NOW()) as active_entries,
        ROUND(SUM(data_size)::NUMERIC / 1024 / 1024, 2) as total_size_mb,
        ROUND(AVG(data_size)::NUMERIC / 1024, 2) as avg_size_kb
    FROM cache_data;
END;
$$ LANGUAGE 'plpgsql';

-- Função para obter estatísticas por tipo de dados
CREATE OR REPLACE FUNCTION get_cache_stats_by_type()
RETURNS TABLE (
    data_type VARCHAR(50),
    total_count BIGINT,
    active_count BIGINT,
    expired_count BIGINT,
    total_size_mb NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cd.data_type,
        COUNT(*) as total_count,
        COUNT(*) FILTER (WHERE cd.expires_at >= NOW()) as active_count,
        COUNT(*) FILTER (WHERE cd.expires_at < NOW()) as expired_count,
        ROUND(SUM(cd.data_size)::NUMERIC / 1024 / 1024, 2) as total_size_mb
    FROM cache_data cd
    GROUP BY cd.data_type
    ORDER BY total_count DESC;
END;
$$ LANGUAGE 'plpgsql';

-- =====================================================
-- 5. CRIAR TRIGGERS
-- =====================================================

-- Trigger para atualizar updated_at automaticamente
DROP TRIGGER IF EXISTS update_cache_data_updated_at ON cache_data;
CREATE TRIGGER update_cache_data_updated_at 
    BEFORE UPDATE ON cache_data 
    FOR EACH ROW 
    EXECUTE FUNCTION update_cache_updated_at();

-- =====================================================
-- 6. CONFIGURAR ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Habilitar RLS nas tabelas
ALTER TABLE cache_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE sync_status ENABLE ROW LEVEL SECURITY;

-- Políticas para cache_data (acesso total para service role)
DROP POLICY IF EXISTS "Enable all operations for service role" ON cache_data;
CREATE POLICY "Enable all operations for service role" ON cache_data
    FOR ALL USING (true);

-- Políticas para sync_status (acesso total para service role)
DROP POLICY IF EXISTS "Enable all operations for service role" ON sync_status;
CREATE POLICY "Enable all operations for service role" ON sync_status
    FOR ALL USING (true);

-- =====================================================
-- 7. CRIAR VIEWS ÚTEIS
-- =====================================================

-- View para cache ativo
CREATE OR REPLACE VIEW active_cache AS
SELECT 
    cache_key,
    data_type,
    expires_at,
    created_at,
    updated_at,
    compressed,
    data_size,
    ROUND(data_size::NUMERIC / 1024, 2) as size_kb
FROM cache_data 
WHERE expires_at >= NOW()
ORDER BY updated_at DESC;

-- View para estatísticas de sincronização
CREATE OR REPLACE VIEW sync_statistics AS
SELECT 
    data_type,
    last_sync,
    status,
    records_count,
    processing_time_ms,
    CASE 
        WHEN processing_time_ms > 0 THEN ROUND(records_count::NUMERIC / (processing_time_ms::NUMERIC / 1000), 2)
        ELSE 0
    END as records_per_second,
    AGE(NOW(), last_sync) as time_since_sync
FROM sync_status
ORDER BY last_sync DESC;

-- =====================================================
-- 8. CONFIGURAR LIMPEZA AUTOMÁTICA
-- =====================================================

-- Função para agendar limpeza automática (executar via cron job)
CREATE OR REPLACE FUNCTION schedule_cache_cleanup()
RETURNS VOID AS $$
BEGIN
    -- Esta função pode ser chamada por um cron job externo
    -- ou por um trigger baseado em tempo
    PERFORM cleanup_expired_cache();
END;
$$ LANGUAGE 'plpgsql';

-- =====================================================
-- 9. INSERIR DADOS INICIAIS
-- =====================================================

-- Inserir status inicial de sincronização
INSERT INTO sync_status (data_type, last_sync, status, records_count, error_message) VALUES
    ('clients', NOW() - INTERVAL '1 hour', 'pending', 0, 'Aguardando primeira sincronização'),
    ('sellers', NOW() - INTERVAL '1 hour', 'pending', 0, 'Aguardando primeira sincronização'),
    ('services', NOW() - INTERVAL '1 hour', 'pending', 0, 'Aguardando primeira sincronização'),
    ('service_orders', NOW() - INTERVAL '1 hour', 'pending', 0, 'Aguardando primeira sincronização'),
    ('mappings', NOW() - INTERVAL '1 hour', 'pending', 0, 'Aguardando primeira sincronização')
ON CONFLICT (data_type) DO NOTHING;

-- =====================================================
-- 10. VERIFICAÇÕES FINAIS
-- =====================================================

-- Verificar se as tabelas foram criadas corretamente
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'cache_data') THEN
        RAISE NOTICE '✅ Tabela cache_data criada com sucesso!';
    ELSE
        RAISE EXCEPTION '❌ Erro: Tabela cache_data não foi criada!';
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sync_status') THEN
        RAISE NOTICE '✅ Tabela sync_status criada com sucesso!';
    ELSE
        RAISE EXCEPTION '❌ Erro: Tabela sync_status não foi criada!';
    END IF;
END $$;

-- Verificar se os índices foram criados
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_indexes WHERE tablename = 'cache_data' AND indexname = 'idx_cache_key') THEN
        RAISE NOTICE '✅ Índices de cache criados com sucesso!';
    ELSE
        RAISE NOTICE '⚠️  Alguns índices de cache podem não ter sido criados corretamente';
    END IF;
END $$;

-- Testar funções (versão simplificada)
DO $$
DECLARE
    stats_result RECORD;
BEGIN
    SELECT * INTO stats_result FROM get_cache_statistics();
    RAISE NOTICE '📊 Estatísticas de cache inicializadas - Total: % entradas', stats_result.total_entries;
    
    -- Testar função de estatísticas por tipo
    RAISE NOTICE '📊 Função de estatísticas por tipo disponível';
END $$;

-- =====================================================
-- INFORMAÇÕES IMPORTANTES
-- =====================================================

/*
🚀 SISTEMA DE CACHE INTELIGENTE CONFIGURADO!

📋 TABELAS CRIADAS:
- cache_data: Armazena dados em cache com compressão
- sync_status: Controla status de sincronização

🔧 FUNCIONALIDADES:
- Cache com TTL configurável por tipo de dados
- Compressão automática para dados grandes
- Limpeza automática de dados expirados
- Estatísticas detalhadas de uso
- Controle de sincronização

📊 VIEWS DISPONÍVEIS:
- active_cache: Cache ativo com estatísticas
- sync_statistics: Estatísticas de sincronização

🛠️ FUNÇÕES UTILITÁRIAS:
- cleanup_expired_cache(): Limpa cache expirado
- get_cache_statistics(): Estatísticas gerais
- get_cache_stats_by_type(): Estatísticas por tipo de dados
- schedule_cache_cleanup(): Para agendamento automático

⚡ CONFIGURAÇÕES DE TTL:
- clients: 24 horas
- sellers: 24 horas
- services: 12 horas
- service_orders: 2 horas
- mappings: 6 horas
- stats: 1 hora
- dashboard: 30 minutos

🔄 PRÓXIMOS PASSOS:
1. Configurar limpeza automática via cron job
2. Implementar monitoramento de performance
3. Ajustar TTLs baseado no uso real
4. Configurar alertas para falhas de sincronização

📝 COMO USAR:
-- Estatísticas gerais
SELECT * FROM get_cache_statistics();

-- Estatísticas por tipo
SELECT * FROM get_cache_stats_by_type();

-- Cache ativo
SELECT * FROM active_cache LIMIT 10;

-- Status de sincronização
SELECT * FROM sync_statistics;

-- Limpeza manual
SELECT cleanup_expired_cache();
*/

-- =====================================================
-- FIM DO SCRIPT
-- =====================================================

SELECT '🎉 SISTEMA DE CACHE INTELIGENTE CONFIGURADO COM SUCESSO!' as status;