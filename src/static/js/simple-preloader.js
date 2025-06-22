// Preloader Simples - Financeira Autêntica

(function() {
    'use strict';
    
    let preloader = null;
    let isLoading = false;
    let isNavigationPreloader = false;
    let navigationStartTime = 0;
    
    function createPreloader() {
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
        preloader = document.getElementById('main-preloader');
    }
    
    function showPreloader(isNavigation = false) {
        console.log('showPreloader chamado, isNavigation:', isNavigation);
        
        if (!preloader) createPreloader();
        
        isLoading = true;
        isNavigationPreloader = isNavigation;
        
        if (isNavigation) {
            navigationStartTime = Date.now();
            console.log('Preloader de navegação iniciado');
        }
        
        preloader.classList.remove('fade-out');
        preloader.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
    
    function hidePreloader(force = false) {
        console.log('hidePreloader chamado, force:', force, 'isLoading:', isLoading, 'isNavigationPreloader:', isNavigationPreloader);
        
        if (!preloader || !isLoading) return;
        
        // Se é um preloader de navegação, garantir tempo mínimo de exibição
        if (isNavigationPreloader && !force) {
            const elapsedTime = Date.now() - navigationStartTime;
            const minDisplayTime = 1500; // 1.5 segundos mínimo para navegação
            
            if (elapsedTime < minDisplayTime) {
                console.log(`Preloader de navegação: aguardando mais ${minDisplayTime - elapsedTime}ms`);
                setTimeout(() => hidePreloader(true), minDisplayTime - elapsedTime);
                return;
            }
        }
        
        console.log('Ocultando preloader');
        isLoading = false;
        isNavigationPreloader = false;
        navigationStartTime = 0;
        
        preloader.classList.add('fade-out');
        
        setTimeout(() => {
            if (preloader) {
                preloader.style.display = 'none';
            }
            document.body.style.overflow = '';
        }, 500);
    }
    
    function initPreloader() {
        console.log('initPreloader chamado, readyState:', document.readyState);
        
        // Verificar se há um preloader de navegação pendente
        const hasNavigationPreloader = sessionStorage.getItem('navigationPreloader');
        if (hasNavigationPreloader) {
            console.log('Detectado preloader de navegação pendente');
            sessionStorage.removeItem('navigationPreloader');
            showPreloader(true);
            
            // Aguardar carregamento completo para preloader de navegação
            function waitForPageLoad() {
                console.log('Aguardando carregamento completo da página, readyState:', document.readyState);
                
                if (document.readyState === 'complete') {
                    console.log('Página já carregada, ocultando preloader de navegação');
                    setTimeout(() => hidePreloader(), 300);
                } else {
                    // Aguardar tanto DOMContentLoaded quanto load
                    let domReady = false;
                    let pageLoaded = false;
                    
                    function checkComplete() {
                        if (domReady && pageLoaded) {
                            console.log('DOM e recursos carregados, ocultando preloader de navegação');
                            setTimeout(() => hidePreloader(), 300);
                        }
                    }
                    
                    if (document.readyState === 'loading') {
                        document.addEventListener('DOMContentLoaded', () => {
                            console.log('DOMContentLoaded disparado');
                            domReady = true;
                            checkComplete();
                        });
                    } else {
                        domReady = true;
                    }
                    
                    window.addEventListener('load', () => {
                        console.log('Load event disparado');
                        pageLoaded = true;
                        checkComplete();
                    });
                    
                    // Fallback de segurança para navegação
                    setTimeout(() => {
                        if (isNavigationPreloader) {
                            console.log('Timeout de segurança: forçando ocultação do preloader de navegação');
                            hidePreloader(true);
                        }
                    }, 8000);
                }
            }
            
            waitForPageLoad();
            return;
        }
        
        // Preloader normal de carregamento inicial (apenas para primeira visita)
        if (document.readyState === 'loading') {
            console.log('Página ainda carregando, mostrando preloader inicial');
            showPreloader(false);
            
            // Aguardar carregamento completo
            function checkAndHide() {
                if (document.readyState === 'complete') {
                    setTimeout(() => {
                        if (!isNavigationPreloader) {
                            hidePreloader();
                        }
                    }, 800);
                } else {
                    window.addEventListener('load', () => {
                        setTimeout(() => {
                            if (!isNavigationPreloader) {
                                hidePreloader();
                            }
                        }, 800);
                    });
                }
            }
            
            document.addEventListener('DOMContentLoaded', checkAndHide);
            
            // Fallback de segurança para carregamento inicial
            setTimeout(() => {
                if (isLoading && !isNavigationPreloader) {
                    console.log('Timeout de segurança: forçando ocultação do preloader inicial');
                    hidePreloader(true);
                }
            }, 5000);
        } else {
            console.log('Página já carregada, não mostrando preloader inicial');
        }
    }
    
    // Inicializar quando o script carregar
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPreloader);
    } else {
        initPreloader();
    }
    
    // Expor funções globais
    window.showPreloader = function(isNavigation = false) {
        showPreloader(isNavigation);
    };
    window.hidePreloader = hidePreloader;
    
    // Debug: expor variáveis para inspeção
    window.preloaderDebug = {
        get isLoading() { return isLoading; },
        get isNavigationPreloader() { return isNavigationPreloader; },
        get navigationStartTime() { return navigationStartTime; }
    };
    
})();