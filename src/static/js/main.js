// Main JavaScript for Financeira Autêntica

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Utility Functions
const Utils = {
    // Format currency
    formatCurrency: function(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    },

    // Format date
    formatDate: function(dateString) {
        if (!dateString) return 'N/A';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('pt-BR');
        } catch (e) {
            return dateString;
        }
    },

    // Format phone number
    formatPhone: function(ddd, number) {
        if (!ddd || !number) return '';
        
        const dddClean = ddd.replace(/\D/g, '');
        const numberClean = number.replace(/\D/g, '');
        
        if (numberClean.length === 9) {
            return `(${dddClean}) ${numberClean.substr(0, 5)}-${numberClean.substr(5)}`;
        } else if (numberClean.length === 8) {
            return `(${dddClean}) ${numberClean.substr(0, 4)}-${numberClean.substr(4)}`;
        }
        
        return `(${dddClean}) ${numberClean}`;
    },

    // Format CPF/CNPJ
    formatCpfCnpj: function(value) {
        if (!value) return '';
        
        const numbers = value.replace(/\D/g, '');
        
        if (numbers.length === 11) {
            return numbers.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
        } else if (numbers.length === 14) {
            return numbers.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
        }
        
        return value;
    },

    // Show loading state
    showLoading: function(element) {
        element.classList.add('loading');
        element.disabled = true;
    },

    // Hide loading state
    hideLoading: function(element) {
        element.classList.remove('loading');
        element.disabled = false;
    },

    // Show toast notification
    showToast: function(message, type = 'success') {
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => {
            toastContainer.removeChild(toast);
        });
    },

    // Create toast container
    createToastContainer: function() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    },

    // Debounce function
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Copy to clipboard
    copyToClipboard: function(text) {
        return navigator.clipboard.writeText(text).then(() => {
            this.showToast('Copiado para a área de transferência!', 'success');
        }).catch(err => {
            console.error('Erro ao copiar:', err);
            this.showToast('Erro ao copiar para a área de transferência', 'danger');
        });
    }
};

// Search functionality
const Search = {
    init: function() {
        const searchInputs = document.querySelectorAll('input[name="search"]');
        searchInputs.forEach(input => {
            input.addEventListener('input', Utils.debounce(this.handleSearch.bind(this), 300));
        });
    },

    handleSearch: function(event) {
        const query = event.target.value.trim();
        if (query.length >= 3 || query.length === 0) {
            this.performSearch(query);
        }
    },

    performSearch: function(query) {
        // This would be implemented based on the specific page
        console.log('Searching for:', query);
    }
};

// Table functionality
const Table = {
    init: function() {
        this.initSorting();
        this.initFiltering();
    },

    initSorting: function() {
        const sortableHeaders = document.querySelectorAll('th[data-sort]');
        sortableHeaders.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', this.handleSort.bind(this));
        });
    },

    handleSort: function(event) {
        const header = event.target;
        const column = header.dataset.sort;
        const table = header.closest('table');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        const isAscending = header.classList.contains('sort-asc');
        
        // Remove sort classes from all headers
        table.querySelectorAll('th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });
        
        // Add appropriate class to current header
        header.classList.add(isAscending ? 'sort-desc' : 'sort-asc');
        
        // Sort rows
        rows.sort((a, b) => {
            const aValue = a.querySelector(`td[data-sort="${column}"]`)?.textContent.trim() || '';
            const bValue = b.querySelector(`td[data-sort="${column}"]`)?.textContent.trim() || '';
            
            const comparison = aValue.localeCompare(bValue, 'pt-BR', { numeric: true });
            return isAscending ? -comparison : comparison;
        });
        
        // Reorder rows in DOM
        rows.forEach(row => tbody.appendChild(row));
    },

    initFiltering: function() {
        const filterInputs = document.querySelectorAll('[data-filter]');
        filterInputs.forEach(input => {
            input.addEventListener('input', Utils.debounce(this.handleFilter.bind(this), 300));
        });
    },

    handleFilter: function(event) {
        const input = event.target;
        const filterType = input.dataset.filter;
        const filterValue = input.value.toLowerCase();
        const table = document.querySelector('table');
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            let shouldShow = false;
            
            cells.forEach(cell => {
                if (cell.textContent.toLowerCase().includes(filterValue)) {
                    shouldShow = true;
                }
            });
            
            row.style.display = shouldShow ? '' : 'none';
        });
    }
};

// Export functionality
const Export = {
    toCSV: function(data, filename = 'export.csv') {
        const csvContent = this.arrayToCSV(data);
        this.downloadFile(csvContent, filename, 'text/csv');
    },

    toJSON: function(data, filename = 'export.json') {
        const jsonContent = JSON.stringify(data, null, 2);
        this.downloadFile(jsonContent, filename, 'application/json');
    },

    arrayToCSV: function(data) {
        if (!data.length) return '';
        
        const headers = Object.keys(data[0]);
        const csvRows = [
            headers.join(','),
            ...data.map(row => 
                headers.map(header => {
                    const value = row[header] || '';
                    return `"${value.toString().replace(/"/g, '""')}"`;
                }).join(',')
            )
        ];
        
        return csvRows.join('\n');
    },

    downloadFile: function(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        
        link.href = url;
        link.download = filename;
        link.style.display = 'none';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        URL.revokeObjectURL(url);
        
        Utils.showToast(`Arquivo ${filename} baixado com sucesso!`, 'success');
    }
};

// API helper
const API = {
    baseURL: '',
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            Utils.showToast('Erro na comunicação com o servidor', 'danger');
            throw error;
        }
    },

    async get(endpoint) {
        return this.request(endpoint);
    },

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }
};

// Initialize modules when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    Search.init();
    Table.init();
});

// Global error handler
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    Utils.showToast('Ocorreu um erro inesperado', 'danger');
});

// Global unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    Utils.showToast('Erro na aplicação', 'danger');
});

// Export utilities globally
window.Utils = Utils;
window.Search = Search;
window.Table = Table;
window.Export = Export;
window.API = API;