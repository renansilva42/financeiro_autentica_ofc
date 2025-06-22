// Exemplos de uso do Preloader - Financeira Autêntica

// Função utilitária para mostrar alertas
function showAlert(message, type = 'info') {
    // Criar elemento de alerta
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 10000; min-width: 300px;';
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Remover automaticamente após 5 segundos
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Exemplo 1: Preloader para carregamento de dados de clientes
function loadClientsData() {
    showPreloader('Carregando dados dos clientes...');
    
    // Simular requisição AJAX
    fetch('/api/clients')
        .then(response => response.json())
        .then(data => {
            // Processar dados
            console.log('Dados carregados:', data);
            hidePreloader();
        })
        .catch(error => {
            console.error('Erro:', error);
            hidePreloader();
        });
}

// Exemplo 2: Preloader com progresso personalizado
function syncDataWithProgress() {
    const steps = [
        'Conectando com a API Omie...',
        'Buscando dados de clientes...',
        'Processando informações...',
        'Atualizando banco de dados...',
        'Finalizando sincronização...'
    ];
    
    preloaderManager.showWithProgress(steps);
}

// Exemplo 3: Preloader para card específico
function loadCardData(cardId) {
    const cardElement = document.getElementById(cardId);
    if (cardElement) {
        showCardPreloader(cardElement);
        
        // Simular carregamento
        setTimeout(() => {
            hideCardPreloader(cardElement);
            // Atualizar conteúdo do card
            cardElement.querySelector('.card-body').innerHTML = '<p>Dados carregados com sucesso!</p>';
        }, 2000);
    }
}

// Exemplo 4: Skeleton loader para tabela
function loadTableWithSkeleton(tableId) {
    const tableElement = document.getElementById(tableId);
    if (tableElement) {
        showSkeletonLoader(tableElement, 8);
        
        // Simular carregamento de dados
        setTimeout(() => {
            // Restaurar dados reais da tabela
            const tbody = tableElement.querySelector('tbody');
            tbody.innerHTML = `
                <tr>
                    <td>Cliente 1</td>
                    <td>cliente1@email.com</td>
                    <td>Ativo</td>
                    <td>São Paulo</td>
                </tr>
                <tr>
                    <td>Cliente 2</td>
                    <td>cliente2@email.com</td>
                    <td>Ativo</td>
                    <td>Rio de Janeiro</td>
                </tr>
            `;
        }, 3000);
    }
}

// Exemplo 5: Preloader para formulário
function setupFormPreloader() {
    const form = document.getElementById('client-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitButton = form.querySelector('button[type="submit"]');
            showButtonLoader(submitButton);
            
            // Simular processamento
            setTimeout(() => {
                hideButtonLoader(submitButton);
                showAlert('Formulário enviado com sucesso!', 'success');
            }, 3000);
        });
    }
}

// Exemplo 6: Preloader minimalista para navegação rápida
function quickNavigation(url) {
    preloaderManager.showMinimalPreloader();
    
    setTimeout(() => {
        window.location.href = url;
    }, 500);
}

// Exemplo 7: Preloader para dashboard com múltiplas etapas
function loadDashboard() {
    const steps = [
        'Carregando estatísticas gerais...',
        'Buscando dados de vendas...',
        'Processando gráficos...',
        'Carregando relatórios...',
        'Preparando dashboard...'
    ];
    
    showPreloader();
    
    let currentStep = 0;
    const interval = setInterval(() => {
        if (currentStep < steps.length) {
            const textElement = document.querySelector('.loading-text');
            if (textElement) {
                textElement.textContent = steps[currentStep];
            }
            currentStep++;
        } else {
            clearInterval(interval);
            hidePreloader();
        }
    }, 1000);
}

// Exemplo 8: Preloader para exportação de dados
function exportDataWithPreloader(format = 'excel') {
    const steps = [
        'Preparando dados para exportação...',
        'Formatando arquivo...',
        'Gerando download...'
    ];
    
    preloaderManager.showWithProgress(steps);
    
    // Simular processo de exportação
    setTimeout(() => {
        // Aqui seria feito o download real
        console.log(`Dados exportados em formato ${format}`);
    }, 3000);
}

// Exemplo 9: Preloader para busca em tempo real
function setupLiveSearch() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            
            searchTimeout = setTimeout(() => {
                const query = this.value.trim();
                if (query.length > 2) {
                    showPreloader('Buscando resultados...');
                    
                    // Simular busca
                    setTimeout(() => {
                        hidePreloader();
                        console.log('Resultados para:', query);
                    }, 1500);
                }
            }, 500);
        });
    }
}

