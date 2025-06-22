# Solução Completa para Timeout de Worker

## Problema Identificado

O erro `WORKER TIMEOUT (pid:11)` ocorria quando a aplicação tentava carregar todas as ordens de serviço e mapeamentos de clientes/vendedores simultaneamente, causando timeout no Gunicorn devido ao tempo excessivo de requisições à API do Omie.

## Soluções Implementadas

### 1. Timeout Configurável nas Requisições

**Arquivo:** `src/services/omie_service.py`

- Adicionado parâmetro `timeout` configurável no método `_make_request()`
- Timeout padrão reduzido para 10 segundos
- Tratamento específico para `requests.exceptions.Timeout`

```python
def _make_request(self, resource: str, body: dict, timeout: int = 10) -> dict:
    # Implementação com timeout configurável
```

### 2. Limitação de Páginas para Evitar Timeout

**Modificações nos métodos:**
- `get_all_clients_summary()` - limitado a 20 páginas por padrão
- `get_all_sellers()` - limitado a 10 páginas por padrão
- `get_client_name_mapping()` - usa limitação de páginas
- `get_seller_name_mapping()` - usa limitação de páginas

### 3. Modo Timeout-Safe para Ordens de Serviço

**Arquivo:** `src/services/omie_service.py`

```python
def get_all_service_orders(self, max_pages: int = None, use_background_loading: bool = True, timeout_safe: bool = True):
    # Se timeout_safe está ativo, limitar a 10 páginas para evitar timeout
    if timeout_safe and total_pages > 10:
        max_pages = 10
        print(f"Modo timeout-safe ativo: limitando a {max_pages} páginas para evitar timeout")
```

### 4. Tratamento de Erros Robusto

**Arquivo:** `src/app.py`

- Tratamento individual para cada operação de carregamento
- Fallbacks para dados vazios em caso de erro
- Logs detalhados para debugging

```python
# Buscar mapeamento de clientes com timeout limitado
try:
    client_name_mapping = omie_service.get_client_name_mapping(max_pages=20)
except Exception as e:
    print(f"Erro ao carregar mapeamento de clientes: {str(e)}")
    client_name_mapping = {}
```

### 5. Sistema de Background Tasks

**Novo arquivo:** `src/services/background_service.py`

- Sistema de tarefas em background usando threads
- Permite carregamento completo de dados sem bloquear a interface
- Endpoints para iniciar e monitorar tarefas

**Endpoints adicionados:**
- `POST /api/background/load-full-data` - Inicia carregamento completo
- `GET /api/background/status/<task_id>` - Verifica status da tarefa
- `POST /api/cache/clear` - Limpa cache

### 6. Configuração do Gunicorn

**Arquivo:** `Procfile`

```
web: gunicorn --chdir src --bind 0.0.0.0:$PORT --timeout 120 --keep-alive 5 --max-requests 1000 --max-requests-jitter 100 app:app
```

**Parâmetros adicionados:**
- `--timeout 120` - Timeout de 2 minutos para workers
- `--keep-alive 5` - Mantém conexões vivas por 5 segundos
- `--max-requests 1000` - Reinicia worker após 1000 requests
- `--max-requests-jitter 100` - Adiciona variação aleatória

### 7. Cache Inteligente

**Melhorias no sistema de cache:**
- Cache com tempo de vida estendido para ordens de serviço (15 minutos)
- Cache separado para diferentes limitações de páginas
- Método para limpeza de cache via API

## Estratégia de Carregamento

### Carregamento Inicial (Timeout-Safe)
1. Carrega até 10 páginas de ordens de serviço
2. Carrega até 20 páginas de clientes
3. Carrega até 10 páginas de vendedores
4. Tempo total estimado: < 60 segundos

### Carregamento Completo (Background)
1. Usuário pode iniciar carregamento completo via API
2. Processo roda em background sem bloquear interface
3. Dados completos ficam disponíveis no cache
4. Interface mostra status do carregamento

## Benefícios da Solução

1. **Eliminação de Timeouts:** Carregamento inicial sempre dentro do limite
2. **Experiência do Usuário:** Interface responsiva mesmo com dados limitados
3. **Dados Completos Opcionais:** Possibilidade de carregar todos os dados quando necessário
4. **Robustez:** Sistema continua funcionando mesmo com falhas parciais
5. **Monitoramento:** Logs detalhados para debugging
6. **Flexibilidade:** Parâmetros configuráveis para diferentes cenários

## Como Usar

### Carregamento Normal
- A aplicação carrega automaticamente dados essenciais
- Funciona imediatamente sem timeout

### Carregamento Completo
```javascript
// Iniciar carregamento completo
fetch('/api/background/load-full-data', { method: 'POST' })
  .then(response => response.json())
  .then(data => console.log('Carregamento iniciado:', data.task_id));

// Verificar status
fetch('/api/background/status/full_data_load')
  .then(response => response.json())
  .then(status => console.log('Status:', status));
```

### Limpar Cache
```javascript
fetch('/api/cache/clear', { method: 'POST' })
  .then(response => response.json())
  .then(data => console.log('Cache limpo'));
```

## Monitoramento

Os logs agora incluem:
- Tempo de carregamento de cada etapa
- Número de registros carregados
- Erros específicos com contexto
- Status do cache

Exemplo de log:
```
Buscando ordens de serviço - página 1, busca: '', mês: ''
Dados de ordens de serviço carregados do cache: 500 registros
Buscando mapeamento de nomes de clientes...
Mapeamento de clientes criado: 1000 clientes
Buscando mapeamento de nomes de vendedores...
Mapeamento de vendedores criado: 50 vendedores
```

## Próximos Passos

1. **Monitoramento em Produção:** Verificar se os timeouts foram eliminados
2. **Otimização de Cache:** Ajustar tempos de vida baseado no uso real
3. **Interface de Carregamento:** Adicionar indicadores visuais para carregamento background
4. **Métricas:** Implementar métricas de performance para monitoramento contínuo

Esta solução garante que a aplicação seja robusta, responsiva e capaz de lidar com grandes volumes de dados sem comprometer a experiência do usuário.