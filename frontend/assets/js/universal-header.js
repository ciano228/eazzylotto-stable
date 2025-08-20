/**
 * EazzyLotto Universal Header
 * Header cohérent avec le logo authentique pour toutes les pages
 */

const UniversalHeader = {
    // Générer le header universel
    generateHeader: function(currentPage = '', options = {}) {
        const config = {
            showNavigation: options.showNavigation !== false,
            showUserInfo: options.showUserInfo || false,
            transparent: options.transparent || false,
            ...options
        };

        return `
            <header class="eazzylotto-header ${config.transparent ? 'transparent' : ''}">
                <div class="header-container">
                    ${this.generateLogo()}
                    
                    ${config.showNavigation ? this.generateNavigation(currentPage) : ''}
                    
                    ${config.showUserInfo ? this.generateUserInfo() : this.generateAuthButtons()}
                </div>
            </header>
        `;
    },

    // Générer le logo authentique
    generateLogo: function() {
        return `
            <a href="index.html" class="eazzylotto-logo-link">
                <div class="eazzylotto-logo">
                    <div class="logo-text">
                        <span class="eazzy">EAZZY</span>
                        <span class="l-red">L</span>
                        <span class="o-ball">9</span>
                        <span class="t-green">T</span>
                        <span class="t-red">T</span>
                        <span class="o-ball blue">2</span>
                    </div>
                </div>
            </a>
        `;
    },

    // Générer la navigation
    generateNavigation: function(currentPage = '') {
        const navItems = [
            { key: 'accueil', label: 'Accueil', url: 'index.html' },
            { key: 'katooling', label: 'Méthode KATOOLING', url: 'katooling-method.html' },
            { key: 'dashboard', label: 'Dashboard', url: 'dashboard.html' },
            { key: 'evenements', label: 'Événements', url: 'evenements.html' },
            { key: 'actualites', label: 'Actualités', url: 'actualites.html' },
            { key: 'support', label: 'Support', url: 'support.html' },
            { key: 'contact', label: 'Contact', url: 'contact.html' },
            { key: 'abonnement', label: 'Abonnement', url: 'abonnement.html' }
        ];

        let navHTML = '<nav class="header-nav">';
        navItems.forEach(item => {
            const activeClass = currentPage === item.key ? 'active' : '';
            navHTML += `
                <a href="${item.url}" class="nav-link ${activeClass}" translate="no">
                    ${item.label}
                </a>
            `;
        });
        navHTML += '</nav>';

        return navHTML;
    },

    // Générer les boutons d'authentification
    generateAuthButtons: function() {
        return `
            <div class="auth-buttons">
                <a href="login.html" class="auth-btn login-btn">Se connecter</a>
                <a href="signup.html" class="auth-btn signup-btn">S'inscrire</a>
            </div>
        `;
    },

    // Générer les infos utilisateur
    generateUserInfo: function() {
        return `
            <div class="user-info">
                <span class="user-welcome">Bienvenue, <strong>Utilisateur</strong></span>
                <div class="user-avatar">U</div>
                <button class="logout-btn" onclick="UniversalHeader.logout()">Déconnexion</button>
            </div>
        `;
    },

    // Injecter le header dans une page
    injectHeader: function(containerId = 'header-container', currentPage = '', options = {}) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = this.generateHeader(currentPage, options);
        } else {
            // Si pas de container spécifique, injecter au début du body
            document.body.insertAdjacentHTML('afterbegin', this.generateHeader(currentPage, options));
        }
        
        this.addHeaderStyles();
        this.initHeaderInteractions();
        
        // Charger le gestionnaire de paramètres si disponible
        this.loadSettingsManager();
    },
    
    // Charger le gestionnaire de paramètres
    loadSettingsManager: function() {
        if (!document.getElementById('settings-manager-script')) {
            const script = document.createElement('script');
            script.id = 'settings-manager-script';
            script.src = 'assets/js/settings-manager.js';
            document.head.appendChild(script);
        }
    },

    // Ajouter les styles du header
    addHeaderStyles: function() {
        if (document.getElementById('universal-header-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'universal-header-styles';
        styles.textContent = `
            .eazzylotto-header {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
                z-index: 1000;
                padding: 15px 0;
                transition: all 0.3s ease;
            }

            .eazzylotto-header.transparent {
                background: transparent;
                backdrop-filter: none;
                border-bottom: none;
            }

            .header-container {
                max-width: 1400px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0 20px;
            }

            .eazzylotto-logo-link {
                text-decoration: none;
            }

            .eazzylotto-logo {
                background: linear-gradient(145deg, #000 0%, #1a1a1a 100%);
                border: 3px solid #fff;
                border-radius: 12px;
                padding: 12px 20px;
                font-family: 'Orbitron', monospace;
                font-weight: 900;
                font-size: 18px;
                letter-spacing: 2px;
                display: flex;
                align-items: center;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
                position: relative;
                transition: all 0.3s ease;
            }

            .eazzylotto-logo:hover {
                transform: translateY(-2px);
                box-shadow: 0 12px 35px rgba(0, 0, 0, 0.4);
            }

            .eazzylotto-logo::before {
                content: '';
                position: absolute;
                top: -2px; 


                 
                left: -2px;
                right: -2px;
                bottom: -2px;
                background: linear-gradient(45deg, #4facfe, #00f2fe, #ffd700, #ff6b6b);
                border-radius: 15px;
                z-index: -1;
                animation: rainbow-border 3s linear infinite;
            }

            @keyframes rainbow-border {
                0% { filter: hue-rotate(0deg); }
                100% { filter: hue-rotate(360deg); }
            }

            .logo-text {
                display: flex;
                align-items: center;
                gap: 2px;
            }

            .eazzylotto-logo .eazzy {
                color: #fff;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            }

            .eazzylotto-logo .l-red {
                color: #ff4757;
                font-weight: 900;
                text-shadow: 0 0 10px rgba(255, 71, 87, 0.5);
            }

            .eazzylotto-logo .o-ball {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 24px;
                height: 24px;
                border-radius: 50%;
                background: linear-gradient(145deg, #ffd700, #ffed4e);
                color: #000;
                font-weight: 900;
                font-size: 12px;
                margin: 0 1px;
                box-shadow: 0 4px 8px rgba(255, 215, 0, 0.4);
                animation: ball-glow 2s ease-in-out infinite alternate;
            }

            .eazzylotto-logo .o-ball.blue {
                background: linear-gradient(145deg, #4facfe, #00f2fe);
                color: #fff;
                box-shadow: 0 4px 8px rgba(79, 172, 254, 0.4);
            }

            @keyframes ball-glow {
                0% { box-shadow: 0 4px 8px rgba(255, 215, 0, 0.4); }
                100% { box-shadow: 0 6px 20px rgba(255, 215, 0, 0.8); }
            }

            .eazzylotto-logo .t-green {
                color: #2ed573;
                font-weight: 900;
                text-shadow: 0 0 10px rgba(46, 213, 115, 0.5);
            }

            .eazzylotto-logo .t-red {
                color: #ff4757;
                font-weight: 900;
                text-shadow: 0 0 10px rgba(255, 71, 87, 0.5);
            }

            .header-nav {
                display: flex;
                gap: 25px;
                align-items: center;
            }

            .nav-link {
                color: white;
                text-decoration: none;
                font-weight: 500;
                padding: 8px 16px;
                border-radius: 6px;
                transition: all 0.3s ease;
                position: relative;
            }

            .nav-link:hover,
            .nav-link.active {
                background: rgba(255, 255, 255, 0.1);
                color: #ffd700;
            }

            .nav-link.active::after {
                content: '';
                position: absolute;
                bottom: -15px;
                left: 50%;
                transform: translateX(-50%);
                width: 6px;
                height: 6px;
                background: #ffd700;
                border-radius: 50%;
            }

            .auth-buttons {
                display: flex;
                gap: 15px;
                align-items: center;
            }

            .auth-btn {
                padding: 10px 20px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s ease;
                border: 2px solid transparent;
            }

            .login-btn {
                background: white;
                color: #1e3c72;
            }

            .login-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(255, 255, 255, 0.3);
            }

            .signup-btn {
                background: transparent;
                color: white;
                border-color: white;
            }

            .signup-btn:hover {
                background: white;
                color: #1e3c72;
            }

            .user-info {
                display: flex;
                align-items: center;
                gap: 15px;
                color: white;
            }

            .user-welcome {
                font-size: 0.9rem;
            }

            .user-avatar {
                width: 40px;
                height: 40px;
                background: #ffd700;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                color: #1e3c72;
            }

            .logout-btn {
                background: transparent;
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                padding: 6px 12px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.8rem;
                transition: all 0.3s ease;
            }

            .logout-btn:hover {
                background: rgba(255, 255, 255, 0.1);
            }
            
            /* Quick Settings */
            .quick-settings {
                position: relative;
                margin-right: 15px;
            }
            
            .settings-toggle {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: white;
                padding: 8px 10px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s ease;
            }
            
            .settings-toggle:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: rotate(90deg);
            }
            
            .quick-settings-menu {
                position: absolute;
                top: 100%;
                right: 0;
                background: white;
                border-radius: 8px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
                padding: 15px;
                min-width: 200px;
                z-index: 1001;
                display: none;
                margin-top: 5px;
            }
            
            .quick-settings-menu.show {
                display: block;
                animation: slideDown 0.3s ease;
            }
            
            @keyframes slideDown {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .quick-settings-menu .setting-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
                color: #2c3e50;
            }
            
            .quick-settings-menu .setting-item:last-child {
                margin-bottom: 0;
                border-top: 1px solid #eee;
                padding-top: 10px;
            }
            
            .quick-settings-menu label {
                font-size: 12px;
                font-weight: 500;
            }
            
            .quick-settings-menu select {
                background: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                color: #2c3e50;
            }
            
            .theme-toggle {
                background: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px 8px;
                cursor: pointer;
                font-size: 12px;
                transition: all 0.3s ease;
            }
            
            .theme-toggle:hover {
                background: #e9ecef;
            }
            
            .settings-link {
                color: #1e3c72;
                text-decoration: none;
                font-size: 11px;
                font-weight: 500;
                padding: 4px 0;
                display: block;
                text-align: center;
            }
            
            .settings-link:hover {
                color: #2a5298;
                text-decoration: underline;
            }

            /* Responsive */
            @media (max-width: 1024px) {
                .header-nav {
                    display: none;
                }
                
                .eazzylotto-logo {
                    font-size: 16px;
                    padding: 10px 16px;
                }
                
                .eazzylotto-logo .o-ball {
                    width: 20px;
                    height: 20px;
                    font-size: 10px;
                }
            }

            @media (max-width: 768px) {
                .header-container {
                    padding: 0 15px;
                }
                
                .auth-buttons {
                    gap: 10px;
                }
                
                .auth-btn {
                    padding: 8px 16px;
                    font-size: 0.9rem;
                }
                
                .user-info {
                    gap: 10px;
                }
                
                .user-welcome {
                    display: none;
                }
            }

            /* Variables CSS globales pour thèmes */
            :root {
                --bg-color: #f8f9fa;
                --text-color: #2c3e50;
                --card-bg: white;
            }
            
            .dark-theme {
                --bg-color: #1a1a1a;
                --text-color: #e0e0e0;
                --card-bg: #2d2d2d;
            }
            
            /* Appliquer le thème seulement aux pages qui n'ont pas de fond personnalisé */
            body:not(.custom-background):not([style*="background"]) {
                background: var(--bg-color) !important;
                color: var(--text-color) !important;
                transition: background 0.3s ease, color 0.3s ease;
            }
            
            /* Préserver les fonds définis dans les styles inline ou CSS */
            body[style*="background"],
            body.custom-background {
                /* Ne pas écraser le fond personnalisé */
            }
            
            .container, .dashboard-card, .settings-section, .universe-container {
                background: var(--card-bg) !important;
                color: var(--text-color) !important;
            }

            /* Ajustement du contenu principal */
            body.has-header {
                padding-top: 80px;
            }
        `;

        document.head.appendChild(styles);
    },

    // Initialiser les interactions du header
    initHeaderInteractions: function() {
        // Animation des boules du logo
        const balls = document.querySelectorAll('.o-ball');
        balls.forEach((ball, index) => {
            setInterval(() => {
                ball.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    ball.style.transform = 'scale(1)';
                }, 200);
            }, 4000 + (index * 1000));
        });

        // Effet de scroll sur le header
        let lastScrollY = window.scrollY;
        window.addEventListener('scroll', () => {
            const header = document.querySelector('.eazzylotto-header');
            if (header) {
                if (window.scrollY > lastScrollY && window.scrollY > 100) {
                    header.style.transform = 'translateY(-100%)';
                } else {
                    header.style.transform = 'translateY(0)';
                }
                lastScrollY = window.scrollY;
            }
        });

        // Ajouter la classe au body
        document.body.classList.add('has-header');
        
        // Fermer le menu des paramètres en cliquant ailleurs
        document.addEventListener('click', function(e) {
            const menu = document.getElementById('quickSettingsMenu');
            const toggle = document.querySelector('.settings-toggle');
            if (menu && !menu.contains(e.target) && e.target !== toggle) {
                menu.classList.remove('show');
            }
        });
    },

    // Fonction de déconnexion
    logout: function() {
        if (confirm('Êtes-vous sûr de vouloir vous déconnecter ?')) {
            localStorage.removeItem('eazzylotto_user');
            localStorage.removeItem('eazzylotto_loginTime');
            window.location.href = 'index.html';
        }
    },
    
    // Fonctions pour les paramètres rapides
    toggleQuickSettings: function() {
        const menu = document.getElementById('quickSettingsMenu');
        if (menu) {
            menu.classList.toggle('show');
            
            const settings = JSON.parse(localStorage.getItem('eazzylotto_settings') || '{}');
            const langSelect = document.getElementById('headerLanguage');
            const themeBtn = document.getElementById('themeToggle');
            
            if (langSelect) langSelect.value = settings.language || 'fr';
            if (themeBtn) themeBtn.innerHTML = settings.theme === 'dark' ? '&#9728;' : '&#9789;';
        }
    },
    
    changeLanguage: function(lang) {
        const settings = JSON.parse(localStorage.getItem('eazzylotto_settings') || '{}');
        settings.language = lang;
        localStorage.setItem('eazzylotto_settings', JSON.stringify(settings));
        
        if (window.i18n) {
            window.i18n.setLanguage(lang);
        }
        
        window.dispatchEvent(new CustomEvent('settingsApplied', { detail: settings }));
    },
    
    toggleTheme: function() {
        const settings = JSON.parse(localStorage.getItem('eazzylotto_settings') || '{}');
        settings.theme = settings.theme === 'dark' ? 'light' : 'dark';
        localStorage.setItem('eazzylotto_settings', JSON.stringify(settings));
        
        const themeBtn = document.getElementById('themeToggle');
        if (themeBtn) themeBtn.innerHTML = settings.theme === 'dark' ? '&#9728;' : '&#9789;';
        
        window.dispatchEvent(new CustomEvent('settingsApplied', { detail: settings }));
    }
};

// Auto-injection si un container existe
document.addEventListener('DOMContentLoaded', function() {
    const headerContainer = document.getElementById('header-container');
    if (headerContainer) {
        const currentPage = document.body.dataset.page || '';
        const showUserInfo = document.body.dataset.showUserInfo === 'true';
        UniversalHeader.injectHeader('header-container', currentPage, { showUserInfo });
    }
    
    // Écouter les changements de paramètres pour mettre à jour le header
    window.addEventListener('settingsApplied', function(event) {
        const settings = event.detail;
        // Appliquer le thème au header si nécessaire
        const header = document.querySelector('.eazzylotto-header');
        if (header && settings.theme === 'dark') {
            header.classList.add('dark-theme');
        } else if (header) {
            header.classList.remove('dark-theme');
        }
    });
});

// Export global
window.UniversalHeader = UniversalHeader;