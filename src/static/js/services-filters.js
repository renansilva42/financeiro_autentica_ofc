// Função melhorada para limpar filtros com restauração do ano padrão
function clearAllFiltersAndRestoreYear() {
    // Primeiro, fazer scroll para a seção de filtros
    const filterSection = document.getElementById('filtros-section');
    if (filterSection) {
        // Calcular a posição exata da seção de filtros
        const rect = filterSection.getBoundingClientRect();
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const targetPosition = rect.top + scrollTop - 120; // Offset para compensar o header

        // Fazer scroll suave para a posição calculada
        try {
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        } catch (e) {
            // Fallback para navegadores mais antigos
            window.scrollTo(0, targetPosition);
        }

        // Adicionar efeito visual temporário para destacar a seção
        const card = filterSection.querySelector('.card');
        if (card) {
            card.style.boxShadow = '0 0 20px rgba(255, 193, 7, 0.4)'; // Cor amarela para indicar limpeza
            card.style.transition = 'box-shadow 0.3s ease';
            setTimeout(() => {
                card.style.boxShadow = '';
            }, 1500);
        }

        console.log('Scroll para filtros executado antes de limpar');
    }

    // Aguardar um pouco para o scroll completar, depois redirecionar
    // Quando limpar todos os filtros, voltar para o filtro de ano atual (padrão)
    setTimeout(() => {
        const currentYear = new Date().getFullYear();
        window.location.href = window.location.pathname + "?year=" + currentYear + "#filtros-section";
    }, 300);
}

// Sobrescrever a função original para usar a nova lógica
function clearFiltersWithScroll() {
    clearAllFiltersAndRestoreYear();
}