# Configuração de Autenticação - Financeira Autêntica

Este documento explica como configurar a autenticação com Supabase para o sistema Financeira Autêntica.

## 📋 Pré-requisitos

1. Conta no [Supabase](https://supabase.com)
2. Projeto criado no Supabase
3. Python 3.7+ instalado

## 🚀 Configuração Passo a Passo

### 1. Configurar o Supabase

1. **Acesse seu projeto no Supabase**
2. **Obtenha as credenciais:**
   - Vá em `Settings` > `API`
   - Copie a `URL` do projeto
   - Copie a `anon/public` key

### 2. Configurar Variáveis de Ambiente

1. **Edite o arquivo `.env`** na raiz do projeto:
```env
# Supabase Configuration
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-publica-aqui

# Flask Configuration (opcional - gere uma chave segura)
SECRET_KEY=sua-chave-secreta-super-segura-aqui
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Criar Tabela de Usuários

1. **No Supabase Dashboard:**
   - Vá em `SQL Editor`
   - Execute o script em `src/utils/create_users_table.sql`

2. **Ou copie e execute este SQL:**
```sql
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
```

### 5. Criar Primeiro Usuário

**Opção 1: Via Script Python**
```bash
cd src/utils
python create_user.py
```

**Opção 2: Inserção Manual no Supabase**
```sql
-- Senha: admin123 (altere em produção!)
INSERT INTO users (email, password_hash, name) 
VALUES (
    'admin@financeira.com', 
    'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 
    'Administrador'
);
```

## 🔐 Como Funciona a Autenticação

### Fluxo de Login
1. Usuário acessa qualquer rota protegida
2. Sistema redireciona para `/login`
3. Usuário insere email e senha
4. Sistema valida credenciais no Supabase
5. Se válido, cria sessão e redireciona para dashboard
6. Se inválido, mostra mensagem de erro

### Proteção de Rotas
Todas as rotas principais estão protegidas com `@login_required`:
- `/` (Dashboard principal)
- `/clients` (Clientes)
- `/purchase-orders` (Pedidos de Compra)
- `/sales` (Vendas)
- `/services` (Serviços)
- Todas as rotas da API (`/api/*`)

### Sessões
- Sessões são armazenadas no servidor (filesystem)
- Dados da sessão: `user_id`, `user_email`, `user_name`
- Logout limpa toda a sessão

## 🛠️ Comandos Úteis

### Gerar Hash de Senha
```bash
cd src/utils
python create_user.py
# Escolha opção 2
```

### Criar Novo Usuário
```bash
cd src/utils
python create_user.py
# Escolha opção 1
```

### Executar Aplicação
```bash
python src/app.py
```

## 🔒 Segurança

### Senhas
- Senhas são hasheadas com SHA-256
- Nunca armazenadas em texto plano
- Hash é comparado durante login

### Sessões
- Chave secreta configurável via `.env`
- Sessões expiram ao fechar navegador
- Dados sensíveis não ficam no cliente

### Variáveis de Ambiente
- Credenciais ficam no `.env`
- Arquivo `.env` está no `.gitignore`
- Nunca commitar credenciais

## 🚨 Importante para Produção

1. **Altere a SECRET_KEY** para uma chave realmente segura
2. **Altere credenciais padrão** (email/senha do admin)
3. **Configure HTTPS** no servidor
4. **Use variáveis de ambiente** do servidor, não arquivo `.env`
5. **Configure backup** da tabela de usuários

## 📞 Suporte

Se encontrar problemas:
1. Verifique se as variáveis do `.env` estão corretas
2. Confirme se a tabela `users` foi criada no Supabase
3. Teste a conexão com o Supabase
4. Verifique os logs da aplicação

## 🎯 Credenciais de Teste

**Email:** admin@financeira.com  
**Senha:** admin123

> ⚠️ **IMPORTANTE:** Altere essas credenciais em produção!