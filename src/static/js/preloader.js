// Preloader JavaScript - Financeira Autêntica

class PreloaderManager {
    constructor() {
        this.preloader = null;
        this.isLoading = false;
        this.loadingTexts = [
            'Carregando dados...',
            'Processando informações...',
            'Sincronizando com a API...',
            'Preparando interface...',
            'Finalizando carregamento...'
        ];
        this.currentTextIndex = 0;
        this.textInterval = null;
        this.init();
    }

    init() {
        // Criar preloader se não existir
        this.createPreloader();
        
        // Mostrar preloader no carregamento inicial da página
        this.showOnPageLoad();
        
        // Configurar interceptadores para requisições AJAX
        this.setupAjaxInterceptors();
        
        // Configurar preloader para formulários
        this.setupFormPreloaders();
        
        // Configurar preloader para navegação
        this.setupNavigationPreloaders();
    }

    createPreloader() {
        if (document.getElementById('main-preloader')) return;

        const preloaderHTML = `
            <div id="main-preloader" class="preloader">
                <div class="preloader-content">
                    <div class="preloader-logo">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    <h2 class="preloader-title">Financeira Autêntica</h2>
                    <div class="preloader-spinner">
                        <div class="spinner-circle"></div>
                        <div class="spinner-circle"></div>
                        <div class="spinner-circle"></div>
                    </div>
                    <div class="preloader-progress">
                        <div class="preloader-progress-bar"></div>
                    </div>
                    <div class="preloader-text">
                        <span class="loading-text">Carregando dados</span><span class="loading-dots"></span>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('afterbegin', preloaderHTML);
        this.preloader = document.getElementById('main-preloader');
    }

    showOnPageLoad() {
        // Mostrar preloader até a página estar completamente carregada
        this.show();
        
        // Aguardar o carregamento completo da página
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.waitForPageLoad();
            });
        } else {
            this.waitForPageLoad();
        }
    }
    
    waitForPageLoad() {
        // Aguardar que todos os recursos sejam carregados
        if (document.readyState === 'complete') {
            setTimeout(() => {
                this.hide();
            }, 800);
        } else {
            window.addEventListener('load', () => {
                setTimeout(() => {
                    this.hide();
                }, 800);
            });
        }
    }

    show(customText = null) {
        if (!this.preloader) this.createPreloader();
        
        this.isLoading = true;
        this.preloader.classList.remove('fade-out');
        this.preloader.style.display = 'flex';
        
        // Atualizar texto se fornecido
        if (customText) {
            const textElement = this.preloader.querySelector('.loading-text');
            if (textElement) textElement.textContent = customText;
        } else {
            this.startTextRotation();
        }
        
        // Bloquear scroll do body
        document.body.style.overflow = 'hidden';
    }

    hide() {
        if (!this.preloader || !this.isLoading) return;
        
        this.isLoading = false;
        this.stopTextRotation();
        
        this.preloader.classList.add('fade-out');
        
        setTimeout(() => {
            if (this.preloader) {
                this.preloader.style.display = 'none';
            }
            // Restaurar scroll do body
            document.body.style.overflow = '';
        }, 500);
    }

    startTextRotation() {
        this.stopTextRotation();
        
        this.textInterval = setInterval(() => {
            const textElement = this.preloader?.querySelector('.loading-text');
            if (textElement) {
                this.currentTextIndex = (this.currentTextIndex + 1) % this.loadingTexts.length;
                textElement.textContent = this.loadingTexts[this.currentTextIndex];
            }
        }, 2000);
    }

    stopTextRotation() {
        if (this.textInterval) {
            clearInterval(this.textInterval);
            this.textInterval = null;
        }
    }

    // Preloader para cards específicos
    showCardPreloader(cardElement) {
        if (!cardElement) return;
        
        cardElement.style.position = 'relative';
        
        const preloaderHTML = `
            <div class="card-preloader">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
            </div>
        `;
        
        cardElement.insertAdjacentHTML('beforeend', preloaderHTML);
    }

    hideCardPreloader(cardElement) {
        if (!cardElement) return;
        
        const preloader = cardElement.querySelector('.card-preloader');
        if (preloader) {
            preloader.remove();
        }
    }

    // Preloader para páginas específicas
    showPagePreloader(containerElement) {
        if (!containerElement) return;
        
        containerElement.style.position = 'relative';
        
        const preloaderHTML = `
            <div class="page-preloader">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
            </div>
        `;
        
        containerElement.insertAdjacentHTML('beforeend', preloaderHTML);
    }

    hidePagePreloader(containerElement) {
        if (!containerElement) return;
        
        const preloader = containerElement.querySelector('.page-preloader');
        if (preloader) {
            preloader.remove();
        }
    }

    // Skeleton loader para tabelas
    showSkeletonLoader(tableElement, rows = 5) {
        if (!tableElement) return;
        
        const tbody = tableElement.querySelector('tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        for (let i = 0; i < rows; i++) {
            const row = document.createElement('tr');
            const cols = tableElement.querySelectorAll('thead th').length || 4;
            
            for (let j = 0; j < cols; j++) {
                const cell = document.createElement('td');
                const skeletonClass = j % 3 === 0 ? 'short' : j % 3 === 1 ? 'medium' : 'long';
                cell.innerHTML = `<div class="skeleton-loader skeleton-row ${skeletonClass}"></div>`;
                row.appendChild(cell);
            }
            
            tbody.appendChild(row);
        }
    }

    // Preloader para botões
    showButtonLoader(buttonElement) {
        if (!buttonElement) return;
        
        buttonElement.classList.add('btn-loading');
        buttonElement.disabled = true;
        
        const textElement = buttonElement.querySelector('.btn-text') || buttonElement;
        if (!buttonElement.querySelector('.btn-text')) {
            const originalText = buttonElement.innerHTML;
            buttonElement.innerHTML = `<span class="btn-text">${originalText}</span>`;
        }
    }

    hideButtonLoader(buttonElement) {
        if (!buttonElement) return;
        
        buttonElement.classList.remove('btn-loading');
        buttonElement.disabled = false;
    }

    // Configurar interceptadores para requisições AJAX
    setupAjaxInterceptors() {
        // Desabilitado temporariamente para evitar conflitos
        // Os interceptadores podem ser habilitados manualmente quando necessário
        
        /*
        // Interceptar fetch
        const originalFetch = window.fetch;
        window.fetch = (...args) => {
            this.show('Carregando dados...');
            
            return originalFetch(...args)
                .then(response => {
                    this.hide();
                    return response;
                })
                .catch(error => {
                    this.hide();
                    throw error;
                });
        };

        // Interceptar XMLHttpRequest
        const originalOpen = XMLHttpRequest.prototype.open;
        const originalSend = XMLHttpRequest.prototype.send;
        
        XMLHttpRequest.prototype.open = function(...args) {
            this._url = args[1];
            return originalOpen.apply(this, args);
        };
        
        XMLHttpRequest.prototype.send = function(...args) {
            if (this._url && !this._url.includes('static/')) {
                preloaderManager.show('Processando requisição...');
                
                this.addEventListener('loadend', () => {
                    preloaderManager.hide();
                });
            }
            
            return originalSend.apply(this, args);
        };
        */
    }

    // Configurar preloader para formulários
    setupFormPreloaders() {
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.tagName === 'FORM' && !form.hasAttribute('data-no-preloader')) {
                const submitButton = form.querySelector('button[type="submit"]');
                if (submitButton) {
                    this.showButtonLoader(submitButton);
                }
                
                this.show('Processando formulário...');
                
                // Se for um formulário que não redireciona, esconder após um tempo
                setTimeout(() => {
                    if (this.isLoading) {
                        this.hide();
                        if (submitButton) {
                            this.hideButtonLoader(submitButton);
                        }
                    }
                }, 5000);
            }
        });
    }

    // Configurar preloader para navegação
    setupNavigationPreloaders() {
        // Preloader para links de navegação
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[href]');
            if (link && 
                !link.hasAttribute('data-no-preloader') && 
                !link.href.includes('#') && 
                !link.href.includes('javascript:') &&
                !link.hasAttribute('download') &&
                link.target !== '_blank') {
                
                this.show('Navegando...');
            }
        });

        // Preloader para botões com data-href
        document.addEventListener('click', (e) => {
            const button = e.target.closest('[data-href]');
            if (button) {
                this.show('Carregando página...');
                setTimeout(() => {
                    window.location.href = button.getAttribute('data-href');
                }, 300);
            }
        });
    }

    // Preloader minimalista (barra no topo)
    showMinimalPreloader() {
        let minimalPreloader = document.getElementById('minimal-preloader');
        if (!minimalPreloader) {
            minimalPreloader = document.createElement('div');
            minimalPreloader.id = 'minimal-preloader';
            minimalPreloader.className = 'minimal-preloader';
            document.body.appendChild(minimalPreloader);
        }
        minimalPreloader.style.display = 'block';
    }

    hideMinimalPreloader() {
        const minimalPreloader = document.getElementById('minimal-preloader');
        if (minimalPreloader) {
            minimalPreloader.style.display = 'none';
        }
    }

    // Método para mostrar preloader com progresso personalizado
    showWithProgress(steps = []) {
        this.show();
        
        if (steps.length === 0) return;
        
        let currentStep = 0;
        const progressBar = this.preloader?.querySelector('.preloader-progress-bar');
        const textElement = this.preloader?.querySelector('.loading-text');
        
        const updateProgress = () => {
            if (currentStep < steps.length && textElement) {
                textElement.textContent = steps[currentStep];
                
                if (progressBar) {
                    const progress = ((currentStep + 1) / steps.length) * 100;
                    progressBar.style.width = `${progress}%`;
                }
                
                currentStep++;
                
                if (currentStep < steps.length) {
                    setTimeout(updateProgress, 1000);
                } else {
                    setTimeout(() => this.hide(), 500);
                }
            }
        };
        
        updateProgress();
    }
}

// Inicializar o gerenciador de preloader
let preloaderManager;

// Inicializar imediatamente se o DOM já estiver carregado
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        preloaderManager = new PreloaderManager();
    });
} else {
    preloaderManager = new PreloaderManager();
}

// Fallback de segurança - esconder preloader após 5 segundos no máximo
setTimeout(() => {
    if (preloaderManager && preloaderManager.isLoading) {
        console.log('Forçando ocultação do preloader por timeout de segurança');
        preloaderManager.hide();
    }
}, 5000);

// Funções globais para facilitar o uso
window.showPreloader = (text) => preloaderManager?.show(text);
window.hidePreloader = () => preloaderManager?.hide();
window.showCardPreloader = (element) => preloaderManager?.showCardPreloader(element);
window.hideCardPreloader = (element) => preloaderManager?.hideCardPreloader(element);
window.showPagePreloader = (element) => preloaderManager?.showPagePreloader(element);
window.hidePagePreloader = (element) => preloaderManager?.hidePagePreloader(element);
window.showSkeletonLoader = (element, rows) => preloaderManager?.showSkeletonLoader(element, rows);
window.showButtonLoader = (element) => preloaderManager?.showButtonLoader(element);
window.hideButtonLoader = (element) => preloaderManager?.hideButtonLoader(element);

// Exportar para uso em módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PreloaderManager;
}