/**
 * Gestionnaire global des paramètres EazzyLotto
 * Applique automatiquement les paramètres sur toutes les pages
 */

class SettingsManager {
    constructor() {
        this.settings = this.loadSettings();
        this.initializeEventListeners();
        this.applySettings();
    }

    loadSettings() {
        const saved = localStorage.getItem('eazzylotto_settings');
        return saved ? JSON.parse(saved) : this.getDefaultSettings();
    }

    getDefaultSettings() {
        return {
            defaultUniverse: 'mundo',
            confidenceLevel: '80',
            theme: 'light',
            language: 'fr',
            historyDuration: '90',
            notifications: true,
            animations: true,
            autoLogin: true,
            autoSave: true
        };
    }

    saveSettings(newSettings) {
        this.settings = { ...this.settings, ...newSettings };
        localStorage.setItem('eazzylotto_settings', JSON.stringify(this.settings));
        this.applySettings();
        this.notifySettingsChanged();
    }

    applySettings() {
        // Appliquer le thème
        this.applyTheme();
        
        // Appliquer les animations
        this.applyAnimations();
        
        // Configurer l'univers par défaut
        this.setDefaultUniverse();
        
        // Appliquer la langue
        this.applyLanguage();
    }

    applyTheme() {
        const body = document.body;
        if (this.settings.theme === 'dark') {
            body.classList.add('dark-theme');
        } else {
            body.classList.remove('dark-theme');
        }
    }

    applyAnimations() {
        const body = document.body;
        if (!this.settings.animations) {
            body.classList.add('no-animations');
        } else {
            body.classList.remove('no-animations');
        }
    }

    setDefaultUniverse() {
        // Stocker l'univers par défaut globalement
        window.defaultUniverse = this.settings.defaultUniverse;
        
        // Pré-sélectionner dans les sélecteurs d'univers
        const universeSelectors = document.querySelectorAll('select[name="universe"], #universe-select');
        universeSelectors.forEach(select => {
            if (select.value === '' || select.value === 'default') {
                select.value = this.settings.defaultUniverse;
            }
        });
    }

    applyLanguage() {
        // Appliquer la langue (pour une future implémentation i18n)
        document.documentElement.lang = this.settings.language;
    }

    initializeEventListeners() {
        // Écouter les changements de paramètres
        window.addEventListener('settingsChanged', (event) => {
            this.settings = event.detail;
            this.applySettings();
        });

        // Auto-sauvegarder si activé
        if (this.settings.autoSave) {
            this.setupAutoSave();
        }
    }

    setupAutoSave() {
        // Sauvegarder automatiquement les données importantes
        setInterval(() => {
            const currentData = {
                lastActivity: new Date().toISOString(),
                currentPage: window.location.pathname
            };
            localStorage.setItem('eazzylotto_activity', JSON.stringify(currentData));
        }, 30000); // Toutes les 30 secondes
    }

    notifySettingsChanged() {
        // Notifier les autres composants
        window.dispatchEvent(new CustomEvent('settingsApplied', { 
            detail: this.settings 
        }));

        // Afficher une notification si activé
        if (this.settings.notifications) {
            this.showNotification('Paramètres appliqués avec succès !', 'success');
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `settings-notification settings-notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 6px;
            color: white;
            z-index: 3000;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideInRight 0.3s ease-out;
            background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // Méthodes utilitaires pour les autres pages
    getConfidenceLevel() {
        return parseInt(this.settings.confidenceLevel);
    }

    getDefaultUniverse() {
        return this.settings.defaultUniverse;
    }

    shouldShowNotifications() {
        return this.settings.notifications;
    }

    shouldUseAnimations() {
        return this.settings.animations;
    }

    getTheme() {
        return this.settings.theme;
    }

    getLanguage() {
        return this.settings.language;
    }
}

// Styles CSS pour les animations et thèmes
const settingsStyles = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .no-animations * {
        animation-duration: 0s !important;
        transition-duration: 0s !important;
    }
    
    .dark-theme {
        background: #1a1a1a !important;
        color: #e0e0e0 !important;
    }
    
    .dark-theme .container,
    .dark-theme .dashboard-card,
    .dark-theme .settings-section {
        background: #2d2d2d !important;
        color: #e0e0e0 !important;
    }
    
    .dark-theme .nav-item {
        color: #b0b0b0 !important;
    }
    
    .dark-theme .nav-item:hover,
    .dark-theme .nav-item.active {
        background: #3d3d3d !important;
        color: #ffd700 !important;
    }
`;

// Injecter les styles
if (!document.getElementById('settings-styles')) {
    const settingsStyleSheet = document.createElement('style');
    settingsStyleSheet.id = 'settings-styles';
    settingsStyleSheet.textContent = settingsStyles;
    document.head.appendChild(settingsStyleSheet);
}

// Initialiser le gestionnaire de paramètres
window.settingsManager = new SettingsManager();

// Export pour utilisation dans d'autres scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SettingsManager;
}