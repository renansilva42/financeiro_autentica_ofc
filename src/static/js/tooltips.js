// Gerenciador de Tooltips para Observações
// Evita duplicação e gerencia tooltips de forma centralizada

class TooltipManager {
    constructor() {
        this.initialized = false;
        this.tooltips = new Map();
    }

    init() {
        if (this.initialized) {
            console.log('Tooltips já foram inicializados');
            return;
        }

        console.log('Inicializando gerenciador de tooltips...');
        
        // Tentar Bootstrap tooltips primeiro
        if (this.initBootstrapTooltips()) {
            console.log('Bootstrap tooltips inicializados com sucesso');
        } else {
            console.log('Bootstrap não disponível, usando tooltips customizados');
            this.initCustomTooltips();
        }

        this.initialized = true;
    }

    initBootstrapTooltips() {
        try {
            const obsTexts = document.querySelectorAll('.obs-text[data-obs]');
            console.log('Elementos encontrados para Bootstrap tooltips:', obsTexts.length);

            obsTexts.forEach((obsText, index) => {
                const fullText = obsText.getAttribute('data-obs');
                if (!fullText || fullText.trim() === '') return;

                // Verificar se já tem tooltip
                if (obsText.hasAttribute('data-bs-original-title')) {
                    console.log(`Elemento ${index} já tem tooltip Bootstrap`);
                    return;
                }

                // Configurar atributos
                obsText.setAttribute('data-bs-toggle', 'tooltip');
                obsText.setAttribute('data-bs-placement', 'top');
                obsText.setAttribute('data-bs-title', fullText);
                obsText.setAttribute('data-bs-html', 'false');
                obsText.style.cursor = 'help';

                // Adicionar indicador visual se truncado
                if (this.isTextTruncated(obsText)) {
                    obsText.classList.add('truncated');
                }
            });

            // Inicializar tooltips Bootstrap
            if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
                const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]:not([data-bs-original-title])');
                const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => 
                    new bootstrap.Tooltip(tooltipTriggerEl, {
                        container: 'body',
                        trigger: 'hover focus',
                        delay: { show: 300, hide: 100 }
                    })
                );
                
                console.log('Bootstrap tooltips criados:', tooltipList.length);
                return tooltipList.length > 0;
            }
            
            return false;
        } catch (error) {
            console.error('Erro ao inicializar Bootstrap tooltips:', error);
            return false;
        }
    }

    initCustomTooltips() {
        console.log('Inicializando tooltips customizados...');
        
        const obsTexts = document.querySelectorAll('.obs-text[data-obs]');
        console.log('Elementos encontrados:', obsTexts.length);

        obsTexts.forEach((obsText, index) => {
            const fullText = obsText.getAttribute('data-obs');
            if (!fullText || fullText.trim() === '') return;

            // Pular se já tem Bootstrap tooltip
            if (obsText.hasAttribute('data-bs-original-title')) return;

            // Pular se já foi processado
            if (obsText.hasAttribute('data-custom-tooltip')) return;

            this.createCustomTooltip(obsText, fullText, index);
        });

        this.addGlobalEvents();
    }

    createCustomTooltip(obsText, fullText, index) {
        // Marcar como processado
        obsText.setAttribute('data-custom-tooltip', 'true');

        // Criar elemento tooltip
        const tooltip = document.createElement('div');
        tooltip.id = `custom-tooltip-${index}`;
        tooltip.className = 'custom-tooltip';
        tooltip.style.cssText = `
            position: fixed;
            background: #333;
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.875rem;
            max-width: 350px;
            min-width: 200px;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            white-space: pre-wrap;
            word-wrap: break-word;
            display: none;
            line-height: 1.4;
            pointer-events: none;
        `;
        document.body.appendChild(tooltip);

        // Configurar elemento
        obsText.style.cursor = 'help';
        if (this.isTextTruncated(obsText)) {
            obsText.classList.add('truncated');
        }

        // Criar funções de evento
        const showTooltip = (e) => {
            tooltip.textContent = fullText;
            tooltip.style.display = 'block';
            this.positionTooltip(obsText, tooltip);
        };

        const hideTooltip = () => {
            tooltip.style.display = 'none';
        };

        const toggleTooltip = (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            // Esconder outros tooltips
            this.hideAllTooltips();
            
            if (tooltip.style.display === 'block') {
                hideTooltip();
            } else {
                showTooltip();
            }
        };

        // Adicionar eventos
        obsText.addEventListener('mouseenter', showTooltip);
        obsText.addEventListener('mouseleave', hideTooltip);
        obsText.addEventListener('click', toggleTooltip);

        // Armazenar referências
        this.tooltips.set(obsText, {
            tooltip,
            showTooltip,
            hideTooltip,
            toggleTooltip
        });

        console.log(`Tooltip customizado criado para elemento ${index}`);
    }

    positionTooltip(element, tooltip) {
        const rect = element.getBoundingClientRect();
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

        // Posição inicial (acima do elemento)
        let top = rect.top + scrollTop - 10;
        let left = rect.left + scrollLeft;

        // Aguardar um frame para dimensões corretas
        requestAnimationFrame(() => {
            const tooltipRect = tooltip.getBoundingClientRect();

            // Ajustar horizontalmente
            if (left + tooltipRect.width > window.innerWidth - 10) {
                left = window.innerWidth + scrollLeft - tooltipRect.width - 10;
            }
            if (left < scrollLeft + 10) {
                left = scrollLeft + 10;
            }

            // Ajustar verticalmente
            if (top - tooltipRect.height < scrollTop + 10) {
                top = rect.bottom + scrollTop + 10;
            }

            tooltip.style.top = top + 'px';
            tooltip.style.left = left + 'px';
        });
    }

    hideAllTooltips() {
        document.querySelectorAll('.custom-tooltip').forEach(tooltip => {
            tooltip.style.display = 'none';
        });
    }

    addGlobalEvents() {
        if (this.globalEventsAdded) return;

        // Fechar tooltips ao clicar fora
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.obs-text')) {
                this.hideAllTooltips();
            }
        });

        // Esconder durante scroll
        window.addEventListener('scroll', () => {
            this.hideAllTooltips();
        });

        this.globalEventsAdded = true;
    }

    isTextTruncated(element) {
        return element.scrollHeight > element.clientHeight || 
               element.scrollWidth > element.clientWidth;
    }

    destroy() {
        // Limpar tooltips customizados
        this.tooltips.forEach((data, element) => {
            element.removeEventListener('mouseenter', data.showTooltip);
            element.removeEventListener('mouseleave', data.hideTooltip);
            element.removeEventListener('click', data.toggleTooltip);
            if (data.tooltip.parentNode) {
                data.tooltip.parentNode.removeChild(data.tooltip);
            }
        });

        this.tooltips.clear();
        this.initialized = false;
    }
}

// Instância global
window.tooltipManager = new TooltipManager();

// Auto-inicializar quando DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => window.tooltipManager.init(), 500);
    });
} else {
    setTimeout(() => window.tooltipManager.init(), 500);
}