# 🚀 Guia de Deploy - Financeira Autêntica

Este guia explica como fazer deploy da aplicação em diferentes plataformas.

## 📋 Pré-requisitos

### **Variáveis de Ambiente Obrigatórias:**
```env
# Flask
SECRET_KEY=sua-chave-secreta-aqui
FLASK_ENV=production

# Omie API
OMIE_APP_KEY=sua-chave-omie
OMIE_APP_SECRET=seu-secret-omie
BASE_URL=https://app.omie.com.br/api/v1/

# Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-publica-supabase
```

### **Banco de Dados:**
- Execute o script SQL no Supabase antes do deploy
- Use `SUPABASE_SETUP.sql` ou `SUPABASE_SIMPLES.sql`

---

## 🌐 Deploy no Heroku

### **1. Via Heroku CLI:**
```bash
# Instalar Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Criar app
heroku create seu-app-name

# Configurar variáveis
heroku config:set SECRET_KEY="sua-chave-secreta"
heroku config:set OMIE_APP_KEY="sua-chave-omie"
heroku config:set OMIE_APP_SECRET="seu-secret-omie"
heroku config:set SUPABASE_URL="https://seu-projeto.supabase.co"
heroku config:set SUPABASE_KEY="sua-chave-supabase"
heroku config:set FLASK_ENV="production"

# Deploy
git push heroku main
```

### **2. Via Deploy Button:**
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

### **Arquivos necessários:**
- ✅ `Procfile`
- ✅ `requirements.txt`
- ✅ `runtime.txt`
- ✅ `app.json`

---

## ⚡ Deploy no Vercel

### **1. Via Vercel CLI:**
```bash
# Instalar Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# Configurar variáveis no dashboard
# https://vercel.com/dashboard
```

### **2. Via GitHub:**
1. Conecte seu repositório no [Vercel Dashboard](https://vercel.com)
2. Configure as variáveis de ambiente
3. Deploy automático a cada push

### **Arquivos necessários:**
- ✅ `vercel.json`
- ✅ `requirements.txt`

---

## 🚂 Deploy no Railway

### **1. Via Railway CLI:**
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Inicializar projeto
railway init

# Deploy
railway up
```

### **2. Via GitHub:**
1. Conecte no [Railway Dashboard](https://railway.app)
2. Importe seu repositório
3. Configure variáveis de ambiente

### **Arquivos necessários:**
- ✅ `railway.json`
- ✅ `requirements.txt`

---

## 🎨 Deploy no Render

### **1. Via Dashboard:**
1. Acesse [Render Dashboard](https://render.com)
2. Conecte seu repositório
3. Configure como Web Service
4. Defina variáveis de ambiente

### **2. Via Blueprint:**
```bash
# Usar render.yaml para configuração automática
```

### **Arquivos necessários:**
- ✅ `render.yaml`
- ✅ `requirements.txt`

---

## 🐳 Deploy com Docker

### **1. Build Local:**
```bash
# Build da imagem
docker build -t financeira-autentica .

# Executar container
docker run -p 8000:8000 --env-file .env financeira-autentica
```

### **2. Docker Compose:**
```bash
# Executar com compose
docker-compose up -d

# Com Nginx (produção)
docker-compose --profile production up -d
```

### **3. Deploy em Cloud:**
```bash
# Google Cloud Run
gcloud run deploy --source .

# AWS ECS, Azure Container Instances, etc.
```

### **Arquivos necessários:**
- ✅ `Dockerfile`
- ✅ `docker-compose.yml`
- ✅ `nginx.conf` (opcional)

---

## ☁️ Deploy em VPS/Servidor

### **1. Configuração do Servidor:**
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python e dependências
sudo apt install python3 python3-pip python3-venv nginx -y

# Clonar repositório
git clone https://github.com/seu-usuario/financeira-autentica.git
cd financeira-autentica

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### **2. Configurar Systemd:**
```bash
# Criar arquivo de serviço
sudo nano /etc/systemd/system/financeira.service
```

```ini
[Unit]
Description=Financeira Autêntica
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/financeira_autentica
Environment="PATH=/path/to/financeira_autentica/venv/bin"
EnvironmentFile=/path/to/financeira_autentica/.env
ExecStart=/path/to/financeira_autentica/venv/bin/gunicorn --chdir src --bind 127.0.0.1:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Ativar serviço
sudo systemctl enable financeira
sudo systemctl start financeira
```

### **3. Configurar Nginx:**
```bash
sudo nano /etc/nginx/sites-available/financeira
```

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/financeira /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 Configurações de Segurança

### **Variáveis de Ambiente:**
- ✅ Nunca commite o arquivo `.env`
- ✅ Use chaves secretas diferentes para cada ambiente
- ✅ Configure `SECRET_KEY` única e segura
- ✅ Use HTTPS em produção

### **Supabase:**
- ✅ Configure Row Level Security (RLS)
- ✅ Use apenas chaves `anon/public` no frontend
- ✅ Monitore logs de acesso

### **Omie:**
- ✅ Proteja as chaves da API
- ✅ Configure rate limiting se necessário

---

## 📊 Monitoramento

### **Logs:**
```bash
# Heroku
heroku logs --tail

# Docker
docker-compose logs -f

# Systemd
sudo journalctl -u financeira -f
```

### **Health Checks:**
- ✅ Endpoint: `GET /`
- ✅ Status esperado: `200 OK`
- ✅ Timeout: 30 segundos

---

## 🛠️ Troubleshooting

### **Problemas Comuns:**

1. **Erro de Supabase:**
   - Verifique URL e chave
   - Execute `python diagnostico_supabase.py`

2. **Erro de Omie:**
   - Verifique credenciais da API
   - Teste conectividade

3. **Erro de Sessões:**
   - Verifique `SECRET_KEY`
   - Limpe diretório `flask_session`

4. **Erro de Porta:**
   - Configure variável `PORT`
   - Verifique bind do gunicorn

### **Scripts de Diagnóstico:**
```bash
# Verificar configuração
python diagnostico_supabase.py

# Verificar usuários
python verificar_usuarios.py

# Gerar nova SECRET_KEY
python generate_secret_key.py
```

---

## 🎯 Checklist de Deploy

### **Antes do Deploy:**
- [ ] Configurar Supabase e criar tabela `users`
- [ ] Obter credenciais da API Omie
- [ ] Gerar `SECRET_KEY` segura
- [ ] Testar aplicação localmente
- [ ] Configurar variáveis de ambiente

### **Após o Deploy:**
- [ ] Verificar health check
- [ ] Testar login
- [ ] Verificar logs
- [ ] Configurar domínio (se aplicável)
- [ ] Configurar SSL/HTTPS
- [ ] Configurar backups

---

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs da aplicação
2. Execute scripts de diagnóstico
3. Consulte documentação da plataforma
4. Verifique configurações de rede/firewall

**Aplicação pronta para deploy! 🚀**