// Exemplo 10: Preloader para upload de arquivo
function setupFileUpload() {
    const fileInput = document.getElementById('file-upload');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                showPreloader('Fazendo upload do arquivo...');
                
                // Simular upload
                setTimeout(() => {
                    hidePreloader();
                    showAlert('Arquivo enviado com sucesso!', 'success');
                }, 3000);
            }
        });
    }
}

// Inicializar exemplos quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    // Configurar exemplos se os elementos existirem
    setupFormPreloader();
    setupLiveSearch();
    setupFileUpload();
    
    // Adicionar event listeners para botões de exemplo
    const loadDataBtn = document.getElementById('load-data-btn');
    if (loadDataBtn) {
        loadDataBtn.addEventListener('click', loadClientsData);
    }
    
    const syncBtn = document.getElementById('sync-btn');
    if (syncBtn) {
        syncBtn.addEventListener('click', syncDataWithProgress);
    }
    
    const loadCardBtn = document.getElementById('load-card-btn');
    if (loadCardBtn) {
        loadCardBtn.addEventListener('click', () => loadCardData('stats-card'));
    }
    
    const loadTableBtn = document.getElementById('load-table-btn');
    if (loadTableBtn) {
        loadTableBtn.addEventListener('click', () => loadTableWithSkeleton('clients-table'));
    }
    
    const exportBtn = document.getElementById('export-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', () => exportDataWithPreloader('excel'));
    }
});

// Demonstração de progresso manual
function demonstrateManualProgress() {
    showPreloader();
    
    // Parar a animação automática para controle manual
    if (typeof stopPreloaderProgress === 'function') {
        stopPreloaderProgress();
    }
    
    let progress = 0;
    const steps = [
        { progress: 15, message: 'Iniciando processo...', delay: 600 },
        { progress: 35, message: 'Carregando dados...', delay: 800 },
        { progress: 55, message: 'Processando informações...', delay: 700 },
        { progress: 75, message: 'Validando dados...', delay: 600 },
        { progress: 90, message: 'Finalizando...', delay: 500 },
        { progress: 100, message: 'Concluído!', delay: 800 }
    ];
    
    function executeStep(index) {
        if (index >= steps.length) {
            setTimeout(hidePreloader, 1000);
            return;
        }
        
        const step = steps[index];
        
        if (typeof updatePreloaderProgress === 'function') {
            updatePreloaderProgress(step.progress);
        }
        
        // Atualizar texto de carregamento se possível
        const loadingText = document.querySelector('.loading-text');
        if (loadingText) {
            loadingText.textContent = step.message;
        }
        
        setTimeout(() => executeStep(index + 1), step.delay);
    }
    
    // Iniciar com 0%
    if (typeof updatePreloaderProgress === 'function') {
        updatePreloaderProgress(0);
    }
    
    setTimeout(() => executeStep(0), 300);
}

// Funções utilitárias para demonstração
function showPreloaderDemo(type) {
    switch(type) {
        case 'basic':
            showPreloader('Demonstração do preloader básico...');
            setTimeout(hidePreloader, 3000);
            break;
            
        case 'progress':
            showPreloader();
            showAlert('Preloader com contador automático de 0% a 100%', 'info');
            setTimeout(hidePreloader, 4000);
            break;
            
        case 'manual':
            demonstrateManualProgress();
            break;
            
        case 'card':
            loadCardData('demo-card');
            break;
            
        case 'table':
            loadTableWithSkeleton('demo-table');
            break;
            
        case 'minimal':
            if (typeof preloaderManager !== 'undefined') {
                preloaderManager.showMinimalPreloader();
                setTimeout(() => preloaderManager.hideMinimalPreloader(), 2000);
            } else {
                showPreloader();
                setTimeout(hidePreloader, 2000);
            }
            break;
            
        default:
            showPreloader();
            setTimeout(hidePreloader, 2000);
    }
}

// Exportar funções para uso global
window.showPreloaderDemo = showPreloaderDemo;
window.loadClientsData = loadClientsData;
window.syncDataWithProgress = syncDataWithProgress;
window.loadCardData = loadCardData;
window.loadTableWithSkeleton = loadTableWithSkeleton;