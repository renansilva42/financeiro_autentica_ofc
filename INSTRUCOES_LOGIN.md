# 🔐 Sistema de Login - Financeira Autêntica

## ✅ O que foi implementado

### 1. **Autenticação Completa**
- ✅ Sistema de login com email e senha
- ✅ Integração com Supabase para armazenar usuários
- ✅ Proteção de todas as rotas com `@login_required`
- ✅ Sessões seguras com Flask-Session
- ✅ Hash de senhas com SHA-256

### 2. **Interface de Login**
- ✅ Página de login responsiva e moderna
- ✅ Validação de formulário
- ✅ Mensagens de erro e sucesso
- ✅ Redirecionamento após login

### 3. **Navegação Protegida**
- ✅ Botão de logout na barra de navegação
- ✅ Informações do usuário logado
- ✅ Mensagens flash em todas as páginas
- ✅ Redirecionamento automático para login

### 4. **Segurança**
- ✅ Variáveis de ambiente para credenciais
- ✅ Senhas hasheadas (nunca em texto plano)
- ✅ Sessões seguras
- ✅ Validação de email

## 🚀 Como usar

### 1. **Configurar Supabase**
```bash
# 1. Crie uma conta no Supabase (https://supabase.com)
# 2. Crie um novo projeto
# 3. Vá em Settings > API e copie:
#    - Project URL
#    - anon/public key
```

### 2. **Configurar .env**
```env
# Edite o arquivo .env e substitua:
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-publica-aqui
SECRET_KEY=uma-chave-super-secreta-aqui
```

### 3. **Criar tabela de usuários**
```sql
-- Execute no SQL Editor do Supabase:
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Criar usuário admin (senha: admin123)
INSERT INTO users (email, password_hash, name) 
VALUES (
    'admin@financeira.com', 
    'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 
    'Administrador'
);
```

### 4. **Executar aplicação**
```bash
cd /Users/renansilva/VS\ Code\ Workspace/financeira_autentica
python src/app.py
```

### 5. **Fazer login**
```
URL: http://localhost:8002/login
Email: admin@financeira.com
Senha: admin123
```

## 🛠️ Ferramentas incluídas

### **Script para criar usuários**
```bash
cd src/utils
python create_user.py
```

### **Arquivos criados/modificados**
- ✅ `src/services/auth_service.py` - Serviço de autenticação
- ✅ `src/utils/auth_decorators.py` - Decoradores de proteção
- ✅ `src/templates/login.html` - Página de login
- ✅ `src/utils/create_user.py` - Script para criar usuários
- ✅ `src/utils/create_users_table.sql` - SQL para criar tabela
- ✅ `src/app.py` - Atualizado com autenticação
- ✅ `src/templates/base.html` - Atualizado com logout
- ✅ `requirements.txt` - Novas dependências
- ✅ `.env` - Variáveis do Supabase

## 🔒 Fluxo de Autenticação

1. **Usuário tenta acessar qualquer página**
2. **Sistema verifica se está logado**
3. **Se não estiver → redireciona para /login**
4. **Usuário insere email/senha**
5. **Sistema valida no Supabase**
6. **Se válido → cria sessão e redireciona**
7. **Se inválido → mostra erro**

## 📋 Rotas protegidas

Todas essas rotas agora exigem login:
- `/` (Dashboard)
- `/clients` (Clientes)
- `/purchase-orders` (Compras)
- `/sales` (Vendas)
- `/services` (Serviços)
- `/api/*` (Todas as APIs)

## 🎯 Credenciais de teste

**Email:** admin@financeira.com  
**Senha:** admin123

> ⚠️ **IMPORTANTE:** Altere essas credenciais em produção!

## 🆘 Solução de problemas

### **Erro: SUPABASE_URL não configurada**
- Verifique se o arquivo `.env` tem as variáveis corretas
- Certifique-se de que não há espaços extras

### **Erro: Usuário não encontrado**
- Verifique se a tabela `users` foi criada no Supabase
- Confirme se o usuário foi inserido corretamente

### **Erro: Senha incorreta**
- A senha padrão é `admin123`
- Verifique se o hash está correto na tabela

### **Página não carrega**
- Verifique se todas as dependências foram instaladas
- Confirme se o Flask está rodando na porta 8002

## 🎉 Pronto!

Agora seu sistema tem autenticação completa! Todos os dashboards estão protegidos e só podem ser acessados após login.