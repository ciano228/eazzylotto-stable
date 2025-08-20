/**
 * Système de traduction simple pour EazzyLotto
 */

const translations = {
    fr: {
        // Navigation
        'Accueil': 'Accueil',
        'Dashboard': 'Tableau de Bord',
        'Tableau de Bord': 'Tableau de Bord',
        'Méthode KATOOLING': 'Méthode KATOOLING',
        'Événements': 'Événements',
        'Actualités': 'Actualités',
        'Support': 'Support',
        'Contact': 'Contact',
        'Abonnement': 'Abonnement',
        'Paramètres': 'Paramètres',
        'Katula Multi-Univers': 'Katula Multi-Univers',
        'Recherche & Données': 'Recherche & Données',
        'Analyse Temporelle': 'Analyse Temporelle',
        'Patterns & Résultats': 'Patterns & Résultats',
        'Prédictions ML': 'Prédictions ML',
        'Résultats & Historique': 'Résultats & Historique',
        
        // Auth
        'Se connecter': 'Se connecter',
        'S\'inscrire': 'S\'inscrire',
        'Déconnexion': 'Déconnexion',
        'Bienvenue': 'Bienvenue',
        
        // Settings
        'Univers par défaut': 'Univers par défaut',
        'Niveau de confiance minimum': 'Niveau de confiance minimum',
        'Thème de l\'interface': 'Thème de l\'interface',
        'Langue de l\'interface': 'Langue de l\'interface',
        'Sauvegarder': 'Sauvegarder',
        'Réinitialiser': 'Réinitialiser',
        'Exporter': 'Exporter',
        'Paramètres sauvegardés avec succès !': 'Paramètres sauvegardés avec succès !',
        
        // Common
        'Chargement...': 'Chargement...',
        'Erreur': 'Erreur',
        'Succès': 'Succès',
        'Analyses Effectuées': 'Analyses Effectuées',
        'Taux de Précision': 'Taux de Précision',
        'Prédictions Actives': 'Prédictions Actives',
        'Gains Potentiels': 'Gains Potentiels',
        'Activité Récente': 'Activité Récente'
    },
    
    en: {
        // Navigation
        'Accueil': 'Home',
        'Dashboard': 'Dashboard',
        'Tableau de Bord': 'Dashboard',
        'Méthode KATOOLING': 'KATOOLING Method',
        'Événements': 'Events',
        'Actualités': 'News',
        'Support': 'Support',
        'Contact': 'Contact',
        'Abonnement': 'Subscription',
        'Paramètres': 'Settings',
        'Katula Multi-Univers': 'Katula Multi-Universe',
        'Recherche & Données': 'Research & Data',
        'Analyse Temporelle': 'Temporal Analysis',
        'Patterns & Résultats': 'Patterns & Results',
        'Prédictions ML': 'ML Predictions',
        'Résultats & Historique': 'Results & History',
        
        // Auth
        'Se connecter': 'Login',
        'S\'inscrire': 'Sign Up',
        'Déconnexion': 'Logout',
        'Bienvenue': 'Welcome',
        
        // Settings
        'Univers par défaut': 'Default Universe',
        'Niveau de confiance minimum': 'Minimum Confidence Level',
        'Thème de l\'interface': 'Interface Theme',
        'Langue de l\'interface': 'Interface Language',
        'Sauvegarder': 'Save',
        'Réinitialiser': 'Reset',
        'Exporter': 'Export',
        'Paramètres sauvegardés avec succès !': 'Settings saved successfully!',
        
        // Common
        'Chargement...': 'Loading...',
        'Erreur': 'Error',
        'Succès': 'Success',
        
        // Login page
        'Se connecter': 'Login',
        'Email': 'Email',
        'Mot de passe': 'Password',
        'Se rappeler de moi': 'Remember me',
        'Suivant': 'Next',
        'Vous n\'avez pas de compte ?': 'Don\'t have an account?',
        'S\'inscrire maintenant': 'Sign up now',
        'Révolutionnez Votre Jeu': 'Revolutionize Your Game',
        'avec': 'with',
        'Méthode Révolutionnaire': 'Revolutionary Method',
        'Prédictions Précises': 'Precise Predictions',
        'Résultats Prouvés': 'Proven Results',
        'Découvrir KATOOLING': 'Discover KATOOLING',
        'Commencer Maintenant': 'Start Now',
        'Table Katula': 'Katula Table',
        'Géométrie des combinaisons': 'Combination geometry',
        'IA Prédictive': 'Predictive AI',
        'Algorithmes avancés': 'Advanced algorithms',
        'Multi-Univers': 'Multi-Universe',
        '5 univers d\'analyse': '5 analysis universes',
        'Temps Réel': 'Real Time',
        'Analyse continue': 'Continuous analysis',
        'Analyses Effectuées': 'Analyses Performed',
        'Taux de Précision': 'Precision Rate',
        'Prédictions Actives': 'Active Predictions',
        'Gains Potentiels': 'Potential Gains',
        'Activité Récente': 'Recent Activity'
    },
    
    es: {
        // Navigation
        'Accueil': 'Inicio',
        'Dashboard': 'Panel',
        'Tableau de Bord': 'Panel de Control',
        'Méthode KATOOLING': 'Método KATOOLING',
        'Événements': 'Eventos',
        'Actualités': 'Noticias',
        'Support': 'Soporte',
        'Contact': 'Contacto',
        'Abonnement': 'Suscripción',
        'Paramètres': 'Configuración',
        'Katula Multi-Univers': 'Katula Multi-Universo',
        'Recherche & Données': 'Investigación y Datos',
        'Analyse Temporelle': 'Análisis Temporal',
        'Patterns & Résultats': 'Patrones y Resultados',
        'Prédictions ML': 'Predicciones ML',
        'Résultats & Historique': 'Resultados e Historial',
        
        // Auth
        'Se connecter': 'Iniciar Sesión',
        'S\'inscrire': 'Registrarse',
        'Déconnexion': 'Cerrar Sesión',
        'Bienvenue': 'Bienvenido',
        
        // Settings
        'Univers par défaut': 'Universo Predeterminado',
        'Niveau de confiance minimum': 'Nivel Mínimo de Confianza',
        'Thème de l\'interface': 'Tema de Interfaz',
        'Langue de l\'interface': 'Idioma de Interfaz',
        'Sauvegarder': 'Guardar',
        'Réinitialiser': 'Restablecer',
        'Exporter': 'Exportar',
        'Paramètres sauvegardés avec succès !': '¡Configuración guardada con éxito!',
        
        // Common
        'Chargement...': 'Cargando...',
        'Erreur': 'Error',
        'Succès': 'Éxito',
        
        // Login page
        'Se connecter': 'Iniciar Sesión',
        'Email': 'Correo',
        'Mot de passe': 'Contraseña',
        'Se rappeler de moi': 'Recordarme',
        'Suivant': 'Siguiente',
        'Vous n\'avez pas de compte ?': '¿No tienes cuenta?',
        'S\'inscrire maintenant': 'Registrarse ahora',
        'Révolutionnez Votre Jeu': 'Revoluciona Tu Juego',
        'avec': 'con',
        'Méthode Révolutionnaire': 'Método Revolucionario',
        'Prédictions Précises': 'Predicciones Precisas',
        'Résultats Prouvés': 'Resultados Probados',
        'Découvrir KATOOLING': 'Descubrir KATOOLING',
        'Commencer Maintenant': 'Comenzar Ahora',
        'Table Katula': 'Tabla Katula',
        'Géométrie des combinaisons': 'Geometría de combinaciones',
        'IA Prédictive': 'IA Predictiva',
        'Algorithmes avancés': 'Algoritmos avanzados',
        'Multi-Univers': 'Multi-Universo',
        '5 univers d\'analyse': '5 universos de análisis',
        'Temps Réel': 'Tiempo Real',
        'Analyse continue': 'Análisis continuo',
        'Analyses Effectuées': 'Análisis Realizados',
        'Taux de Précision': 'Tasa de Precisión',
        'Prédictions Actives': 'Predicciones Activas',
        'Gains Potentiels': 'Ganancias Potenciales',
        'Activité Récente': 'Actividad Reciente'
    }
};

