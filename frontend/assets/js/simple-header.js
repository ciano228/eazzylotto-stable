/**
 * Header simple et fonctionnel pour EazzyLotto
 */

const SimpleHeader = {
    generateHeader: function(currentPage = '', showUserInfo = false) {
        return `
            <header style="position: fixed; top: 0; left: 0; right: 0; background: rgba(30, 60, 114, 0.95); backdrop-filter: blur(10px); z-index: 1000; padding: 15px 0;">
                <div style="max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 0 20px;">
                    <a href="index.html" style="text-decoration: none;">
                        <div style="background: linear-gradient(145deg, #000, #1a1a1a); border: 3px solid #fff; border-radius: 12px; padding: 12px 20px; font-family: 'Orbitron', monospace; font-weight: 900; font-size: 18px; letter-spacing: 2px; color: #fff;">
                            EAZZYLOTTO
                        </div>
                    </a>
                    
                    <nav style="display: flex; gap: 25px; align-items: center;">
                        <a href="accueil.html" style="color: white; text-decoration: none; padding: 8px 16px; border-radius: 6px; transition: all 0.3s ease;">Accueil</a>
                        <a href="dashboard.html" style="color: white; text-decoration: none; padding: 8px 16px; border-radius: 6px; transition: all 0.3s ease;">Dashboard</a>
                        <a href="katooling-method.html" style="color: white; text-decoration: none; padding: 8px 16px; border-radius: 6px; transition: all 0.3s ease;">KATOOLING</a>
                        <a href="parametres.html" style="color: white; text-decoration: none; padding: 8px 16px; border-radius: 6px; transition: all 0.3s ease;">Paramètres</a>
                    </nav>
                    
                    ${showUserInfo ? 
                        '<div style="color: white;">Utilisateur connecté</div>' : 
                        '<div><a href="index.html" style="background: white; color: #1e3c72; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600;">Connexion</a></div>'
                    }
                </div>
            </header>
        `;
    },

    injectHeader: function(containerId, currentPage = '', options = {}) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = this.generateHeader(currentPage, options.showUserInfo);
        }
        
        // Ajouter padding au body
        document.body.style.paddingTop = '80px';
        
        // Ajouter les événements hover
        setTimeout(() => {
            document.querySelectorAll('nav a').forEach(link => {
                link.addEventListener('mouseenter', function() {
                    this.style.background = 'rgba(255, 255, 255, 0.1)';
                    this.style.color = '#ffd700';
                });
                link.addEventListener('mouseleave', function() {
                    this.style.background = 'transparent';
                    this.style.color = 'white';
                });
            });
        }, 100);
    }
};

// Export global
window.SimpleHeader = SimpleHeader;