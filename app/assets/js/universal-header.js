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
            { key: 'accueil', label: 'Accueil', url: 'accueil.html' },
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
                <a href="${item.url}" class="nav-link ${activeClass}">
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
    },

    // Fonction de déconnexion
    logout: function() {
        if (confirm('Êtes-vous sûr de vouloir vous déconnecter ?')) {
            // Supprimer les données de session
            localStorage.removeItem('eazzylotto_user');
            localStorage.removeItem('eazzylotto_loginTime');
            
            // Rediriger vers la page d'accueil
            window.location.href = 'index.html';
        }
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
});

// Export global
window.UniversalHeader = UniversalHeader;