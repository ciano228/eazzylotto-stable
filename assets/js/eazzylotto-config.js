/**
 * EazzyLotto - Configuration Globale
 * Système cohérent pour toute la chaîne : Recherche → Analyse → Prédiction → Résultats
 */

const EazzyLotto = {
    // Configuration de base
    config: {
        appName: 'EazzyLotto',
        domain: 'eazzylotto.com',
        version: '1.0.0',
        apiBase: 'http://localhost:8081/api',
        frontendPort: 8081
    },

    // Thème et couleurs
    theme: {
        primary: '#1e3c72',
        secondary: '#2a5298',
        accent: '#ffd700',
        success: '#27ae60',
        warning: '#f39c12',
        danger: '#e74c3c',
        info: '#3498db',
        dark: '#2c3e50',
        light: '#f8f9fa'
    },

    // Univers de données
    universes: {
        mundo: {
            name: 'Mundo',
            color: '#3498db',
            description: 'Univers des combinaisons mondiales'
        },
        fruity: {
            name: 'Fruity',
            color: '#e74c3c',
            description: 'Univers des combinaisons fruitées'
        },
        trigga: {
            name: 'Trigga',
            color: '#f39c12',
            description: 'Univers des combinaisons déclencheurs'
        },
        roaster: {
            name: 'Roaster',
            color: '#9b59b6',
            description: 'Univers des combinaisons torréfiées'
        },
        sunshine: {
            name: 'Sunshine',
            color: '#f1c40f',
            description: 'Univers des combinaisons ensoleillées'
        }
    },

    // Types de marquage
    markingTypes: {
        chip: 'Par Chip',
        combination: 'Par Combinaison',
        denomination: 'Par Dénomination',
        tome: 'Par Tome',
        granque: 'Par Granque',
        forme: 'Par Forme',
        parite: 'Par Parité',
        zone: 'Par Zone Géométrique'
    },

    // Navigation principale
    navigation: {
        dashboard: {
            title: 'Tableau de Bord',
            icon: '📊',
            url: 'dashboard.html',
            description: 'Vue d\'ensemble et statistiques'
        },
        katooling: {
            title: 'Méthode KATOOLING',
            icon: '🔬',
            url: 'katooling-method.html',
            description: 'Notre méthode révolutionnaire'
        },
        research: {
            title: 'Recherche & Données',
            icon: '🔍',
            url: 'katula-multi-universe.html',
            description: 'Exploration des bases de données'
        },
        analysis: {
            title: 'Analyse Temporelle',
            icon: '📈',
            url: 'katula-temporal-analysis.html',
            description: 'Comparaisons et tendances temporelles'
        },
        prediction: {
            title: 'Prédictions IA',
            icon: '🎯',
            url: 'lstm-neural-network.html',
            description: 'Génération de prédictions intelligentes'
        },
        results: {
            title: 'Résultats Gagnants',
            icon: '🏆',
            url: 'prediction-panel.html',
            description: 'Numéros gagnants et performances'
        },
        history: {
            title: 'Historique',
            icon: '📅',
            url: 'gap-analysis.html',
            description: 'Historique complet des analyses'
        },
        settings: {
            title: 'Paramètres',
            icon: '⚙️',
            url: 'test-sessions.html',
            description: 'Configuration et préférences'
        }
    },

    // Utilitaires
    utils: {
        // Générer le logo HTML avec le nouveau design
        generateLogo: function(size = 'normal') {
            const sizes = {
                small: { padding: '6px 12px', fontSize: '14px', ballSize: '16px', ballFont: '8px' },
                normal: { padding: '8px 16px', fontSize: '18px', ballSize: '20px', ballFont: '10px' },
                large: { padding: '12px 24px', fontSize: '24px', ballSize: '28px', ballFont: '14px' }
            };
            
            const style = sizes[size] || sizes.normal;
            
            return `
                <div class="eazzylotto-logo" style="
                    background: linear-gradient(145deg, #000 0%, #1a1a1a 100%);
                    border: 2px solid #fff;
                    border-radius: 10px;
                    padding: ${style.padding};
                    font-family: 'Orbitron', monospace;
                    font-weight: 900;
                    font-size: ${style.fontSize};
                    letter-spacing: 1px;
                    display: inline-flex;
                    align-items: center;
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                ">
                    <div style="display: flex; align-items: center; gap: 1px;">
                        <span style="color: #fff;">EAZZY</span>
                        <span style="color: #ff4757; font-weight: 900;">L</span>
                        <span style="
                            display: inline-flex;
                            align-items: center;
                            justify-content: center;
                            width: ${style.ballSize};
                            height: ${style.ballSize};
                            border-radius: 50%;
                            background: linear-gradient(145deg, #ffd700, #ffed4e);
                            color: #000;
                            font-weight: 900;
                            font-size: ${style.ballFont};
                            margin: 0 1px;
                        ">9</span>
                        <span style="color: #2ed573; font-weight: 900;">T</span>
                        <span style="color: #ff4757; font-weight: 900;">T</span>
                        <span style="
                            display: inline-flex;
                            align-items: center;
                            justify-content: center;
                            width: ${style.ballSize};
                            height: ${style.ballSize};
                            border-radius: 50%;
                            background: linear-gradient(145deg, #4facfe, #00f2fe);
                            color: #fff;
                            font-weight: 900;
                            font-size: ${style.ballFont};
                            margin: 0 1px;
                        ">2</span>
                    </div>
                </div>
            `;
        },

        // Générer la navigation
        generateNavigation: function(currentPage = '') {
            let navHTML = '<nav class="eazzylotto-nav">';
            
            Object.entries(this.navigation).forEach(([key, nav]) => {
                const activeClass = currentPage === key ? 'active' : '';
                navHTML += `
                    <a href="${nav.url}" class="nav-item ${activeClass}" data-page="${key}">
                        <span class="nav-icon">${nav.icon}</span>
                        <span class="nav-title">${nav.title}</span>
                    </a>
                `;
            });
            
            navHTML += '</nav>';
            return navHTML;
        },

        // Formater les nombres
        formatNumber: function(num) {
            return new Intl.NumberFormat('fr-FR').format(num);
        },

        // Formater les dates
        formatDate: function(date) {
            return new Intl.DateTimeFormat('fr-FR').format(new Date(date));
        },

        // Générer des couleurs pour les univers
        getUniverseColor: function(universe) {
            return this.universes[universe]?.color || this.theme.primary;
        },

        // Notification système
        showNotification: function(message, type = 'info') {
            const notification = document.createElement('div');
            notification.className = `eazzylotto-notification ${type}`;
            notification.innerHTML = `
                <div class="notification-content">
                    <span class="notification-icon">${this.getNotificationIcon(type)}</span>
                    <span class="notification-message">${message}</span>
                </div>
            `;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.classList.add('show');
            }, 100);
            
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        },

        getNotificationIcon: function(type) {
            const icons = {
                success: '✅',
                warning: '⚠️',
                danger: '❌',
                info: 'ℹ️'
            };
            return icons[type] || icons.info;
        },

        // Gestion du stockage local
        storage: {
            set: function(key, value) {
                localStorage.setItem(`eazzylotto_${key}`, JSON.stringify(value));
            },
            
            get: function(key) {
                const item = localStorage.getItem(`eazzylotto_${key}`);
                return item ? JSON.parse(item) : null;
            },
            
            remove: function(key) {
                localStorage.removeItem(`eazzylotto_${key}`);
            }
        },

        // Gestion des sessions utilisateur
        user: {
            login: function(userData) {
                this.storage.set('user', userData);
                this.storage.set('loginTime', Date.now());
            },
            
            logout: function() {
                this.storage.remove('user');
                this.storage.remove('loginTime');
                window.location.href = 'index.html';
            },
            
            isLoggedIn: function() {
                const user = this.storage.get('user');
                const loginTime = this.storage.get('loginTime');
                
                if (!user || !loginTime) return false;
                
                // Session expire après 24h
                const sessionDuration = 24 * 60 * 60 * 1000;
                return (Date.now() - loginTime) < sessionDuration;
            },
            
            getCurrentUser: function() {
                return this.storage.get('user');
            }
        }
    },

    // Initialisation globale
    init: function() {
        // Vérifier la session utilisateur
        if (!this.utils.user.isLoggedIn() && !window.location.pathname.includes('index.html')) {
            window.location.href = 'index.html';
            return;
        }

        // Ajouter les styles globaux
        this.addGlobalStyles();
        
        // Initialiser les composants communs
        this.initCommonComponents();
        
        console.log('🎯 EazzyLotto initialisé avec succès');
    },

    // Ajouter les styles globaux
    addGlobalStyles: function() {
        const styles = `
            <style>
                .eazzylotto-notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: white;
                    border-radius: 8px;
                    padding: 15px 20px;
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                    z-index: 10000;
                    transform: translateX(400px);
                    transition: all 0.3s ease;
                    border-left: 4px solid ${this.theme.info};
                }
                
                .eazzylotto-notification.show {
                    transform: translateX(0);
                }
                
                .eazzylotto-notification.success {
                    border-left-color: ${this.theme.success};
                }
                
                .eazzylotto-notification.warning {
                    border-left-color: ${this.theme.warning};
                }
                
                .eazzylotto-notification.danger {
                    border-left-color: ${this.theme.danger};
                }
                
                .notification-content {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .notification-icon {
                    font-size: 18px;
                }
                
                .notification-message {
                    font-weight: 500;
                    color: ${this.theme.dark};
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    },

    // Initialiser les composants communs
    initCommonComponents: function() {
        // Ajouter les gestionnaires d'événements globaux
        document.addEventListener('keydown', (e) => {
            // Raccourci clavier pour la déconnexion (Ctrl+Shift+L)
            if (e.ctrlKey && e.shiftKey && e.key === 'L') {
                this.utils.user.logout();
            }
        });
    }
};

// Auto-initialisation
document.addEventListener('DOMContentLoaded', function() {
    EazzyLotto.init();
});

// Export global
window.EazzyLotto = EazzyLotto;