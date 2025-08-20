// Module d'authentification EazzyLotto
class AuthManager {
    constructor() {
        this.token = localStorage.getItem('eazzylotto_token');
        this.user = JSON.parse(localStorage.getItem('eazzylotto_user') || 'null');
        this.apiBase = 'http://localhost:8000/api';
    }

    // Inscription
    async register(userData) {
        try {
            const response = await fetch(`${this.apiBase}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            const data = await response.json();

            if (response.ok) {
                this.setAuthData(data);
                return { success: true, data };
            } else {
                return { success: false, error: data.detail || 'Erreur d\'inscription' };
            }
        } catch (error) {
            return { success: false, error: 'Erreur de connexion' };
        }
    }

    // Connexion
    async login(credentials) {
        try {
            const response = await fetch(`${this.apiBase}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(credentials)
            });

            const data = await response.json();

            if (response.ok) {
                this.setAuthData(data);
                return { success: true, data };
            } else {
                return { success: false, error: data.detail || 'Email ou mot de passe incorrect' };
            }
        } catch (error) {
            return { success: false, error: 'Erreur de connexion' };
        }
    }

    // Stocker les données d'authentification
    setAuthData(authData) {
        this.token = authData.access_token;
        this.user = {
            id: authData.user_id,
            token_type: authData.token_type
        };

        localStorage.setItem('eazzylotto_token', this.token);
        localStorage.setItem('eazzylotto_user', JSON.stringify(this.user));
    }

    // Déconnexion
    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('eazzylotto_token');
        localStorage.removeItem('eazzylotto_user');
        
        // Rediriger vers la page de connexion
        window.location.href = 'index.html';
    }

    // Vérifier si l'utilisateur est connecté
    isAuthenticated() {
        return this.token !== null && this.user !== null;
    }

    // Obtenir le token pour les requêtes API
    getAuthHeaders() {
        if (this.token) {
            return {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            };
        }
        return {
            'Content-Type': 'application/json'
        };
    }

    // Requête API authentifiée
    async apiRequest(endpoint, options = {}) {
        const url = endpoint.startsWith('http') ? endpoint : `${this.apiBase}${endpoint}`;
        
        const config = {
            ...options,
            headers: {
                ...this.getAuthHeaders(),
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, config);
            
            if (response.status === 401) {
                // Token expiré, déconnecter
                this.logout();
                return { success: false, error: 'Session expirée' };
            }

            const data = await response.json();
            
            if (response.ok) {
                return { success: true, data };
            } else {
                return { success: false, error: data.detail || 'Erreur API' };
            }
        } catch (error) {
            return { success: false, error: 'Erreur de connexion' };
        }
    }

    // Protéger une page (rediriger si non connecté)
    requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = 'index.html';
            return false;
        }
        return true;
    }

    // Afficher les informations utilisateur
    displayUserInfo(containerId) {
        const container = document.getElementById(containerId);
        if (!container || !this.isAuthenticated()) return;

        container.innerHTML = `
            <div class="user-info">
                <span class="user-welcome">👤 Utilisateur #${this.user.id}</span>
                <button class="logout-btn" onclick="auth.logout()">🚪 Déconnexion</button>
            </div>
        `;
    }
}

// Instance globale
const auth = new AuthManager();

// Styles CSS pour l'interface utilisateur
const authStyles = `
    .user-info {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 10px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        backdrop-filter: blur(10px);
    }
    
    .user-welcome {
        color: #ffd700;
        font-weight: 600;
    }
    
    .logout-btn {
        background: #ff4757;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.3s ease;
    }
    
    .logout-btn:hover {
        background: #ff3742;
        transform: translateY(-1px);
    }
    
    .auth-error {
        background: #ff4757;
        color: white;
        padding: 10px 15px;
        border-radius: 6px;
        margin: 10px 0;
        font-weight: 600;
    }
    
    .auth-success {
        background: #2ed573;
        color: white;
        padding: 10px 15px;
        border-radius: 6px;
        margin: 10px 0;
        font-weight: 600;
    }
`;

// Injecter les styles
const styleSheet = document.createElement('style');
styleSheet.textContent = authStyles;
document.head.appendChild(styleSheet);