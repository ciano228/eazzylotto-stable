/**
 * EazzyLotto Application Stability Manager
 * Système de verrouillage pour éviter les variations non désirées
 */

const AppStability = {
    // Configuration stable verrouillée
    STABLE_CONFIG: {
        LOGO_STANDARD: 'EAZZY + L9TT2 (fond noir)',
        API_PORT: 8000,
        FRONTEND_PORT: 8081,
        HEADER_COMPONENT: 'universal-header.js',
        
        STABLE_PAGES: [
            'index.html',
            'dashboard.html', 
            'katooling-workflow.html',
            'prediction-panel.html',
            'pattern-viewer.html',
            'results-history.html',
            'advanced-journal.html'
        ],
        
        NAVIGATION_LINKS: {
            'dashboard_katooling': 'katooling-workflow.html',
            'dashboard_predictions': 'prediction-panel.html',
            'dashboard_patterns': 'pattern-viewer.html',
            'dashboard_results': 'results-history.html'
        }
    },

    // Vérifier la stabilité au chargement
    checkStability: function() {
        // Vérifier que le header universel est présent
        if (!document.getElementById('header-container')) {
            console.warn('⚠️ Header container manquant - stabilité compromise');
        }
        
        // Vérifier que UniversalHeader est chargé
        if (typeof UniversalHeader === 'undefined') {
            console.warn('⚠️ UniversalHeader non chargé - stabilité compromise');
        }
        
        // Marquer la page comme stable
        document.body.setAttribute('data-stable', 'true');
        console.log('✅ Page marquée comme stable');
    },

    // Forcer la stabilité des liens
    enforceStableLinks: function() {
        const links = document.querySelectorAll('a[href]');
        links.forEach(link => {
            const href = link.getAttribute('href');
            
            // Corriger les liens vers des pages obsolètes
            if (href === 'katooling-method.html') {
                link.setAttribute('href', 'katooling-workflow.html');
                console.log('🔧 Lien corrigé: katooling-method.html → katooling-workflow.html');
            }
        });
    },

    // Initialiser la stabilité
    init: function() {
        document.addEventListener('DOMContentLoaded', () => {
            this.checkStability();
            this.enforceStableLinks();
        });
    }
};

// Auto-initialisation
AppStability.init();

// Export global
window.AppStability = AppStability;