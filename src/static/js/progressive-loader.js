    /**
 * Sistema de Carregamento Progressivo - Financeira Autêntica
 * Integra com o sistema de preloader existente para carregamento otimizado
 */

class ProgressiveLoader {
    constructor() {
        this.isLoading = false;
        this.currentStage = 0;
        this.stages = [
            { id: 'cache', name: 'Verificando Cache', progress: 0 },
            { id: 'mappings', name: 'Carregando Mapeamentos', progress: 0 },
            { id: 'services', name: 'Carregando Serviços', progress: 0 },
            { id: 'stats', name: 'Calculando Estatísticas', progress: 0 },
            { id: 'dashboard', name: 'Preparando Dashboard', progress: 0 }
        ];
        this.callbacks = {
            onProgress: null,
            onStageChange: null,
            onComplete: null,
            onError: null
        };
    }

    /**
     * Inicia carregamento progressivo do dashboard
     */
    async loadDashboard(options = {}) {
        if (this.isLoading) {
            console.log('Carregamento já em andamento');
            return;
        }

        this.isLoading = true;
        this.currentStage = 0;
        
        // Configurar callbacks
        Object.assign(this.callbacks, options);

        try {
            // Mostrar preloader se disponível
            if (window.showPreloader) {
                window.showPreloader();
            }

            // Iniciar carregamento
            const response = await fetch('/api/progressive/dashboard', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'success') {
                this._updateProgress(100, 'Carregamento concluído!');
                
                if (this.callbacks.onComplete) {
                    this.callbacks.onComplete(result.data);
                }

                return result.data;
            } else {
                throw new Error(result.error || 'Erro desconhecido');
            }

        } catch (error) {
            console.error('Erro no carregamento progressivo:', error);
            
            if (this.callbacks.onError) {
                this.callbacks.onError(error);
            }

            throw error;
        } finally {
            this.isLoading = false;
            
            // Esconder preloader
            if (window.hidePreloader) {
                setTimeout(() => window.hidePreloader(), 500);
            }
        }
    }