class I18n {
    constructor() {
        this.currentLanguage = this.getStoredLanguage() || 'fr';
        this.applyLanguage();
    }
    
    getStoredLanguage() {
        const settings = JSON.parse(localStorage.getItem('eazzylotto_settings') || '{}');
        return settings.language || 'fr';
    }
    
    translate(key) {
        return translations[this.currentLanguage]?.[key] || key;
    }
    
    setLanguage(lang) {
        if (translations[lang]) {
            this.currentLanguage = lang;
            this.applyLanguage();
        }
    }
    
    applyLanguage() {
        document.documentElement.lang = this.currentLanguage;
        
        // Traduire UNIQUEMENT les éléments avec data-i18n
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            element.textContent = this.translate(key);
        });
        
        // Traduire les placeholders
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            element.placeholder = this.translate(key);
        });
        
        // Traduire les titres
        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            element.title = this.translate(key);
        });
        
        // NE PAS traduire automatiquement les liens ou autres éléments
        // pour éviter les conflits de navigation
    }
}

// Instance globale
if (typeof window !== 'undefined') {
    window.i18n = new I18n();
    
    // Appliquer la langue au chargement complet
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(() => {
            if (window.i18n) {
                window.i18n.applyLanguage();
            }
        }, 1000);
    });
}

// Écouter les changements de paramètres
window.addEventListener('settingsChanged', function(event) {
    const settings = event.detail;
    if (settings.language && settings.language !== window.i18n.currentLanguage) {
        window.i18n.setLanguage(settings.language);
    }
});

window.addEventListener('settingsApplied', function(event) {
    const settings = event.detail;
    if (settings.language && settings.language !== window.i18n.currentLanguage) {
        window.i18n.setLanguage(settings.language);
    }
});

// Désactiver l'observer automatique qui cause les problèmes
// const observer = new MutationObserver...