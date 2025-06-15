# Financeira Autêntica - Sistema de Gestão de Clientes

Uma interface web moderna e responsiva desenvolvida com Python Flask para visualizar e gerenciar informações de clientes da API Omie.

## 🚀 Características

- **Dashboard Interativo**: Visão geral com estatísticas e gráficos
- **Lista de Clientes**: Visualização em tabela e cards com busca e filtros
- **Detalhes do Cliente**: Página completa com todas as informações
- **Busca Avançada**: Busca por nome, razão social ou CNPJ/CPF
- **Exportação de Dados**: Export para CSV
- **Design Responsivo**: Funciona perfeitamente em desktop e mobile
- **Interface Moderna**: Design limpo e profissional com Bootstrap 5

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Pip (gerenciador de pacotes Python)
- Credenciais da API Omie (APP_KEY e APP_SECRET)

## 🔧 Instalação

1. **Clone o repositório ou navegue até o diretório do projeto**

2. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente**:
   
   Edite o arquivo `.env` com suas credenciais da API Omie:
   ```env
   OMIE_APP_KEY=sua_app_key_aqui
   OMIE_APP_SECRET=seu_app_secret_aqui
   BASE_URL=https://app.omie.com.br/api/v1/
   ```

## 🚀 Como Usar

### Executar a Aplicação Web

1. **Navegue até o diretório src**:
   ```bash
   cd src
   ```

2. **Execute a aplicação Flask**:
   ```bash
   python app.py
   ```

3. **Acesse no navegador**:
   ```
   http://localhost:8000
   ```

### Fazer Backup dos Dados

Para criar um backup local dos dados dos clientes:

```bash
cd src
python main.py
```

Isso criará um arquivo `clients_backup.json` com todos os dados dos clientes.

## 📱 Funcionalidades da Interface

### Dashboard
- Estatísticas gerais dos clientes
- Gráficos interativos (Pizza e Barras)
- Ações rápidas para navegação

### Lista de Clientes
- Visualização em tabela ou cards
- Busca em tempo real
- Paginação automática
- Filtros por status e tipo
- Exportação para CSV

### Detalhes do Cliente
- Informações completas do cliente
- Dados de contato e endereço
- Informações bancárias
- Histórico do sistema
- Ações rápidas (email, telefone)

## 🎨 Recursos da Interface

- **Responsiva**: Adapta-se a qualquer tamanho de tela
- **Busca Inteligente**: Busca por múltiplos campos simultaneamente
- **Exportação**: Dados podem ser exportados em formato CSV
- **Navegação Intuitiva**: Interface limpa e fácil de usar
- **Feedback Visual**: Notificações e estados de carregamento
- **Impressão**: Páginas otimizadas para impressão

## 📊 API Endpoints

A aplicação também fornece endpoints de API para integração:

- `GET /api/clients` - Lista todos os clientes
- `GET /api/client/<id>` - Detalhes de um cliente específico
- `GET /api/stats` - Estatísticas dos clientes

### Parâmetros de Query para /api/clients:
- `search`: Termo de busca
- `page`: Número da página
- `per_page`: Registros por página

## 🔒 Segurança

- Credenciais armazenadas em variáveis de ambiente
- Validação de entrada de dados
- Tratamento de erros robusto
- Timeout configurado para requisições

## 🛠️ Estrutura do Projeto

```
financeira_autentica/
├── src/
│   ├── config/
│   │   └── __init__.py          # Configurações da aplicação
│   ├── services/
│   │   ├── __init__.py
│   │   └── omie_service.py      # Serviço para API Omie
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css        # Estilos customizados
│   │   └── js/
│   │       └── main.js          # JavaScript principal
│   ├── templates/
│   │   ├── base.html            # Template base
│   │   ├── index.html           # Dashboard
│   │   ├── clients.html         # Lista de clientes
│   │   ├── client_detail.html   # Detalhes do cliente
│   │   └── error.html           # Página de erro
│   ├── app.py                   # Aplicação Flask principal
│   └── main.py                  # Script de backup
├── .env                         # Variáveis de ambiente
├── requirements.txt             # Dependências Python
└── README.md                    # Este arquivo
```

## 🎯 Tecnologias Utilizadas

- **Backend**: Python 3.8+, Flask
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **UI Framework**: Bootstrap 5
- **Ícones**: Bootstrap Icons
- **Gráficos**: Chart.js
- **API**: Requests para integração com Omie

## 📈 Melhorias Futuras

- [ ] Cache de dados para melhor performance
- [ ] Autenticação de usuários
- [ ] Relatórios avançados
- [ ] Integração com outras APIs
- [ ] Notificações em tempo real
- [ ] Modo escuro

## 🐛 Solução de Problemas

### Erro de Conexão com a API
- Verifique suas credenciais no arquivo `.env`
- Confirme se a URL base está correta
- Verifique sua conexão com a internet

### Erro ao Instalar Dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Porta 8000 já em uso
Altere a porta no arquivo `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=9000)
```

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação da API Omie
2. Consulte os logs da aplicação
3. Verifique as configurações do arquivo `.env`

## 📄 Licença

Este projeto é de uso interno da Financeira Autêntica.

---

**Desenvolvido com ❤️ para uma melhor gestão de clientes**