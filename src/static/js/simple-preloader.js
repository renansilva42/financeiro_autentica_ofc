// Preloader Simples - Financeira Autêntica

(function() {
    'use strict';
    
    let preloader = null;
    let isLoading = false;
    let isNavigationPreloader = false;
    let navigationStartTime = 0;
    let progressInterval = null;
    let currentProgress = 0;
    
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
                        <div class="preloader-progress-bar" style="width: 0%;"></div>
                    </div>
                    <div class="preloader-percentage">
                        <span class="percentage-text">0%</span>
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
    
    function updateProgress(progress) {
        if (!preloader) return;
        
        const progressBar = preloader.querySelector('.preloader-progress-bar');
        const percentageText = preloader.querySelector('.percentage-text');
        
        if (progressBar) {
            progressBar.style.width = progress + '%';
        }
        
        if (percentageText) {
            percentageText.textContent = Math.round(progress) + '%';
        }
        
        currentProgress = progress;
    }
    
    function startProgressAnimation(duration = 3000) {
        if (progressInterval) {
            clearInterval(progressInterval);
        }
        
        currentProgress = 0;
        updateProgress(0);
        
        const startTime = Date.now();
        const increment = 100 / (duration / 50); // Atualiza a cada 50ms
        
        progressInterval = setInterval(() => {
            const elapsedTime = Date.now() - startTime;
            const targetProgress = Math.min((elapsedTime / duration) * 100, 100);
            
            // Animação suave do progresso
            if (currentProgress < targetProgress) {
                currentProgress = Math.min(currentProgress + increment, targetProgress);
                updateProgress(currentProgress);
            }
            
            if (currentProgress >= 100 || elapsedTime >= duration) {
                clearInterval(progressInterval);
                progressInterval = null;
                updateProgress(100);
            }
        }, 50);
    }
    
    function stopProgressAnimation() {
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }
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
        
        // Iniciar animação de progresso
        const duration = isNavigation ? 2500 : 3000;
        startProgressAnimation(duration);
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
        
        // Parar animação de progresso
        stopProgressAnimation();
        
        // Garantir que o progresso chegue a 100% antes de ocultar
        updateProgress(100);
        
        isLoading = false;
        isNavigationPreloader = false;
        navigationStartTime = 0;
        
        preloader.classList.add('fade-out');
        
        setTimeout(() => {
            if (preloader) {
                preloader.style.display = 'none';
                // Reset do progresso para próxima vez
                updateProgress(0);
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
        
        // Preloader normal de carregamento inicial
        // Mostrar sempre no carregamento inicial, especialmente para o dashboard
        const isInitialLoad = !sessionStorage.getItem('app_loaded');
        const isDashboard = window.location.pathname === '/' || window.location.pathname === '/index';
        
        if (document.readyState === 'loading' || isInitialLoad || isDashboard) {
            console.log('Mostrando preloader inicial - readyState:', document.readyState, 'isInitialLoad:', isInitialLoad, 'isDashboard:', isDashboard);
            showPreloader(false);
            
            // Marcar que a aplicação foi carregada
            if (isInitialLoad) {
                sessionStorage.setItem('app_loaded', 'true');
            }
            
            // Aguardar carregamento completo
            function checkAndHide() {
                if (document.readyState === 'complete') {
                    // Aguardar um pouco mais para o dashboard carregar as estatísticas
                    const delay = isDashboard ? 1200 : 800;
                    setTimeout(() => {
                        if (!isNavigationPreloader) {
                            hidePreloader();
                        }
                    }, delay);
                } else {
                    window.addEventListener('load', () => {
                        // Aguardar um pouco mais para o dashboard carregar as estatísticas
                        const delay = isDashboard ? 1200 : 800;
                        setTimeout(() => {
                            if (!isNavigationPreloader) {
                                hidePreloader();
                            }
                        }, delay);
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
            }, 6000);
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
    window.updatePreloaderProgress = updateProgress;
    window.startPreloaderProgress = startProgressAnimation;
    window.stopPreloaderProgress = stopProgressAnimation;
    
    // Debug: expor variáveis para inspeção
    window.preloaderDebug = {
        get isLoading() { return isLoading; },
        get isNavigationPreloader() { return isNavigationPreloader; },
        get navigationStartTime() { return navigationStartTime; },
        get currentProgress() { return currentProgress; }
    };
    
})();