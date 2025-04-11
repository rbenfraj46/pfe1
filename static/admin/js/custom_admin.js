// Fonctions pour améliorer l'interface d'administration
document.addEventListener('DOMContentLoaded', function() {
    // Animer l'apparition des messages
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        message.classList.add('fade-in');
        // Auto-masquer les messages après 5 secondes
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });

    // Améliorer les filtres de recherche
    const searchInputs = document.querySelectorAll('.search-form input[type="text"]');
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(function(e) {
            const form = e.target.closest('form');
            if (form) {
                form.submit();
            }
        }, 500));
    });

    // Ajouter des tooltips aux icônes d'aide
    const helpIcons = document.querySelectorAll('.help-icon');
    helpIcons.forEach(icon => {
        const helpText = icon.getAttribute('data-help-text');
        if (helpText) {
            icon.setAttribute('data-tooltip', helpText);
        }
    });

    // Confirmation personnalisée pour les actions de suppression
    const deleteButtons = document.querySelectorAll('.delete-button, .deletelink');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Êtes-vous sûr de vouloir supprimer cet élément ? Cette action est irréversible.')) {
                e.preventDefault();
            }
        });
    });

    // Améliorer les sélecteurs de date
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        input.addEventListener('change', function() {
            validateDateRange(input);
        });
    });

    // Ajouter des indicateurs de chargement
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            showLoadingIndicator();
        });
    });

    // Améliorer la navigation dans les tableaux
    const tables = document.querySelectorAll('.results');
    tables.forEach(table => {
        makeTableRowsClickable(table);
        addTableSorting(table);
    });
});

// Utilitaires
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showLoadingIndicator() {
    const loader = document.createElement('div');
    loader.className = 'loading-indicator';
    loader.innerHTML = '<div class="spinner"></div>';
    document.body.appendChild(loader);
}

function validateDateRange(input) {
    const startDate = document.querySelector('input[name="start_date"]');
    const endDate = document.querySelector('input[name="end_date"]');
    
    if (startDate && endDate) {
        const start = new Date(startDate.value);
        const end = new Date(endDate.value);
        
        if (end <= start) {
            alert('La date de fin doit être postérieure à la date de début.');
            input.value = '';
        }
    }
}

function makeTableRowsClickable(table) {
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const link = row.querySelector('td:first-child a');
        if (link) {
            row.style.cursor = 'pointer';
            row.addEventListener('click', function(e) {
                if (!e.target.matches('a, input, button')) {
                    link.click();
                }
            });
        }
    });
}

function addTableSorting(table) {
    const headers = table.querySelectorAll('thead th:not(.action-checkbox-column)');
    headers.forEach(header => {
        if (!header.classList.contains('sortable')) {
            header.classList.add('sortable');
            header.addEventListener('click', function() {
                const isAscending = !this.classList.contains('sorted-asc');
                sortTable(table, Array.from(headers).indexOf(this), isAscending);
                headers.forEach(h => {
                    h.classList.remove('sorted-asc', 'sorted-desc');
                });
                this.classList.add(isAscending ? 'sorted-asc' : 'sorted-desc');
            });
        }
    });
}

function sortTable(table, columnIndex, ascending) {
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const sortedRows = rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        return ascending ? 
            aValue.localeCompare(bValue, undefined, {numeric: true}) :
            bValue.localeCompare(aValue, undefined, {numeric: true});
    });
    
    const tbody = table.querySelector('tbody');
    sortedRows.forEach(row => tbody.appendChild(row));
}