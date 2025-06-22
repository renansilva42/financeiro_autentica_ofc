# Preloader com Contador de Progresso - Financeira Autêntica

## Funcionalidades Implementadas

O preloader agora inclui um contador de progresso visual que vai de 0% a 100%, proporcionando uma melhor experiência do usuário durante o carregamento.

### Características do Contador

- **Contador Visual**: Exibe a porcentagem de 0% a 100%
- **Barra de Progresso**: Barra visual que se preenche conforme o progresso
- **Animação Suave**: Transições fluidas entre os valores
- **Responsivo**: Adapta-se a diferentes tamanhos de tela
- **Automático**: Funciona automaticamente com o preloader existente

## Como Funciona

### Automático
O contador de progresso funciona automaticamente quando o preloader é exibido:

```javascript
// Mostra o preloader com contador automático
showPreloader(); // Para carregamento normal (3 segundos)
showPreloader(true); // Para navegação (2.5 segundos)
```

### Controle Manual
Você também pode controlar o progresso manualmente:

```javascript
// Atualizar progresso manualmente
updatePreloaderProgress(50); // Define progresso para 50%

// Iniciar animação de progresso personalizada
startPreloaderProgress(5000); // Animação de 5 segundos

// Parar animação de progresso
stopPreloaderProgress();
```

## Funções Disponíveis

### Funções Principais
- `showPreloader(isNavigation)` - Mostra o preloader com contador
- `hidePreloader()` - Oculta o preloader
- `updatePreloaderProgress(percentage)` - Atualiza o progresso (0-100)
- `startPreloaderProgress(duration)` - Inicia animação automática
- `stopPreloaderProgress()` - Para a animação

### Debug
```javascript
// Verificar estado atual
console.log(preloaderDebug.currentProgress); // Progresso atual
console.log(preloaderDebug.isLoading); // Se está carregando
```

## Exemplos de Uso

### Exemplo 1: Carregamento de Dados
```javascript
function loadData() {
    showPreloader();
    
    // Simular carregamento com progresso manual
    let progress = 0;
    const interval = setInterval(() => {
        progress += 10;
        updatePreloaderProgress(progress);
        
        if (progress >= 100) {
            clearInterval(interval);
            setTimeout(() => hidePreloader(), 500);
        }
    }, 200);
}
```

### Exemplo 2: Upload de Arquivo
```javascript
function uploadFile(file) {
    showPreloader();
    
    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            updatePreloaderProgress(percentComplete);
        }
    });
    
    xhr.addEventListener('load', () => {
        updatePreloaderProgress(100);
        setTimeout(() => hidePreloader(), 500);
    });
    
    // Enviar arquivo...
}
```

### Exemplo 3: Múltiplas Etapas
```javascript
async function processMultipleSteps() {
    showPreloader();
    
    try {
        updatePreloaderProgress(20);
        await step1();
        
        updatePreloaderProgress(40);
        await step2();
        
        updatePreloaderProgress(60);
        await step3();
        
        updatePreloaderProgress(80);
        await step4();
        
        updatePreloaderProgress(100);
        setTimeout(() => hidePreloader(), 500);
    } catch (error) {
        hidePreloader();
        console.error('Erro:', error);
    }
}
```

## Personalização CSS

### Cores do Contador
```css
.percentage-text {
    color: #fff; /* Cor do texto */
    font-size: 1.2rem; /* Tamanho da fonte */
    font-weight: 600; /* Peso da fonte */
}
```

### Barra de Progresso
```css
.preloader-progress-bar {
    background: linear-gradient(90deg, #fff, #f6c23e, #1cc88a, #36b9cc);
    transition: width 0.3s ease-out; /* Suavidade da animação */
}
```

## Compatibilidade

- ✅ Funciona com preloader de navegação
- ✅ Funciona com preloader de carregamento inicial
- ✅ Responsivo para mobile
- ✅ Compatível com todos os navegadores modernos
- ✅ Não interfere com funcionalidades existentes

## Notas Técnicas

- O progresso é resetado automaticamente quando o preloader é ocultado
- A animação automática tem duração configurável
- O contador sempre chega a 100% antes de ocultar o preloader
- Suporte a múltiplas instâncias de progresso simultâneas

## Estrutura HTML Gerada

```html
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
            <span class="loading-text">Carregando dados</span>
            <span class="loading-dots"></span>
        </div>
    </div>
</div>
```

## Implementação Concluída

✅ Contador de progresso de 0% a 100%  
✅ Barra de progresso visual  
✅ Animação automática  
✅ Controle manual  
✅ Estilos responsivos  
✅ Integração com preloader existente  
✅ Funções globais expostas  
✅ Documentação completa  

O preloader agora oferece uma experiência de carregamento muito mais informativa e profissional para os usuários da Financeira Autêntica.