    /**
     * Carrega dados com simulação de progresso
     */
    async loadWithProgress() {
        if (this.isLoading) return;

        this.isLoading = true;
        
        try {
            // Simular progresso por estágios
            for (let i = 0; i < this.stages.length; i++) {
                this.currentStage = i;
                const stage = this.stages[i];
                
                this._updateStage(i, stage.name);
                
                // Simular tempo de carregamento
                await this._simulateStageProgress(i);
            }

            // Carregar dados reais
            const data = await this.loadDashboard();
            return data;

        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Simula progresso de um estágio
     */
    async _simulateStageProgress(stageIndex) {
        const stage = this.stages[stageIndex];
        const baseProgress = (stageIndex / this.stages.length) * 100;
        const stageProgress = 100 / this.stages.length;

        for (let progress = 0; progress <= 100; progress += 10) {
            stage.progress = progress;
            const totalProgress = baseProgress + (progress * stageProgress / 100);
            
            this._updateProgress(totalProgress, stage.name);
            
            // Pequena pausa para visualização
            await new Promise(resolve => setTimeout(resolve, 50));
        }
    }

    /**
     * Atualiza progresso geral
     */
    _updateProgress(percentage, message) {
        // Atualizar preloader se disponível
        if (window.updatePreloaderProgress) {
            window.updatePreloaderProgress(Math.round(percentage));
        }

        // Callback personalizado
        if (this.callbacks.onProgress) {
            this.callbacks.onProgress(percentage, message);
        }

        console.log(`[${Math.round(percentage)}%] ${message}`);
    }

    /**
     * Atualiza estágio atual
     */
    _updateStage(stageIndex, stageName) {
        this.currentStage = stageIndex;
        
        if (this.callbacks.onStageChange) {
            this.callbacks.onStageChange(stageIndex, stageName, this.stages);
        }
    }

    /**
     * Verifica status do carregamento
     */
    async getStatus() {
        try {
            const response = await fetch('/api/progressive/status');
            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Erro ao verificar status:', error);
            return { status: 'error', error: error.message };
        }
    }

    /**
     * Carrega dados específicos com cache inteligente
     */
    async loadCachedData(dataType, endpoint) {
        try {
            const response = await fetch(endpoint, {
                headers: {
                    'Cache-Control': 'max-age=300' // 5 minutos
                }
            });

            if (!response.ok) {
                throw new Error(`Erro ao carregar ${dataType}: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.status === 'success') {
                console.log(`${dataType} carregado:`, {
                    from_cache: result.from_cache,
                    count: result.count || 'N/A'
                });
                
                return result.data || result.mapping;
            }

            throw new Error(result.error || `Erro ao carregar ${dataType}`);

        } catch (error) {
            console.error(`Erro ao carregar ${dataType}:`, error);
            throw error;
        }
    }

    /**
     * Limpa cache inteligente
     */
    async clearIntelligentCache(options = {}) {
        try {
            const response = await fetch('/api/cache/intelligent/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(options)
            });

            const result = await response.json();
            
            if (result.status === 'success') {
                console.log('Cache inteligente limpo:', result.message);
                return true;
            }

            throw new Error(result.error || 'Erro ao limpar cache');

        } catch (error) {
            console.error('Erro ao limpar cache inteligente:', error);
            throw error;
        }
    }

    /**
     * Obtém estatísticas do cache inteligente
     */
    async getCacheStats() {
        try {
            const response = await fetch('/api/cache/intelligent/stats');
            const result = await response.json();
            
            if (result.status === 'success') {
                return result;
            }

            throw new Error(result.error || 'Erro ao obter estatísticas');

        } catch (error) {
            console.error('Erro ao obter estatísticas do cache:', error);
            return null;
        }
    }
}

/**
 * Gerenciador de Interface para Carregamento Progressivo
 */
class ProgressiveUI {
    constructor(progressiveLoader) {
        this.loader = progressiveLoader;
        this.stageIndicators = null;
        this.progressInfo = null;
    }

    /**
     * Cria indicadores visuais de progresso
     */
    createStageIndicators(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const indicatorsHTML = `
            <div class="progressive-stages">
                ${this.loader.stages.map((stage, index) => `
                    <div class="stage-indicator" data-stage="${index}">
                        <div class="stage-icon">
                            <i class="fas fa-circle"></i>
                        </div>
                        <div class="stage-name">${stage.name}</div>
                        <div class="stage-progress">
                            <div class="progress-bar" style="width: 0%"></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        container.innerHTML = indicatorsHTML;
        this.stageIndicators = container.querySelectorAll('.stage-indicator');
    }

    /**
     * Atualiza indicadores visuais
     */
    updateStageIndicators(currentStage, stages) {
        if (!this.stageIndicators) return;

        this.stageIndicators.forEach((indicator, index) => {
            const progressBar = indicator.querySelector('.progress-bar');
            const icon = indicator.querySelector('.stage-icon i');

            if (index < currentStage) {
                // Estágio concluído
                indicator.classList.add('completed');
                icon.className = 'fas fa-check-circle';
                progressBar.style.width = '100%';
            } else if (index === currentStage) {
                // Estágio atual
                indicator.classList.add('active');
                icon.className = 'fas fa-spinner fa-spin';
                progressBar.style.width = `${stages[index].progress}%`;
            } else {
                // Estágio pendente
                indicator.classList.remove('completed', 'active');
                icon.className = 'fas fa-circle';
                progressBar.style.width = '0%';
            }
        });
    }

    /**
     * Mostra informações de progresso
     */
    showProgressInfo(containerId, info) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = `
            <div class="progress-info">
                <div class="progress-stats">
                    <div class="stat">
                        <span class="label">Total de Registros:</span>
                        <span class="value">${info.total_records || 0}</span>
                    </div>
                    <div class="stat">
                        <span class="label">Tempo de Carregamento:</span>
                        <span class="value">${(info.loading_time || 0).toFixed(2)}s</span>
                    </div>
                    <div class="stat">
                        <span class="label">Cache Utilizado:</span>
                        <span class="value">${info.from_cache ? 'Sim' : 'Não'}</span>
                    </div>
                </div>
            </div>
        `;
    }
}

// Instância global
let progressiveLoader;
let progressiveUI;

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    progressiveLoader = new ProgressiveLoader();
    progressiveUI = new ProgressiveUI(progressiveLoader);
    
    console.log('✅ Sistema de carregamento progressivo inicializado');
});

// Funções globais para facilitar uso
window.loadDashboardProgressively = function(options = {}) {
    if (!progressiveLoader) {
        console.error('Sistema de carregamento progressivo não inicializado');
        return Promise.reject(new Error('Sistema não inicializado'));
    }
    
    return progressiveLoader.loadDashboard(options);
};

window.getProgressiveStatus = function() {
    return progressiveLoader ? progressiveLoader.getStatus() : null;
};

window.clearIntelligentCache = function(options = {}) {
    return progressiveLoader ? progressiveLoader.clearIntelligentCache(options) : null;
};

window.getCacheStats = function() {
    return progressiveLoader ? progressiveLoader.getCacheStats() : null;
};

// Exportar para uso em módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ProgressiveLoader, ProgressiveUI };
}