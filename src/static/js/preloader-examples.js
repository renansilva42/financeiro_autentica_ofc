// Exemplos de uso do Preloader - Financeira Autêntica

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

// Funções utilitárias para demonstração
function showPreloaderDemo(type) {
    switch(type) {
        case 'basic':
            showPreloader('Demonstração do preloader básico...');
            setTimeout(hidePreloader, 3000);
            break;
            
        case 'progress':
            syncDataWithProgress();
            break;
            
        case 'card':
            loadCardData('demo-card');
            break;
            
        case 'table':
            loadTableWithSkeleton('demo-table');
            break;
            
        case 'minimal':
            preloaderManager.showMinimalPreloader();
            setTimeout(() => preloaderManager.hideMinimalPreloader(), 2000);
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